from collections import MutableMapping


class SortedDict(MutableMapping):
    """Dictionary with items sorted by key.

    `SortedDict` inner structure is AVL Tree based, which guaranties
    log(N) time insertion, updating and deletion, although implementation
    is recursive, which places some size restrictions in terms of memory usage.

    Takes instances of `collections.abc.Mapping` (including `SortedDict`)
    and iterable sets of (key, value) pairs as constructor argument.

    Has no public methods or attributes.
    """

    # key sentinel (to keep `None` available as a key)
    _sentinel = object()

    def __init__(self, *constructor_arg):
        """Args:
            `constructor_arg`: is optional, but if present, must be instance
            of `collections.abc.Mapping` or iterable set of (key, value) pairs
        """
        self._k = self._sentinel
        self._val = self._l = self._r = None
        self._h = self._n = 0
        if constructor_arg:
            self.update(*constructor_arg)

    def __len__(self):
        return self._n

    def __setitem__(self, k, val):
        if not self:
            self._k, self._val = k, val
            self._l, self._r = SortedDict(), SortedDict()
        elif k > self._k:
            self._r.__setitem__(k, val)
        elif k < self._k:
            self._l.__setitem__(k, val)
        else:
            self._val = val
        self._rebalance()

    def __getitem__(self, k):
        if not self:
            raise KeyError
        if self._k == k:
            return self._val
        if k > self._k:
            return self._r.__getitem__(k)
        return self._l.__getitem__(k)

    def __delitem__(self, k):
        if not self:
            raise KeyError
        if k == self._k:
            only = self._l if not self._r else self._r if not self._l else None
            if only is not None:
                self.__dict__.update(only.__dict__)
            else:
                next_ = self._r
                while next_._l:
                    next_ = next_._l
                self._k, self._val = next_._k, next_._val
                self._r.__delitem__(next_._k)
            self._rebalance()
            return
        (self._l if k < self._k else self._r).__delitem__(k)
        self._rebalance()

    def __iter__(self):
        if self:
            yield from iter(self._l)
            yield self._k
            yield from iter(self._r)

    # AVL Tree node balance factor property
    @property
    def _balance(self):
        return (self._l._h - self._r._h) if self._l else 0

    def _update(self, full=True):
        """AVL Tree method for height and size evaluation.

        Evaluation is recursive by default. To update only measures of `self`,
        `False` must be passed as `full`.
        Args:
            full (bool): recurse / `self` only
        """
        if self._k == self._sentinel:
            self._h = self._n = 0
            return
        if full:
            if self._l is not None:
                self._l._update()
            if self._r is not None:
                self._r._update()
        self._h = max(self._l._h, self._r._h) + 1
        self._n = self._l._n + self._r._n + 1

    def _rebalance(self):
        """AVL Tree method for balance maintenance."""
        self._update(full=False)
        while abs(self._balance) > 1:
            if self._balance > 1:
                if self._l._balance < 0:
                    self._l._rotate()
                self._rotate(left=False)
            if self._balance < -1:
                if self._r._balance > 0:
                    self._r._rotate(left=False)
                self._rotate()

    def _rotate(self, left=True):
        """AVL Tree auxiliary method for `_rebalance`."""
        s_k, s_val = self._k, self._val
        l_k, l_val = self._l._k, self._l._val
        r_k, r_val = self._r._k, self._r._val
        ll, lr, rl, rr = self._l._l, self._l._r, self._r._l, self._r._r
        t = SortedDict()
        if left:
            t._k, t._val, t._l, t._r = l_k, l_val, ll, lr
            self._l._l, self._l._r, self._r = t, rl, rr
            self._l._k, self._l._val = s_k, s_val
            self._k, self._val = r_k, r_val
        else:
            t._k, t._val, t._l, t._r = r_k, r_val, rl, rr
            self._r._r, self._r._l, self._l = t, lr, ll
            self._r._k, self._r._val = s_k, s_val
            self._k, self._val = l_k, l_val
        self._update()
