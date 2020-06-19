# ----------------------------------------------------------------------------
# Inline Libs
# RedBlack tree implementation
# Found in https://github.com/ideasman42/isect_segments-bentley_ottmann/blob/e7c76149aba7167f4166287baf1a41a38499f632/poly_point_isect.py#L1136/
# -------
# ABCTree

from operator import attrgetter
_sentinel = object()


class _ABCTree(object):
    def __init__(self, items=None, cmp=None, cmp_data=None):
        """T.__init__(...) initializes T; see T.__class__.__doc__ for signature"""
        self._root = None
        self._count = 0
        if cmp is None:
            def cmp(cmp_data, a, b):
                if a < b:
                    return -1
                elif a > b:
                    return 1
                else:
                    return 0
        self._cmp = cmp
        self._cmp_data = cmp_data
        if items is not None:
            self.update(items)

    def clear(self):
        """T.clear() -> None.  Remove all items from T."""
        def _clear(node):
            if node is not None:
                _clear(node.left)
                _clear(node.right)
                node.free()
        _clear(self._root)
        self._count = 0
        self._root = None

    @property
    def count(self):
        """Get items count."""
        return self._count

    def get_value(self, key):
        node = self._root
        while node is not None:
            cmp = self._cmp(self._cmp_data, key, node.key)
            if cmp == 0:
                return node.value
            elif cmp < 0:
                node = node.left
            else:
                node = node.right
        raise KeyError(str(key))

    def pop_item(self):
        """T.pop_item() -> (k, v), remove and return some (key, value) pair as a
        2-tuple; but raise KeyError if T is empty.
        """
        if self.is_empty():
            raise KeyError("pop_item(): tree is empty")
        node = self._root
        while True:
            if node.left is not None:
                node = node.left
            elif node.right is not None:
                node = node.right
            else:
                break
        key = node.key
        value = node.value
        self.remove(key)
        return key, value
    popitem = pop_item  # for compatibility  to dict()

    def min_item(self):
        """Get item with min key of tree, raises ValueError if tree is empty."""
        if self.is_empty():
            raise ValueError("Tree is empty")
        node = self._root
        while node.left is not None:
            node = node.left
        return node.key, node.value

    def max_item(self):
        """Get item with max key of tree, raises ValueError if tree is empty."""
        if self.is_empty():
            raise ValueError("Tree is empty")
        node = self._root
        while node.right is not None:
            node = node.right
        return node.key, node.value

    def succ_item(self, key, default=_sentinel):
        """Get successor (k,v) pair of key, raises KeyError if key is max key
        or key does not exist. optimized for pypy.
        """
        # removed graingets version, because it was little slower on CPython and much slower on pypy
        # this version runs about 4x faster with pypy than the Cython version
        # Note: Code sharing of succ_item() and ceiling_item() is possible, but has always a speed penalty.
        node = self._root
        succ_node = None
        while node is not None:
            cmp = self._cmp(self._cmp_data, key, node.key)
            if cmp == 0:
                break
            elif cmp < 0:
                if (succ_node is None) or self._cmp(self._cmp_data, node.key, succ_node.key) < 0:
                    succ_node = node
                node = node.left
            else:
                node = node.right

        if node is None:  # stay at dead end
            if default is _sentinel:
                raise KeyError(str(key))
            return default
        # found node of key
        if node.right is not None:
            # find smallest node of right subtree
            node = node.right
            while node.left is not None:
                node = node.left
            if succ_node is None:
                succ_node = node
            elif self._cmp(self._cmp_data, node.key, succ_node.key) < 0:
                succ_node = node
        elif succ_node is None:  # given key is biggest in tree
            if default is _sentinel:
                raise KeyError(str(key))
            return default
        return succ_node.key, succ_node.value

    def prev_item(self, key, default=_sentinel):
        """Get predecessor (k,v) pair of key, raises KeyError if key is min key
        or key does not exist. optimized for pypy.
        """
        # removed graingets version, because it was little slower on CPython and much slower on pypy
        # this version runs about 4x faster with pypy than the Cython version
        # Note: Code sharing of prev_item() and floor_item() is possible, but has always a speed penalty.
        node = self._root
        prev_node = None

        while node is not None:
            cmp = self._cmp(self._cmp_data, key, node.key)
            if cmp == 0:
                break
            elif cmp < 0:
                node = node.left
            else:
                if (prev_node is None) or self._cmp(self._cmp_data, prev_node.key, node.key) < 0:
                    prev_node = node
                node = node.right

        if node is None:  # stay at dead end (None)
            if default is _sentinel:
                raise KeyError(str(key))
            return default
        # found node of key
        if node.left is not None:
            # find biggest node of left subtree
            node = node.left
            while node.right is not None:
                node = node.right
            if prev_node is None:
                prev_node = node
            elif self._cmp(self._cmp_data, prev_node.key, node.key) < 0:
                prev_node = node
        elif prev_node is None:  # given key is smallest in tree
            if default is _sentinel:
                raise KeyError(str(key))
            return default
        return prev_node.key, prev_node.value

    def __repr__(self):
        """T.__repr__(...) <==> repr(x)"""
        tpl = "%s({%s})" % (self.__class__.__name__, '%s')
        return tpl % ", ".join(("%r: %r" % item for item in self.items()))

    def __contains__(self, key):
        """k in T -> True if T has a key k, else False"""
        try:
            self.get_value(key)
            return True
        except KeyError:
            return False

    def __len__(self):
        """T.__len__() <==> len(x)"""
        return self.count

    def is_empty(self):
        """T.is_empty() -> False if T contains any items else True"""
        return self.count == 0

    def set_default(self, key, default=None):
        """T.set_default(k[,d]) -> T.get(k,d), also set T[k]=d if k not in T"""
        try:
            return self.get_value(key)
        except KeyError:
            self.insert(key, default)
            return default
    setdefault = set_default  # for compatibility to dict()

    def get(self, key, default=None):
        """T.get(k[,d]) -> T[k] if k in T, else d.  d defaults to None."""
        try:
            return self.get_value(key)
        except KeyError:
            return default

    def pop(self, key, *args):
        """T.pop(k[,d]) -> v, remove specified key and return the corresponding value.
        If key is not found, d is returned if given, otherwise KeyError is raised
        """
        if len(args) > 1:
            raise TypeError("pop expected at most 2 arguments, got %d" % (1 + len(args)))
        try:
            value = self.get_value(key)
            self.remove(key)
            return value
        except KeyError:
            if len(args) == 0:
                raise
            else:
                return args[0]

    def prev_key(self, key, default=_sentinel):
        """Get predecessor to key, raises KeyError if key is min key
        or key does not exist.
        """
        item = self.prev_item(key, default)
        return default if item is default else item[0]

    def succ_key(self, key, default=_sentinel):
        """Get successor to key, raises KeyError if key is max key
        or key does not exist.
        """
        item = self.succ_item(key, default)
        return default if item is default else item[0]

    def pop_min(self):
        """T.pop_min() -> (k, v), remove item with minimum key, raise ValueError
        if T is empty.
        """
        item = self.min_item()
        self.remove(item[0])
        return item

    def pop_max(self):
        """T.pop_max() -> (k, v), remove item with maximum key, raise ValueError
        if T is empty.
        """
        item = self.max_item()
        self.remove(item[0])
        return item

    def min_key(self):
        """Get min key of tree, raises ValueError if tree is empty. """
        return self.min_item()[0]

    def max_key(self):
        """Get max key of tree, raises ValueError if tree is empty. """
        return self.max_item()[0]

    def key_slice(self, start_key, end_key, reverse=False):
        """T.key_slice(start_key, end_key) -> key iterator:
        start_key <= key < end_key.
        Yields keys in ascending order if reverse is False else in descending order.
        """
        return (k for k, v in self.iter_items(start_key, end_key, reverse=reverse))

    def iter_items(self,  start_key=None, end_key=None, reverse=False):
        """Iterates over the (key, value) items of the associated tree,
        in ascending order if reverse is True, iterate in descending order,
        reverse defaults to False"""
        # optimized iterator (reduced method calls) - faster on CPython but slower on pypy

        if self.is_empty():
            return []
        if reverse:
            return self._iter_items_backward(start_key, end_key)
        else:
            return self._iter_items_forward(start_key, end_key)

    def _iter_items_forward(self, start_key=None, end_key=None):
        for item in self._iter_items(left=attrgetter("left"), right=attrgetter("right"),
                                     start_key=start_key, end_key=end_key):
            yield item

    def _iter_items_backward(self, start_key=None, end_key=None):
        for item in self._iter_items(left=attrgetter("right"), right=attrgetter("left"),
                                     start_key=start_key, end_key=end_key):
            yield item

    def _iter_items(self, left=attrgetter("left"), right=attrgetter("right"), start_key=None, end_key=None):
        node = self._root
        stack = []
        go_left = True
        in_range = self._get_in_range_func(start_key, end_key)

        while True:
            if left(node) is not None and go_left:
                stack.append(node)
                node = left(node)
            else:
                if in_range(node.key):
                    yield node.key, node.value
                if right(node) is not None:
                    node = right(node)
                    go_left = True
                else:
                    if not len(stack):
                        return  # all done
                    node = stack.pop()
                    go_left = False

    def _get_in_range_func(self, start_key, end_key):
        if start_key is None and end_key is None:
            return lambda x: True
        else:
            if start_key is None:
                start_key = self.min_key()
            if end_key is None:
                return (lambda x: self._cmp(self._cmp_data, start_key, x) <= 0)
            else:
                return (lambda x: self._cmp(self._cmp_data, start_key, x) <= 0 and
                        self._cmp(self._cmp_data, x, end_key) < 0)

    def print_tree_rec(self, node, spaces):
        if node is None: return
        self.print_tree_rec(node.right, spaces + ' ')
        print(spaces , node.key)
        self.print_tree_rec(node.left, spaces + ' ')

    def print_tree(self):
        self.print_tree_rec(self._root, '')

    def in_order_rec(self, node):
        if node is None: return
        self.in_order_rec(node.left)
        print(node.key)
        self.in_order_rec(node.right)

    def in_order(self):
        self.in_order_rec(self._root)
        
        
        

