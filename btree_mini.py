# Apache License, Version 2.0
# Copyright Campbell Barton, 2016

# Left Leaning red-black tree, see:
# https://en.wikipedia.org/wiki/Left-leaning_red%E2%80%93black_tree
#
# Loosely based on:
# https://github.com/sebastiencs/red-black-tree/blob/master/rbtree.c
# with various additions.
#
# B-Tree logic is provided by functional interface,
# exposed as object oriented ``map`` and ``set`` types.

__all__ = (
    "BTreeMap",
    "BTreeSet",
)

# -----------------------------------------------------------------------------
# Functional B-Tree Implementation

sentinel = object()

BLACK = True
RED = False


def rb_free(node):
    del node.key
    del node.color
    del node.left
    del node.right
    # free(node);


def is_red(node):
    return (node is not None and node.color == RED)


def key_cmp(key1, key2):
    return 0 if (key1 == key2) else (-1 if (key1 < key2) else 1)


def rb_flip_color(node):
    node.color ^= True
    node.left.color ^= True
    node.right.color ^= True


def rb_rotate_left(left):
    """ Make a right-leaning 3-node lean to the left.
    """
    right = left.right
    left.right = right.left
    right.left = left
    right.color = left.color
    left.color = RED
    return right


def rb_rotate_right(right):
    """ Make a left-leaning 3-node lean to the right.
    """
    left = right.left
    right.left = left.right
    left.right = right
    left.color = right.color
    right.color = RED
    return left


def rb_fixup_insert(node):
    if is_red(node.right) and not is_red(node.left):
        node = rb_rotate_left(node)
    if is_red(node.left) and is_red(node.left.left):
        node = rb_rotate_right(node)

    if is_red(node.left) and is_red(node.right):
        rb_flip_color(node)

    return node


def rb_insert_recursive(node, key, cls):
    if node is None:
        node = cls()
        return node, node

    res = key_cmp(key, node.key)
    if res == 0:
        node_found = node
    elif res < 0:
        node.left, node_found = rb_insert_recursive(node.left, key, cls)
    else:
        node.right, node_found = rb_insert_recursive(node.right, key, cls)

    return rb_fixup_insert(node), node_found


def rb_insert_root(root_rbtree, key, cls):
    root_rbtree, node_found = rb_insert_recursive(root_rbtree, key, cls)
    root_rbtree.color = BLACK
    return root_rbtree, node_found


def rb_lookup(node, key):
    # get node from key
    while node is not None:
        cmp = key_cmp(key, node.key)
        if cmp == 0:
            return node
        if cmp < 0:
            node = node.left
        else:
            node = node.right
    return None


def rb_min(node):
    # -> Node
    if node is None:
        return None
    while node.left is not None:
        node = node.left
    return node


def rb_fixup_remove(node):
    # -> Node
    if is_red(node.right):
        node = rb_rotate_left(node)
    if is_red(node.left) and is_red(node.left.left):
        node = rb_rotate_right(node)
    if is_red(node.left) and is_red(node.right):
        rb_flip_color(node)
    return node


def rb_move_red_to_left(node):
    """ Assuming that h is red and both h.left and h.left.left
        are black, make h.left or one of its children red.
    """
    rb_flip_color(node)
    if node.right and is_red(node.right.left):
        node.right = rb_rotate_right(node.right)
        node = rb_rotate_left(node)
        rb_flip_color(node)
    return node


def rb_move_red_to_right(node):
    """ Assuming that h is red and both h.right and h.right.left
        are black, make h.right or one of its children red.
    """
    rb_flip_color(node)
    if node.left and is_red(node.left.left):
        node = rb_rotate_right(node)
        rb_flip_color(node)
    return node


def rb_pop_min_recursive(node):
    if node is None:
        return None, None
    if node.left is None:
        return None, node
    if (not is_red(node.left)) and (not is_red(node.left.left)):
        node = rb_move_red_to_left(node)
    node.left, node_pop = rb_pop_min_recursive(node.left)
    return rb_fixup_remove(node), node_pop


def rb_pop_max_recursive(node):
    if is_red(node.left):
        node = rb_rotate_right(node)
    if node.right is None:
        return None, node
    if (not is_red(node.right)) and (not is_red(node.right.left)):
        node = rb_move_red_to_right(node)
    node.right, node_pop = rb_pop_max_recursive(node.right)
    return rb_fixup_remove(node), node_pop


