# This file is part of dhlibs (https://github.com/DinhHuy2010/dhlibs)
#
# MIT License
#
# Copyright (c) 2024 DinhHuy2010 (https://github.com/DinhHuy2010)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


from functools import partial, reduce
from random import sample
from threading import RLock as Lock

from typing_extensions import Hashable, Optional

from dhlibs.cachedop._typings import AuditEvent, CacheInfo, KeyCallableType, OperatorCallableType
from dhlibs.cachedop._utils import determine_maxsize_args as _determine_maxsize_args
from dhlibs.cachedop._utils import keymaker
from dhlibs.cachedop.audit import Auditer
from dhlibs.cachedop.audit import audit as global_audit


class _cachemap:
    def __init__(
        self,
        keymaker: keymaker,
        maxsize: Optional[int],
        removal_limit: Optional[int],
        auditer: Auditer,
    ) -> None:
        self._keymaker = keymaker
        self._dcache: dict[Hashable, int] = {}
        maxsize, removal_limit = _determine_maxsize_args(maxsize, removal_limit)
        self._maxsize = maxsize
        self._removal_limit = removal_limit
        self._hits = 0
        self._misses = 0
        self._cleanup_count = 0
        self._thread_lock = Lock()
        self._auditer = auditer

    def cleancache(self) -> None:
        if self._maxsize is None or self._removal_limit is None or len(self._dcache) < self._maxsize:
            return
        with self._thread_lock:
            self._auditer.audit(AuditEvent.CLEAN, {"removal_limit": self._removal_limit})
            history = tuple(self._dcache.keys())
            for key in sample(history, self._removal_limit):
                self._auditer.audit(AuditEvent.REMOVE_KEY, {"key": key})
                try:
                    self._dcache.pop(key)
                except KeyError:
                    pass
                else:
                    self._cleanup_count += 1

    def getcache(self, args: tuple[int, ...]) -> Optional[int]:
        with self._thread_lock:
            key = self._keymaker.make_key(args)
            cached = self._dcache.get(key)
            if cached:
                self._auditer.audit(AuditEvent.HIT, {"key": key, "value": cached})
                self._hits += 1
        return cached

    def setcache(self, args: tuple[int, ...], value: int) -> int:
        self.cleancache()
        with self._thread_lock:
            key = self._keymaker.make_key(args)
            self._auditer.audit(AuditEvent.MISS, {"key": key, "value": value})
            self._misses += 1
            self._dcache[key] = value
        return value

    def cacheinfo(self) -> CacheInfo:
        return CacheInfo(len(self._dcache), self._hits, self._misses, self._cleanup_count)

    def clearcache(self) -> None:
        with self._thread_lock:
            self._dcache.clear()
            self._hits = 0
            self._misses = 0
            self._cleanup_count = 0


class _cached_opfunc_wrapper:
    def __init__(
        self,
        op: OperatorCallableType,
        key: Optional[KeyCallableType],
        maxsize: Optional[int],
        removal_limit: Optional[int],
        order_matters: bool,
        recursive: bool,
        auditer: Optional[Auditer],
    ) -> None:
        if auditer is None:
            auditer = global_audit
        self.__wrapped__ = op
        self.__cache__ = _cachemap(keymaker(key, order_matters), maxsize, removal_limit, auditer)
        self._recursive = recursive
        self._auditer = auditer

    def cache_info(self) -> CacheInfo:
        return self.__cache__.cacheinfo()

    def __call__(self, *args: int) -> int:
        if not args:
            raise ValueError("no values were given")
        elif len(args) == 1:
            return args[0]
        cachedop = self.__call__
        cached = self.__cache__.getcache(args)
        if cached is not None:
            return cached
        else:
            if len(args) == 2:
                self._auditer.audit(AuditEvent.CALL, {"args": args})
                value = self.__cache__.setcache(args, self.__wrapped__(*args))
            else:
                if self._recursive is True:
                    mid = len(args) // 2
                    start, end = args[:mid], args[mid:]
                    value = cachedop(cachedop(*start), cachedop(*end))
                else:
                    value = reduce(cachedop, args)
                value = self.__cache__.setcache(args, value)
            return value

    def cache_clear(self):
        self.__cache__.clearcache()

    def __repr__(self) -> str:
        memid = f"0x{hex(id(self)).upper()[2:]}"
        return f"<cachedop_callable of {self.__wrapped__!r} at {memid}>"


