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

"""
dhlibs.indices - provides utility class
for managing and manipulating ranges of indices
with support for slices, infinite ranges, and
tuple-based ranges.
"""

from itertools import count
from typing import Any, Iterable, Optional, TypeAlias, Union, cast, overload

from dhlibs.reprfmt import put_repr

_IndicesArgsType: TypeAlias = tuple[int, ...] | slice

_marker = put_repr(type("_marker", (), {}))()


def _resolve_slice(s: slice) -> tuple[int, int | None, int]:
    start = s.start
    stop = s.stop
    step = s.step
    if start is None:
        start = 0
    if step is None:
        step = 1
    if stop is not None:
        stop = int(stop)
    return int(start), stop, int(step)


def _make_niter_from_slice(s: slice) -> Iterable[int]:
    start, stop, step = _resolve_slice(s)
    if stop is None:
        if step < 0:
            raise IndexError("negative step index without stop limit is not supported")
        r = count(start, step)
    else:
        r = range(start, stop, step)
    return r


def _resolve_indices_args(args: tuple[Any, ...], kwargs: dict[str, Any]) -> _IndicesArgsType:
    start, stop, step = [_marker] * 3
    argdict = dict(enumerate(args))

    if len(argdict) == 1 and not kwargs:
        value = argdict[0]
        if isinstance(value, (tuple, slice)):
            return cast(Union[tuple[int, ...], slice], value)
        elif isinstance(value, int) and stop is _marker:
            stop = value
    else:
        start = argdict.get(0) or kwargs.get("start", start)
        stop = argdict.get(1) or kwargs.get("stop", stop)
        step = argdict.get(2) or kwargs.get("step", step)

    if start is _marker:
        start = 0
    if stop is _marker:
        stop = None
    if step is _marker:
        step = 1
    return slice(start, stop, step)


def _compute_range_length(start: int, stop: int, step: int) -> int:
    return (stop - start + (step - 1 if step > 0 else step + 1)) // step