def rb_pop_key_recursive(node, key):
    if node is None:
        return None, None

    node_pop = None
    if key_cmp(key, node.key) == -1:
        if node.left is not None:
            if (not is_red(node.left)) and (not is_red(node.left.left)):
                node = rb_move_red_to_left(node)
        node.left, node_pop = rb_pop_key_recursive(node.left, key)
    else:
        if is_red(node.left):
            node = rb_rotate_right(node)
        cmp = key_cmp(key, node.key)
        if cmp == 0 and (node.right is None):
            return None, node
        # assert(node.right is not None)

        # this part of the check is only needed to support
        # removal of key's which don't exist
        if node.right is not None:
            if (not is_red(node.right)) and (not is_red(node.right.left)):
                node = rb_move_red_to_right(node)
                cmp = key_cmp(key, node.key)

            if cmp == 0:
                # minor improvement over original method
                # no need to double lookup min
                node.right, node_pop = rb_pop_min_recursive(node.right)

                node_pop.left = node.left
                node_pop.right = node.right
                node_pop.color = node.color
                node_pop, node = node, node_pop
            else:
                node.right, node_pop = rb_pop_key_recursive(node.right, key)
    return rb_fixup_remove(node), node_pop


def rb_pop_key(root, key):
    root, node_pop = rb_pop_key_recursive(root, key)
    if root is not None:
        root.color = BLACK
    return root, node_pop


def rb_pop_min(node):
    node, node_pop = rb_pop_min_recursive(node)
    if node is not None:
        node.color = BLACK
    return node, node_pop


def rb_pop_max(node):
    node, node_pop = rb_pop_max_recursive(node)
    if node is not None:
        node.color = BLACK
    return node, node_pop


def rb_copy_recursive(node):
    if node is None:
        return None
    copy = node.copy()
    copy.color = node.color
    copy.left = rb_copy_recursive(copy.left)
    copy.right = rb_copy_recursive(copy.right)
    return copy


def rb_free_recursive(node):
    if node is not None:
        if node.left:
            rb_free_recursive(node.left)
        if node.right:
            rb_free_recursive(node.right)
        node.left = None
        node.right = None
        rb_free(node)


def rb_count_recursive(node):
    if node is not None:
        return (
            1 +
            rb_count_recursive(node.left) +
            rb_count_recursive(node.right))
    else:
        return 0


def rb_is_balanced_recursive(node, black):
    # Does every path from the root to a leaf
    # have the given number of black links?
    if node is None:
        return black == False
    if not is_red(node):
        black -= 1
    return (rb_is_balanced_recursive(node.left, black) and
            rb_is_balanced_recursive(node.right, black))


def rb_is_balanced(root):
    # Do all paths from root to leaf have same number of black edges?
    black = 0  # number of black links on path from root to min
    node = root
    while node is not None:
        if not is_red(node):
            black += 1
        node = node.left
    return rb_is_balanced_recursive(root, black)


def rb_is_ordered(root):
    n_prev = None
    for n in rb_iter_forward_recursive(root):
        if n_prev is not None:
            if n_prev.key > n.key:
                return False
        n_prev = n
    return True


def rb_is_balanced_and_ordered(root):
    return rb_is_balanced(root) and rb_is_ordered(root)


# -----------------------------------------------------------------------------
# Pythonic Helpers
#
# Not directly related to binary-tree logic.

def rb_iter_forward_recursive(node):
    if node is not None:
        yield from rb_iter_forward_recursive(node.left)
        yield node
        yield from rb_iter_forward_recursive(node.right)


def rb_iter_backward_recursive(node):
    if node is not None:
        yield from rb_iter_backward_recursive(node.right)
        yield node
        yield from rb_iter_backward_recursive(node.left)


def rb_iter_dir(root, reverse=False):
    if reverse:
        yield from rb_iter_backward_recursive(root)
    else:
        yield from rb_iter_forward_recursive(root)


# -----------------------------------------------------------------------------
# Pythonic Object Oriented Access
#
# - BTreeMap
# - BTreeSet

class BNodeMap:

    __slots__ = (
        "key",
        "value",
        "color",
        "left",
        "right",
    )

    def __init__(self):
        self.color = RED
        self.left = None
        self.right = None

    def copy(self):
        copy = BNodeMap()
        copy.key = self.key
        copy.value = self.value
        copy.color = self.color
        copy.left = self.left
        copy.right = self.right
        return copy