def cached_opfunc(
    op: Optional[OperatorCallableType] = None,
    /,
    *,
    key: Optional[KeyCallableType] = None,
    maxsize: Optional[int] = None,
    removal_limit: Optional[int] = None,
    order_matters: bool = False,
    recursive: bool = True,
    auditer: Optional[Auditer] = None,
):
    """
    Decorator to cache the results of binary operations.

    Parameters
    ----------
    op : OperatorCallableType, optional
        The callable to be cached.
        The callable must accept 2 positional arguments of `int` and return an `int`.
    key : KeyCallableType, optional
        A custom callable to generate cache keys.
        If not provided, a default key generation callable is used.
        The callable must accept 2 positional arguments of `int` and return any object that is hashable (e.g. usable as dictionary keys).
    maxsize : int, optional
        The maximum number of entries allowed in the cache.
        If not specified, the cache size is unlimited.
        The maxsize must not be zero or negative.
    removal_limit : int, optional
        The number of entries to remove when the cache reaches its maximum size.
        Defaults to one-third of `maxsize` if not specified.
        The removal_limit must not be zero, negative or higher than maxsize.
    order_matters : bool, default=False
        Determines if the order of arguments matters for the cache keys.
        If `False`, the arguments are sorted before generating the cache key.
        Useful for binary opreation is commutative (e.g. addition, multiplication, etc.)
    recursive : bool, default=True
        If `True`, enables recursive calculation for operations with more than two arguments.
        Otherwise, uses the `reduce` callable for non-recursive calculation.
    auditer : Auditer, optional
        If passed, log the opreation to the auditer for debugging purposes.
        Otherwise, the global auditer will used.

    Returns
    -------
    A decorator that can be applied to a binary operation function to enable caching.
    If `op` was passed, return the caching function directly.

    Methods
    -------
    __call__(*args: int) -> int
        Executes the cached operation with the provided arguments.
        Retrieves the result from the cache if available;
        otherwise, computes the result, stores it in the cache, and returns it.
    cache_info() -> CacheInfo
        Returns cache statistics, including the number of entries, hits, misses, and cleanup count.
    cache_clear() -> None
        Clears all entries in the cache and resets the cache statistics.

    Examples
    --------
    >>> @cached_opfunc(maxsize=100, order_matters=True)
    >>> def add(x: int, y: int) -> int:
    >>>     return x + y
    >>>
    >>> result1 = add(2, 3)  # Computes and caches the result
    >>> result2 = add(3, 2)  # Retrieves the result from the cache if order does not matter
    >>> print(add.cache_info())  # Outputs cache statistics

    >>> @cached_opfunc(maxsize=100, order_matters=False)
    >>> def gcd(x: int, y: int) -> int:
    >>>     if y == 0:
    >>>         return x
    >>>     return gcd(y, x % y)
    >>>
    >>> result = gcd(48, 18)  # Computes and caches the result
    >>> print(gcd.cache_info())  # Outputs cache statistics

    >>> def custom_key(args: tuple[int, ...]) -> Hashable:
    >>>     # just an example
    >>>     return hash(args)
    >>>
    >>> @cached_opfunc(maxsize=100, key=custom_key)
    >>> def multiply(x: int, y: int) -> int:
    >>>     return x * y
    >>>
    >>> result = multiply(3, 4)  # Computes and caches the result using custom key
    >>> result = multiply(4, 3)  # Retrieves the result from the cache due to custom key
    >>> print(multiply.cache_info())  # Outputs cache statistics

    >>> @cached_opfunc(maxsize=100, order_matters=True)
    >>> def add(x: int, y: int) -> int:
    >>>     return x + y
    >>>
    >>> result = add(2, 3)  # Computes and caches the result
    >>> print(add.cache_info())  # Outputs cache statistics
    >>> add.cache_clear()  # Clears the cache
    >>> print(add.cache_info())  # Outputs cache statistics after clearing

    >>> @cached_opfunc(maxsize=30, removal_limit=10)
    >>> def expensive_operation(x: int, y: int) -> int:
    >>>     return x * y
    >>>
    >>> for i in range(20):
    >>>     expensive_operation(i, i+1)
    >>>
    >>> print(expensive_operation.cache_info())  # Outputs cache statistics after multiple calls
    """

    params = {
        "key": key,
        "maxsize": maxsize,
        "removal_limit": removal_limit,
        "order_matters": order_matters,
        "recursive": recursive,
        "auditer": auditer,
    }
    callback = partial(_cached_opfunc_wrapper, **params)
    if op is None:
        # @cached_opfunc(...)
        return callback
    # @cached_opfunc
    return callback(op)