# ------
# RBTree

class Node(object):
    """Internal object, represents a tree node."""
    __slots__ = ['key', 'value', 'red', 'left', 'right']

    def __init__(self, key=None, value=None):
        self.key = key
        self.value = value
        self.red = True
        self.left = None
        self.right = None

    def free(self):
        self.left = None
        self.right = None
        self.key = None
        self.value = None

    def __getitem__(self, key):
        """N.__getitem__(key) <==> x[key], where key is 0 (left) or 1 (right)."""
        return self.left if key == 0 else self.right

    def __setitem__(self, key, value):
        """N.__setitem__(key, value) <==> x[key]=value, where key is 0 (left) or 1 (right)."""
        if key == 0:
            self.left = value
        else:
            self.right = value


class RBTree(_ABCTree):
    """
    RBTree implements a balanced binary tree with a dict-like interface.
    see: http://en.wikipedia.org/wiki/Red_black_tree
    """
    @staticmethod
    def is_red(node):
        if (node is not None) and node.red:
            return True
        else:
            return False

    @staticmethod
    def jsw_single(root, direction):
        other_side = 1 - direction
        save = root[other_side]
        root[other_side] = save[direction]
        save[direction] = root
        root.red = True
        save.red = False
        return save

    @staticmethod
    def jsw_double(root, direction):
        other_side = 1 - direction
        root[other_side] = RBTree.jsw_single(root[other_side], other_side)
        return RBTree.jsw_single(root, direction)

    def _new_node(self, key, value):
        """Create a new tree node."""
        self._count += 1
        return Node(key, value)

    def insert(self, key, value):
        """T.insert(key, value) <==> T[key] = value, insert key, value into tree."""
        if self._root is None:  # Empty tree case
            self._root = self._new_node(key, value)
            self._root.red = False  # make root black
            return

        head = Node()  # False tree root
        grand_parent = None
        grand_grand_parent = head
        parent = None  # parent
        direction = 0
        last = 0

        # Set up helpers
        grand_grand_parent.right = self._root
        node = grand_grand_parent.right
        # Search down the tree
        while True:
            if node is None:  # Insert new node at the bottom
                node = self._new_node(key, value)
                parent[direction] = node
            elif RBTree.is_red(node.left) and RBTree.is_red(node.right):  # Color flip
                node.red = True
                node.left.red = False
                node.right.red = False

            # Fix red violation
            if RBTree.is_red(node) and RBTree.is_red(parent):
                direction2 = 1 if grand_grand_parent.right is grand_parent else 0
                if node is parent[last]:
                    grand_grand_parent[direction2] = RBTree.jsw_single(grand_parent, 1 - last)
                else:
                    grand_grand_parent[direction2] = RBTree.jsw_double(grand_parent, 1 - last)

            # Stop if found
            if self._cmp(self._cmp_data, key, node.key) == 0:
                node.value = value  # set new value for key
                break

            last = direction
            direction = 0 if (self._cmp(self._cmp_data, key, node.key) < 0) else 1
            # Update helpers
            if grand_parent is not None:
                grand_grand_parent = grand_parent
            grand_parent = parent
            parent = node
            node = node[direction]

        self._root = head.right  # Update root
        self._root.red = False  # make root black

    def remove(self, key):
        """T.remove(key) <==> del T[key], remove item <key> from tree."""
        if self._root is None:
            raise KeyError(str(key))
        head = Node()  # False tree root
        node = head
        node.right = self._root
        parent = None
        grand_parent = None
        found = None  # Found item
        direction = 1

        # Search and push a red down
        while node[direction] is not None:
            last = direction

            # Update helpers
            grand_parent = parent
            parent = node
            node = node[direction]
            direction = 1 if (self._cmp(self._cmp_data, key, node.key) > 0) else 0
            # Save found node
            if self._cmp(self._cmp_data, key, node.key) == 0:
                found = node

            # Push the red node down
            if not RBTree.is_red(node) and not RBTree.is_red(node[direction]):
                if RBTree.is_red(node[1 - direction]):
                    parent[last] = RBTree.jsw_single(node, direction)
                    parent = parent[last]
                elif not RBTree.is_red(node[1 - direction]):
                    sibling = parent[1 - last]
                    if sibling is not None:
                        if (not RBTree.is_red(sibling[1 - last])) and (not RBTree.is_red(sibling[last])):
                            # Color flip
                            parent.red = False
                            sibling.red = True
                            node.red = True
                        else:
                            direction2 = 1 if grand_parent.right is parent else 0
                            if RBTree.is_red(sibling[last]):
                                grand_parent[direction2] = RBTree.jsw_double(parent, last)
                            elif RBTree.is_red(sibling[1-last]):
                                grand_parent[direction2] = RBTree.jsw_single(parent, last)
                            # Ensure correct coloring
                            grand_parent[direction2].red = True
                            node.red = True
                            grand_parent[direction2].left.red = False
                            grand_parent[direction2].right.red = False

        # Replace and remove if found
        if found is not None:
            found.key = node.key
            found.value = node.value
            parent[int(parent.right is node)] = node[int(node.left is None)]
            node.free()
            self._count -= 1

        # Update root and make it black
        self._root = head.right
        if self._root is not None:
            self._root.red = False
        if not found:
            raise KeyError(str(key))
