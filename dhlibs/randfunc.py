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

"""dhlibs.randfunc - create unique random callback functions using memoization."""

from __future__ import annotations

from functools import partial, update_wrapper

from more_itertools import repeatfunc as _miter_repeatfunc
from typing_extensions import Any, Callable, Generator, Generic, NamedTuple, overload

from dhlibs._typing import P, T

__all__ = ["make_rf_unique"]

class _MemoInfo(NamedTuple):
    size: int
    hits: int
    misses: int

_MemoInfo.__name__ = "MemoInfo"



class NoNewValueFound(ValueError):
    """
    Exception raised when no new unique value can be generated.

    This exception is triggered after the maximum number of tries has been
    exceeded without generating a unique value.
    """
    pass


def _repeatfunc(func: Callable[..., T], times: int | None, args: tuple[Any, ...], kwargs: dict[str, Any]) -> Generator[T, None, None]:
    yield from _miter_repeatfunc(partial(func, *args, **kwargs), times)


class _UniqueRandomCallback(Generic[P, T]):
    """
    Ensures that repeated calls to a function produce unique outputs.

    This class wraps a callable and memoizes its outputs to avoid duplicates.
    If a duplicate value is generated, it will retry until a unique value is
    found or the maximum number of allowed tries is exceeded.

    Do not use this class directly, use make_rf_unique() instead.

    Attributes
    ----------
    __wrapped__ : Callable
        The original wrapped function.
    _memo : set
        Stores previously returned values.
    _hits : int
        Counts how many duplicate results were encountered.
    _miss : int
        Counts how many unique values were successfully generated.
    _tries : int
        Maximum number of tries allowed to find a unique result.

    Methods
    -------
    memo_info()
        Returns memoization statistics as a named tuple.
    clear_memo()
        Clears the memoization set and resets hit/miss counters.
    """

    def __init__(self, func: Callable[P, T], /, *, tries: int | None = None) -> None:
        if not callable(func):
            raise TypeError(
                f"expecting 'func' is callable, got {func.__class__.__name__}"
            )
        if tries is not None and tries <= 0:
            raise ValueError("tries cannot be 0 or below")

        self.__wrapped__ = func
        self._memo: set[T] = set()
        self._hits = 0
        self._miss = 0
        self._tries = tries

        update_wrapper(self, self.__wrapped__)

    def memo_info(self) -> _MemoInfo:
        """
        Provides information about memoization statistics.

        Returns
        -------
        MemoInfo
            A named tuple with the following fields:
            - size : int
                The number of unique values stored in the memoization set.
            - hits : int
                The number of duplicate values encountered.
            - misses : int
                The number of unique values successfully generated.
        """
        return _MemoInfo(len(self._memo), self._hits, self._miss)

    def clear_memo(self) -> None:
        """
        Clears the memoization set and resets hit/miss counters.
        """
        self._hits = 0
        self._miss = 0
        self._memo.clear()

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> T:
        for result in _repeatfunc(self.__wrapped__, self._tries, args, kwargs):
            if result not in self._memo:
                self._memo.add(result)
                self._miss += 1
                return result
            else:
                self._hits += 1
        raise NoNewValueFound("no new value return from the callback")

@overload
def make_rf_unique(
    callback: None = None, /
) -> Callable[[Callable[P, T]], _UniqueRandomCallback[P, T]]: ...
@overload
def make_rf_unique(
    callback: None = None, /, *, tries: int | None = ...
) -> Callable[[Callable[P, T]], _UniqueRandomCallback[P, T]]: ...
@overload
def make_rf_unique(callback: Callable[P, T], /) -> _UniqueRandomCallback[P, T]: ...
@overload
def make_rf_unique(callback: Callable[P, T], /, *, tries: int = ...) -> _UniqueRandomCallback[P, T]: ...

def make_rf_unique(callback: Callable[P, T] | None = None, /, *, tries: int | None = None) -> _UniqueRandomCallback[P, T] | Callable[[Callable[P, T]], _UniqueRandomCallback[P, T]]:
    """
    Creates a unique random callback using `_UniqueRandomCallback`.

    This function can be used as a decorator or a factory to wrap a function
    and ensure that it produces unique results.

    Parameters
    ----------
    callback : Callable, optional
        The function to wrap.
    tries : int, optional
        Maximum number of attempts to generate a unique result. Default is None,
        meaning unlimited tries.

    Returns
    -------
    Callable
        A wrapped function that ensures unique outputs.
        OR if callback is None, returns a decorator.

    Examples
    --------
    Use as a decorator:

    >>> @make_rf_unique(tries=3)
    ... def random_number():
    ...     import random
    ...     return random.randint(1, 10)
    ...
    >>> random_number()  # Always generates a unique result if possible.

    Use as a function factory:

    >>> unique_func = make_rf_unique(lambda: 1, tries=1)
    >>> unique_func()
    Traceback (most recent call last):
        ...
    NoNewValueFound: no new value return from the callback
    """
    def make_func(f: Callable[P, T]):
        return _UniqueRandomCallback(f, tries=tries)

    if callback is None:
        return make_func
    return make_func(callback)