class BTreeMap:
    __slots__ = (
        "_root",
    )

    def __init__(self, data=None):
        self._root = None

        if data is None:
            pass
        elif isinstance(data, BTreeMap):
            self._root = rb_copy_recursive(data._root)
        elif hasattr(data, "items"):
            for k, v in data.items():
                self[k] = v
        else:
            # iterate over key-value pairs
            for k, v in data:
                self[k] = v

    def get(self, key, default=None):
        n = rb_lookup(self._root, key)
        if n is not None:
            return n.value
        else:
            return default

    def insert(self, key, value):
        self._root, node_found = rb_insert_root(self._root, key, BNodeMap)
        node_found.key = key
        node_found.value = value

    def remove(self, key):
        self._root, node_pop = rb_pop_key(self._root, key)
        if node_pop is None:
            raise KeyError("key not found")
        rb_free(node_pop)

    def discard(self, key):
        self._root, node_pop = rb_pop_key(self._root, key)
        if node_pop is not None:
            rb_free(node_pop)

    def pop_key(self, key, default=sentinel):
        self._root, node_pop = rb_pop_key(self._root, key)
        if node_pop is None:
            if default is sentinel:
                raise KeyError("key not found")
            return default
        value = node_pop.value
        rb_free(node_pop)
        return value

    def pop_min_item(self, default=sentinel):
        if self._root is None:
            if default is sentinel:
                raise KeyError("pop from empty tree")
            return default
        self._root, node_pop = rb_pop_min(self._root)
        item = (node_pop.key, node_pop.value)
        rb_free(node_pop)
        return item

    def pop_max_item(self, default=sentinel):
        if self._root is None:
            if default is sentinel:
                raise KeyError("pop from empty tree")
            return default
        self._root, node_pop = rb_pop_max(self._root)
        item = (node_pop.key, node_pop.value)
        rb_free(node_pop)
        return item

    def pop_min_value(self, default=sentinel):
        if self._root is None:
            if default is sentinel:
                raise KeyError("pop from empty tree")
            return default
        self._root, node_pop = rb_pop_min(self._root)
        value = node_pop.value
        rb_free(node_pop)
        return value

    def pop_max_value(self, default=sentinel):
        if self._root is None:
            if default is sentinel:
                raise KeyError("pop from empty tree")
            return default
        self._root, node_pop = rb_pop_max(self._root)
        value = node_pop.value
        rb_free(node_pop)
        return value

    def clear(self):
        rb_free_recursive(self._root)
        self._root = None

    def is_empty(self):
        self._root is None

    def copy(self):
        return BTreeMap(self)

    def __bool__(self):
        self._root is not None

    def __len__(self):
        # could track this
        return rb_count_recursive(self._root)

    def __contains__(self, key):
        return rb_lookup(self._root, key) is not None

    def __getitem__(self, key):
        node = rb_lookup(self._root, key)
        if node is None:
            raise KeyError(repr(key))
        return node.value

    def __setitem__(self, key, value):
        self.insert(key, value)

    def __delitem__(self, key):
        return self.remove(key)

    # ------------------------------------------------------------------------
    # Convenience Helpers

    def items(self, reverse=False):
        for n in rb_iter_dir(self._root, reverse):
            yield (n.key, n.value)

    def keys(self, reverse=False):
        for n in rb_iter_dir(self._root, reverse):
            yield n.key

    def values(self, reverse=False):
        for n in rb_iter_dir(self._root, reverse):
            yield n.value

    # ------------------------------------------------------------------------
    # Debugging Functions (use for testing)

    def is_valid(self):
        return rb_is_balanced_and_ordered(self._root)


class BNodeSet:

    __slots__ = (
        "key",
        "color",
        "left",
        "right",
    )

    def __init__(self):
        self.color = RED
        self.left = None
        self.right = None

    def copy(self):
        copy = BNodeSet()
        copy.key = self.key
        copy.color = self.color
        copy.left = self.left
        copy.right = self.right
        return copy


class BTreeSet:
    __slots__ = (
        "_root",
    )

    def __init__(self, data=None):
        self._root = None

        if data is None:
            pass
        elif isinstance(data, BTreeSet):
            self._root = rb_copy_recursive(data._root)
        else:
            for k in data:
                self.add(k)

    def add(self, key):
        self._root, node_found = rb_insert_root(self._root, key, BNodeSet)
        node_found.key = key

    def remove(self, key):
        self._root, node_pop = rb_pop_key(self._root, key)
        if node_pop is None:
            raise KeyError("key not found")
        rb_free(node_pop)

    def discard(self, key):
        self._root, node_pop = rb_pop_key(self._root, key)
        if node_pop is not None:
            rb_free(node_pop)

    def pop_min_key(self, default=sentinel):
        if self._root is None:
            if default is sentinel:
                raise KeyError("pop from empty tree")
            return default
        self._root, node_pop = rb_pop_min(self._root)
        key = node_pop.key
        rb_free(node_pop)
        return key

    def pop_max_key(self, default=sentinel):
        if self._root is None:
            if default is sentinel:
                raise KeyError("pop from empty tree")
            return default
        self._root, node_pop = rb_pop_max(self._root)
        key = node_pop.key
        rb_free(node_pop)
        return key

    def clear(self):
        rb_free_recursive(self._root)
        self._root = None

    def is_empty(self):
        self._root is None

    def copy(self):
        return BTreeSet(self)

    def __bool__(self):
        self._root is not None

    def __len__(self):
        # could track this
        return rb_count_recursive(self._root)

    def __iter__(self):
        for n in rb_iter_forward_recursive(self._root):
            yield n.key

    def __reversed__(self):
        for n in rb_iter_backward_recursive(self._root):
            yield n.key

    def __contains__(self, key):
        return rb_lookup(self._root, key) is not None

    def __delitem__(self, key):
        return self.remove(key)

    # ------------------------------------------------------------------------
    # Convenience Helpers

    # ------------------------------------------------------------------------
    # Debugging Functions (use for testing)

    def is_valid(self):
        return rb_is_balanced_and_ordered(self._root)