################################################################################

from geocomp.common import prim
from geocomp.common import segment
from geocomp.common.point import Point
from geocomp.common.prim import left, right
from geocomp.common import control
from geocomp import config

eps = 0.0001

def compare_point(data, p1, p2):
    if (abs(p1.x - p2.x) < eps):
        if abs(p1.y - p2.y) < eps: return 0
        else: return p1.y - p2.y
    return p1.x - p2.x

class Event:
    def __init__(self, point):
        self.point = point
        self.left = []
        self.right = []
        self.middle = RBTree()
        self.middle_print = RBTree()
        self.lines = 0

    def insert_left(self, seg):
        self.left.append(seg)
        self.lines += 1

    def insert_right(self, seg):
        self.right.append(seg)
        self.lines += 1

    def insert_middle(self, seg, value = True):
        seg2 = Segment2(seg.init, seg)
        self.middle.insert(seg2, value)
        self.lines += 1
        self.insert_middle_print(seg)

    def insert_middle_print(self, seg, value = True):
        seg2 = Segment2(seg.init, seg)
        self.middle_print.insert(seg2, value)
        self.lines += 1

    def print_lines(self):
        print(self.point)
        for s in self.left: print(s)
        for s in self.right: print(s)
        for node in self.middle_print.iter_items(reverse=True): print(node[0].seg)
        print()

    def __eq__(self, other):
        if self.point == other.point: return True
        else: return False

    def __lt__(self, other):
        if (self.point.x == other.point.x):
            if (self.point.y < other.point.y): return True
            else: return False
        if (self.point.x < other.point.x): return True
        else: return False

    def __gt__(self, other):
        if (self.point.x == other.point.x):
            if (self.point.y > other.point.y): return True
            else: return False
        if (self.point.x > other.point.x): return True
        else: return False