@put_repr
class indices:
    """
    indices - flexible handling of index ranges

    - Create ranges with start, stop, and step values.
    - Handle both finite and infinite ranges.
    - Use slices and tuples to define custom ranges.
    - Reverse ranges, access sub-ranges, and compute range length.
    - Efficiently check for containment and retrieve values by index.

    Methods:
    - values: Return an iterable of the computed values within the range.
    - contains: Check if a given integer is within the range.
    - get: Retrieve a specific value from the range by index.
    - indices: Generate a sub-range from the current range.
    - reverse: Return a reversed version of the range.
    - copy: Return a copy of the current range object.
    - slice: Property of the slice.
    - is_infinite: Property to check if the range is infinite.
    - __getitem__: Support for index access and slicing.
    - __contains__: Support for the 'in' operator.
    - __iter__: Provide iteration support over the range.
    - __len__: Compute the length of the range.
    """

    __slots__ = ("_slice",)

    @overload
    def __init__(self) -> None: ...
    @overload
    def __init__(self, stop: int, /) -> None: ...
    @overload
    def __init__(self, start: int = 0, stop: Optional[int] = None, step: int = 1) -> None: ...
    @overload
    def __init__(self, s: slice, /) -> None: ...
    @overload
    def __init__(self, s: tuple[int, ...], /) -> None: ...
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self._slice = _resolve_indices_args(args, kwargs)

    def values(self) -> Iterable[int]:
        """Get the values."""
        if isinstance(self._slice, tuple):
            return map(self.get, self._slice)
        return _make_niter_from_slice(self._slice)

    def contains(self, item: int) -> bool:
        """Return True if item within range, else False"""
        if isinstance(self._slice, tuple):
            return item in self._slice
        else:
            start, stop, step = _resolve_slice(self._slice)
            # efficiency™
            return (
                not (
                    (step > 0 and (item < start or (stop is not None and item >= stop)))
                    or step < 0
                    and (item > start or (stop is not None and item <= stop))
                )
                and (item - start) % step == 0
            )

    def get(self, index: int) -> int:
        """Get a item from `index`."""
        index = int(index)
        if isinstance(self._slice, tuple):
            return self._slice[index]

        start, stop, step = _resolve_slice(self._slice)
        if stop is None:
            if index < 0:
                raise IndexError("negative indices without stop limit is not supported")
            if step < 0:
                raise IndexError("negative step index without stop limit is not supported")
            final_index = start + (index * step)
        else:
            range_length = _compute_range_length(start, stop, step)
            if index < 0:
                index += range_length
            if index < 0 or index >= range_length:
                raise IndexError("index out of range")
            final_index = start + index * step
        return final_index

    @overload
    def indices(self) -> "indices": ...
    @overload
    def indices(self, stop: int, /) -> "indices": ...
    @overload
    def indices(self, start: int = 0, stop: Optional[int] = None, step: int = 1) -> "indices": ...
    @overload
    def indices(self, s: slice, /) -> "indices": ...
    @overload
    def indices(self, s: tuple[int, ...], /) -> "indices": ...
    def indices(self, *args: Any, **kwargs: Any) -> "indices":
        """Slice the range."""
        new_slice = _resolve_indices_args(args, kwargs)
        if isinstance(new_slice, tuple):
            d = tuple(self.get(i) for i in new_slice)
            return self.__class__(d)
        elif isinstance(self._slice, tuple):
            return self.__class__(self._slice[new_slice])
        else:
            original_slice_start, original_slice_stop, original_slice_step = _resolve_slice(self._slice)
            new_slice_start, new_slice_stop, new_slice_step = _resolve_slice(new_slice)
            final_slice_start = original_slice_start + (new_slice_start * original_slice_step)
            final_slice_step = original_slice_step * new_slice_step
            if original_slice_stop is None and new_slice_stop is None:
                final_slice = slice(final_slice_start, None, final_slice_step)
            elif new_slice_stop is None:
                final_slice = slice(final_slice_start, original_slice_stop, final_slice_step)
            else:
                nstop = original_slice_start + (new_slice_stop * original_slice_step)
                final_slice = slice(final_slice_start, nstop, final_slice_step)
            fstart, fstop, fstep = _resolve_slice(final_slice)
            if fstop is None:
                return self.__class__(final_slice)
            plength = _compute_range_length(fstart, fstop, fstep)
            if not self.is_infinite and plength >= len(self):
                return self
            return self.__class__(final_slice)

    def reverse(self) -> "indices":
        """Reverse the range."""
        if isinstance(self._slice, tuple):
            return self.__class__(tuple(reversed(self._slice)))

        start, stop, step = _resolve_slice(self._slice)

        if stop is None:
            raise ValueError("Cannot reverse an infinite range")

        # Calculate the new start, stop, and step for the reversed range
        # The last element in the reversed range should be the last element of the original range
        new_start = stop - ((stop - start) % step or step)
        new_stop = start - step
        new_step = -step

        return self.__class__(slice(new_start, new_stop, new_step))

    @overload
    def __getitem__(self, index: int) -> int: ...
    @overload
    def __getitem__(self, index: _IndicesArgsType) -> "indices": ...
    def __getitem__(self, index: int | _IndicesArgsType | Any) -> "int | indices":
        if isinstance(index, int):
            return self.get(index)
        elif isinstance(index, (slice, tuple)):
            return self.indices(index)
        else:
            return NotImplemented

    def __contains__(self, index: int) -> bool:
        return self.contains(index)

    def __iter__(self):
        return iter(self.values())

    @property
    def slice(self) -> _IndicesArgsType:
        """The slice itself."""
        return self._slice

    @property
    def is_infinite(self) -> bool:
        """Return True if the range is infinite, else False"""
        return not isinstance(self._slice, tuple) and self._slice.stop is None

    def copy(self) -> "indices":
        """Copy the range."""
        return self.__class__(self._slice)

    def __copy__(self) -> "indices":
        return self.copy()

    def __len__(self) -> int:
        if self.is_infinite:
            raise ValueError("cannot compute length of an infinite range")

        if isinstance(self._slice, tuple):
            return len(self._slice)

        start, stop, step = _resolve_slice(self._slice)

        if stop is None:
            raise RuntimeError("internal error: stop should not be None here.")

        length = (stop - start + (step - 1 if step > 0 else step + 1)) // step

        return max(0, length)
