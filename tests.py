# Licensed under the Apache License, Version 2.0 (the "License");

import btree_mini

import unittest


# -----------------------------------------------------------------------------
# BTreeMap

class TestMapBasics(unittest.TestCase):

    def test_create_dict(self):
        data = {i: -i for i in range(10)}
        r = btree_mini.BTreeMap(data)
        self.assertEqual(list(data.items()), list(r.items()))
        self.assertEqual(10, len(r))

    def test_create_list(self):
        data = [(i, -i) for i in range(10)]
        r = btree_mini.BTreeMap(data)
        self.assertEqual(data, list(r.items()))

    def test_clear(self):
        r = btree_mini.BTreeMap({i: -i for i in range(10)})
        r.clear()
        self.assertEqual(0, len(list(r.keys())))
        self.assertEqual(0, len(r))

    def test_copy(self):
        r = btree_mini.BTreeMap({i: -i for i in range(10)})
        r_copy = r.copy()
        for a, b in zip(r.items(), r_copy.items()):
            self.assertEqual(a, b)
        self.assertEqual(10, len(r))
        self.assertEqual(10, len(r_copy))

    def test_discard(self):
        seed = 10
        total = 512

        items = list(range(0, total))

        items_single = items
        items = items * 10
        import random
        rng = random.Random(seed)
        rng.shuffle(items)

        for pass_nr in 0, 1:
            if pass_nr == 1:
                data = [(i, i) for i in items_single]
            else:
                data = []

            r = btree_mini.BTreeMap(data)
            d = dict(data)

            while items:
                value = items.pop()
                if rng.random() < 0.5:
                    r[value] = value
                    d[value] = value
                else:
                    r.discard(value)
                    d.pop(value, None)

            self.assertEqual(r.is_valid(), True)
            self.assertEqual(list(sorted(d.items())), list(r.items()))


class TestMapInsertRemove_Helper:

    def assertDict(self, d, *, seed):
        r = btree_mini.BTreeMap()
        d_items = list(d.items())
        d_items.sort()

        for pass_nr in range(2):
            if pass_nr == 0:
                pass
            elif pass_nr == 1:
                d_items.reverse()
            elif pass_nr == 2:
                rng = random.Random(seed)
                rng.shuffle(d_items)

            for k, v in d_items:
                self.assertEqual(k in r, False)
                r[k] = v
                self.assertEqual(k in r, True)

            self.assertEqual(r.is_valid(), True)

            for k, v in d_items:
                self.assertEqual(r[k], v)

            self.assertEqual(len(d), len(list(r.keys())))

            # remove half the items
            d_items_split = len(d_items) // 2
            d_items_a = d_items[d_items_split:]
            d_items_b = d_items[:d_items_split]

            for k, v in d_items_a:
                self.assertEqual(r.pop_key(k), v)

            for k, v in d_items_a:
                self.assertEqual(k in r, False)
            for k, v in d_items_b:
                self.assertEqual(r[k], d[k])

            self.assertEqual(r.is_valid(), True)
            self.assertEqual(d_items_split, len(r))

            for k, v in reversed(d_items_a):
                r[k] = v

            for k, v in reversed(d_items_b):
                self.assertEqual(r.pop_key(k), v)

            for k, v in d_items_a:
                self.assertEqual(r[k], v)

            self.assertEqual(r.is_valid(), True)

            for k, v in d_items_a:
                r.remove(k)

            self.assertEqual(0, len(list(r.keys())))
            self.assertEqual(0, len(r))

    def assertSet(self, s, *, seed):
        self.assertDict({k: repr(k) for k in s}, seed=seed)


class TestMapInsertRemove(unittest.TestCase, TestMapInsertRemove_Helper):

    def test_empty(self):
        self.assertSet(set(), seed=0)

    def test_single(self):
        self.assertSet(set(range(1)), seed=1)

    def test_10(self):
        self.assertSet(set(range(10)), seed=10)

    def test_100(self):
        self.assertSet(set(range(100)), seed=100)


class TestMapPopMinMax_Helper:

    def assertDict(self, d, *, seed):
        r = btree_mini.BTreeMap()
        d_items = list(d.items())
        d_items.sort()

        for k, v in d_items:
            r[k] = v

        for k, v in d_items:
            self.assertEqual((k, v), r.pop_min_item())

        for k, v in d_items:
            r[k] = v

        d_items.reverse()
        for k, v in d_items:
            self.assertEqual((k, v), r.pop_max_item())

        self.assertEqual(0, len(list(r.keys())))

    def assertSet(self, s, *, seed):
        self.assertDict({k: repr(k) for k in s}, seed=seed)


class TestMapPopMinMax(unittest.TestCase, TestMapPopMinMax_Helper):

    def test_empty(self):
        self.assertSet(set(), seed=0)

    def test_single(self):
        self.assertSet(set(range(1)), seed=1)

    def test_10(self):
        self.assertSet(set(range(10)), seed=1)

    def test_100(self):
        self.assertSet(set(range(100)), seed=1)


# -----------------------------------------------------------------------------
# BTreeSet
#
# Note, this uses exactly the same logic as BTreeMap
# so these tests are more for the BTreeSet API.

class TestSetBasics(unittest.TestCase):

    def test_create_set(self):
        data = {i for i in range(10)}
        r = btree_mini.BTreeSet(data)
        self.assertEqual(list(data), list(r))

    def test_create_list(self):
        data = [(i, -i) for i in range(10)]
        r = btree_mini.BTreeSet(data)
        self.assertEqual(data, list(r))

    def test_clear(self):
        r = btree_mini.BTreeSet({i for i in range(10)})
        r.clear()
        self.assertEqual(0, len(list(r)))

    def test_reversed(self):
        r = btree_mini.BTreeSet({i for i in range(10)})
        for a, b in zip(reversed(r), reversed(range(10))):
            self.assertEqual(a, b)

    def test_copy(self):
        r = btree_mini.BTreeSet({i for i in range(10)})
        r_copy = r.copy()
        for a, b in zip(r, r_copy):
            self.assertEqual(a, b)


if __name__ == "__main__":
    unittest.main()