class EventQueue:
    def __init__(self, segs):
        for s in segs:
            if compare_point(None, s.init, s.to) >= 0:
                s.init, s.to = s.to, s.init
        
        self.queue = RBTree(cmp = compare_point)
        for s in segs:
            p1 = s.init
            p1.plot('green')
            p2 = s.to
            p2.plot('yellow')
            event_p1 = self.queue.get(p1)
            if (event_p1 is None):
                event_p1 = Event(p1)
                event_p1.insert_left(s)
                self.queue.insert(p1, event_p1)
            else:
                event_p1.insert_left(s)
            
            event_p2 = self.queue.get(p2)
            if (event_p2 is None):
                event_p2 = Event(p2)
                event_p2.insert_right(s)
                self.queue.insert(p2, event_p2)
            else:
                event_p2.insert_right(s)

    def insert(self, event):
        self.queue.insert(event.point, event)

            
    def pop_min(self):
        return self.queue.pop_min()[1]
    
    def is_empty(self):
        return self.queue.is_empty()

    def __contains__(self, key):
        return key in self.queue
    
    def get(self, key):
        return self.queue.get(key)

class Segment2:
    def __init__(self, point, seg):
        self.seg = seg
        self.point = point

    def __eq__(self, other):
        return self.seg == other.seg

    def __lt__(self, other):
        if (other.seg.has_left(self.point)): return True
        elif (other.seg.has_inside(self.point) and other.seg.has_left(self.seg.to)): return True
        return False

    def __gt__(self, other):
        if (right(other.seg.init, other.seg.to, self.point)): return True
        elif (other.seg.has_inside(self.point) and right(other.seg.init, other.seg.to, self.seg.to)): return True
        return False

    def __repr__ (self):
        return repr(self.point) + " " + repr(self.seg)
    

def vertical(s):
    return s.init.x == s.to.x

def horizontal(s):
    return s.init.y == s.to.y

def vertical(seg):
    return seg.init.x == seg.to.x

def intersection_point(s1, s2):
    x1, y1 = s1.init.x, s1.init.y
    x2, y2 = s1.to.x, s1.to.y
    x3, y3 = s2.init.x, s2.init.y
    x4, y4 = s2.to.x, s2.to.y
    if vertical(s1):
        x = s1.init.x
        m2 = (y4 - y3)/(x4 - x3)
        y = m2*(x - x3) + y3
        p = Point(x,y)
        return p
    if vertical(s2):
        x = s2.init.x
        m1 = (y2 - y1)/(x2 - x1)
        y = m1*(x - x1) + y1
        p = Point(x,y)
        return p
    m1 = (y2 - y1)/(x2 - x1)
    m2 = (y4 - y3)/(x4 - x3)
    x = (m1*x1 - m2*x3 - y1 + y3)/(m1-m2)
    y = m1*x + (-m1*x1 + y1)

    p = Point(x,y)
    return p

def verify_event(event, queue, s1, s2, side = None):
    q = intersection_point(s1, s2)
    new_event = Event(q)
    if (compare_point(None, q, event.point) > 0):
        if (q not in queue):
            q.plot('white')
            new_event.insert_middle(s1)
            new_event.insert_middle(s2)
            queue.insert(new_event)
        else:
            event2 = queue.get(q)
            if not event2.middle.is_empty():
                event2.insert_middle_print(s1)
                event2.insert_middle_print(s2)

    if (compare_point(None, q, event.point) == 0 and side == 'left'):
        event.point.plot('white')
        if (compare_point(None, s2.init, event.point) != 0):
            event.insert_middle_print(s2)
    
def treat_left(event, queue, sweep_line, seg):
    seg2 = Segment2(event.point, seg)
    sweep_line.insert(seg2, True)
    suc = sweep_line.succ_item(seg2, None)
    prev = sweep_line.prev_item(seg2, None)
    if (suc is not None):
        suc[0].seg.hilight('light blue', None)
        if (seg.intersects(suc[0].seg)):
            verify_event(event, queue, seg, suc[0].seg, 'left')
        control.sleep()
        suc[0].seg.unhilight()

    if (prev is not None):
        prev[0].seg.hilight('light blue', None)
        if (seg.intersects(prev[0].seg)):
            verify_event(event, queue, seg, prev[0].seg, 'left')
        control.sleep()
        prev[0].seg.unhilight()

def treat_right(event, queue, sweep_line, seg):
    seg2 = Segment2(seg.to, seg)
    suc = sweep_line.succ_item(seg2, None)
    prev = sweep_line.prev_item(seg2, None)
    sweep_line.remove(seg2)
    if (prev is not None) and (suc is not None):
        suc[0].seg.hilight('light blue', None)
        prev[0].seg.hilight('light blue', None)
        if prev[0].seg.intersects(suc[0].seg):
            verify_event(event, queue, suc[0].seg, prev[0].seg)
        control.sleep()
        suc[0].seg.unhilight()
        prev[0].seg.unhilight()

def swap_points(s):
    s.init, s.to = s.to, s.init

def treat_middle(event, queue, sweep_line):
    p = event.point
    middle = event.middle
    MIN = middle.min_item()[0].seg
    MAX = middle.max_item()[0].seg
    swap_points(MIN)
    swap_points(MAX)
    seg_min = Segment2(p, MIN)
    seg_max = Segment2(p, MAX)
    prev = sweep_line.prev_item(seg_min, None)
    suc = sweep_line.succ_item(seg_max, None)
    swap_points(MIN)
    swap_points(MAX)
    for s in middle.iter_items():
        seg = s[0].seg
        swap_points(seg)
        seg2 = Segment2(p, seg)
        sweep_line.remove(seg2)
        swap_points(seg)
    for s in middle.iter_items():
        seg = s[0].seg
        seg2 = Segment2(p, seg)
        sweep_line.insert(seg2, True)
    if (suc is not None):
        suc[0].seg.hilight('light blue', None)
        MIN.hilight('light blue', None)
        if (MIN.intersects(suc[0].seg)):
            verify_event(event, queue, MIN, suc[0].seg)
        control.sleep()
        MIN.unhilight()
        suc[0].seg.unhilight()

    if (prev is not None):
        prev[0].seg.hilight('light blue', None)
        MAX.hilight('light blue', None)
        if (MAX.intersects(prev[0].seg)):
            verify_event(event, queue, MAX, prev[0].seg)
        control.sleep()
        MAX.unhilight()
        prev[0].seg.unhilight()


def treat_event(event, queue, sweep_line):
    v = control.plot_vert_line(event.point.x, 'blue', 2)
    p = event.point.hilight('cyan')
    
    for s in event.right: 
        s.hilight('yellow', None)
        control.sleep()
        treat_right(event, queue, sweep_line, s)
        s.unhilight()
    for s in event.left:
        s.hilight('yellow', None) 
        control.sleep()
        treat_left(event, queue, sweep_line, s)
        s.unhilight()
    if (not event.middle.is_empty()): treat_middle(event, queue, sweep_line)
    if (event.lines > 1):
        event.print_lines()
    control.sleep()
    control.plot_delete(v)
    event.point.unhilight(p)


def Bentley_Ottman(segments):
    queue = EventQueue(segments)
    sweep_line = RBTree()
    print("Intersection points folled by intersecting segments:")
    while (not queue.is_empty()):
        event = queue.pop_min()
        treat_event(event, queue, sweep_line)



        