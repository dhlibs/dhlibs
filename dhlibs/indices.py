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

from __future__ import annotations

from functools import total_ordering
from itertools import count

from more_itertools import first
from typing_extensions import (
    Any,
    Iterable,
    Literal,
    Mapping,
    NotRequired,
    Optional,
    TypeAlias,
    TypedDict,
    Union,
    cast,
    overload,
)

from dhlibs.reprfmt import put_repr

_IndicesArgsType: TypeAlias = Union[tuple[int, ...], slice]

_marker = put_repr(type("_marker", (), {}))()


class BaseIndicesException(Exception):
    pass


class OutOfRange(BaseIndicesException):
    pass


class GotInfiniteRange(BaseIndicesException):
    pass


class NoRangeFound(BaseIndicesException):
    pass


def _resolve_slice(s: slice) -> tuple[int, Optional[int], int]:
    start = s.start
    stop = s.stop
    step = s.step
    if start is None:
        start = 0
    if step is None:
        step = 1
    return start, stop, step


def _make_niter_from_slice(s: slice) -> Iterable[int]:
    start, stop, step = _resolve_slice(s)
    if stop is None:
        if step < 0:
            raise GotInfiniteRange("negative step index without stop limit is not supported")
        r = count(start, step)
    else:
        r = range(start, stop, step)
    return r


def _resolve_indices_args(args: tuple[Any, ...], kwargs: dict[str, Any]) -> _IndicesArgsType:
    start, stop, step = [_marker] * 3
    argdict = dict(enumerate(args))
    kwargs = kwargs.copy()
    kwargs.pop("_ref", None)

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


class SliceData(TypedDict):
    start: int
    stop: Optional[int]
    step: int


class IndicesSliceData(TypedDict):
    type: Literal["slice"]
    slice: SliceData


class IndicesIndexesTupleData(TypedDict):
    type: Literal["indexes"]
    values: list[int]


class IndicesRangeData(TypedDict):
    slice: Union[IndicesSliceData, IndicesIndexesTupleData]
    ref: NotRequired[IndicesRangeData]


@put_repr
@total_ordering
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

    __slots__ = ("_slice", "_iter", "_ref")

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
        self._ref: Optional[indices] = kwargs.get("_ref")
        self._iter = None

    def values(self) -> Iterable[int]:
        """Get the values."""
        if isinstance(self._slice, slice):
            it = _make_niter_from_slice(self._slice)
            return map(self._ref.get, it) if self._ref else it
        return map(self.get, range(len(self._slice)))

    def contains(self, item: int) -> bool:
        """Return True if item within range, else False"""
        if isinstance(self._slice, tuple):
            # not the fastest way, but is the most efficient
            return first(filter(lambda x: x == item, self.values()), None) is not None
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
        if isinstance(self._slice, tuple):
            if self._ref is None:
                raise NoRangeFound("no slice range cannot been found assoicated with this range")
            return self._ref.get(self._slice[index])

        start, stop, step = _resolve_slice(self._slice)
        if stop is None:
            if index < 0:
                raise GotInfiniteRange("negative indices without stop limit is not supported")
            if step < 0:
                raise GotInfiniteRange("negative step index without stop limit is not supported")
            final_index = start + (index * step)
        else:
            range_length = _compute_range_length(start, stop, step)
            if index < 0:
                index += range_length
            if index < 0 or index >= range_length:
                raise OutOfRange("index out of range")
            final_index = start + index * step
        return final_index

    @overload
    def indices(self) -> indices: ...
    @overload
    def indices(self, stop: int, /) -> indices: ...
    @overload
    def indices(self, start: int = 0, stop: Optional[int] = None, step: int = 1) -> indices: ...
    @overload
    def indices(self, s: slice, /) -> indices: ...
    @overload
    def indices(self, s: tuple[int, ...], /) -> indices: ...
    def indices(self, *args: Any, **kwargs: Any) -> indices:
        """Slice the range."""
        new_slice = _resolve_indices_args(args, kwargs)

        if isinstance(new_slice, tuple) or isinstance(self._slice, tuple):
            return self.__class__(new_slice, _ref=self)  # pyright: ignore[reportCallIssue]

        ostart, ostop, ostep = _resolve_slice(self._slice)
        nstart, nstop, nstep = _resolve_slice(new_slice)
        fstart = ostart + (nstart * ostep)
        fstep = ostep * nstep
        if ostop is None and nstop is None:
            final_slice = slice(fstart, None, fstep)
        elif nstop is None:
            final_slice = slice(fstart, ostop, fstep)
        else:
            fstop = ostart + (nstop * ostep)
            final_slice = slice(fstart, fstop, fstep)
        fstart, fstop, fstep = _resolve_slice(final_slice)
        if fstop is None:
            return self.__class__(final_slice)
        plength = _compute_range_length(fstart, fstop, fstep)
        if not self.is_infinite and plength >= len(self):
            return self
        return self.__class__(final_slice)

    def reverse(self) -> indices:
        """Reverse the range."""
        if isinstance(self._slice, tuple):
            return self.__class__(tuple(reversed(self._slice)), _ref=self._ref)  # pyright: ignore[reportCallIssue]

        start, stop, step = _resolve_slice(self._slice)

        if stop is None:
            raise ValueError("Cannot reverse an infinite range")

        new_start = stop - ((stop - start) % step or step)
        new_stop = start - step
        new_step = -step

        return self.__class__(slice(new_start, new_stop, new_step))

    def __reversed__(self):
        return self.reverse()

    @overload
    def __getitem__(self, index: int) -> int: ...
    @overload
    def __getitem__(self, index: _IndicesArgsType) -> indices: ...
    def __getitem__(self, index: Union[int, _IndicesArgsType, Any]) -> Union[int, indices]:
        if isinstance(index, int):
            return self.get(index)
        elif isinstance(index, (slice, tuple)):
            return self.indices(index)
        else:
            return NotImplemented

    def __contains__(self, index: int) -> bool:
        return self.contains(index)

    def __iter__(self):
        return self

    def __next__(self) -> int:
        if self._iter is None:
            self._iter = iter(self.values())
        try:
            return next(self._iter)
        except StopIteration:
            self._iter = iter(self.values())
            raise

    @property
    def slice(self) -> _IndicesArgsType:
        """The slice itself."""
        return self._slice

    @property
    def is_infinite(self) -> bool:
        """Return True if the range is infinite, else False"""
        return not isinstance(self._slice, tuple) and self._slice.stop is None

    @property
    def reference(self) -> Optional[indices]:
        """The reference of another `indices`, mostly use handling tuple-based slices."""
        return self._ref

    def copy(self) -> indices:
        """Copy the range."""
        return self.__class__(self._slice, _ref=self._ref)  # pyright: ignore[reportCallIssue]

    def for_json(self) -> IndicesRangeData:
        """Convert object to Python dictionary"""
        if isinstance(self._slice, tuple):
            slice_data = IndicesIndexesTupleData(type="indexes", values=list(self._slice))
        else:
            start, stop, step = _resolve_slice(self._slice)
            slice_data = IndicesSliceData(type="slice", slice=SliceData(start=start, stop=stop, step=step))
        d = IndicesRangeData(slice=slice_data)
        if self._ref:
            d["ref"] = self._ref.for_json()
        return d

    @classmethod
    def from_json(cls, data: Mapping[str, Any]) -> indices:
        """Create `indices` from a Python dictionary"""
        self = object.__new__(cls)
        self._ref = None
        if ref := data.get("ref"):
            self._ref = cls.from_json(ref)
        slice_data = data["slice"]
        if slice_data["type"] == "indexes":
            self._slice = tuple(slice_data["values"])
        elif slice_data["type"] == "slice":
            sdata = slice_data["slice"]
            self._slice = slice(sdata["start"], sdata["stop"], sdata["step"])
        self._iter = None
        return self

    def __len__(self) -> int:
        if self.is_infinite:
            raise GotInfiniteRange("cannot compute length of an infinite range")

        if isinstance(self._slice, tuple):
            return len(self._slice)

        start, stop, step = _resolve_slice(self._slice)

        if stop is None:
            raise RuntimeError("internal error: stop should not be None here.")

        length = (stop - start + (step - 1 if step > 0 else step + 1)) // step

        return max(0, length)

    def __hash__(self) -> int:
        return hash(self._slice)

    def __eq__(self, obj: object) -> bool:
        if not isinstance(obj, indices):
            return NotImplemented
        if self._slice != obj._slice:
            return False
        if self._ref is None:
            return obj._ref is None
        return self._ref == obj._ref

    def __le__(self, obj: object) -> bool:
        if not isinstance(obj, indices):
            return NotImplemented
        if self.is_infinite:
            cm = True
        elif obj.is_infinite:
            cm = False
        if isinstance(self._slice, tuple):
            if isinstance(obj._slice, tuple):
                cm = len(self._slice) <= len(obj._slice)
            else:
                start, stop, step = _resolve_slice(obj._slice)
                assert stop is not None
                cm = len(self._slice) <= _compute_range_length(start, stop, step)
        else:
            start, stop, step = _resolve_slice(self._slice)
            assert stop is not None
            if isinstance(obj._slice, tuple):
                cm = _compute_range_length(start, stop, step) <= len(obj._slice)
            else:
                ostart, ostop, ostep = _resolve_slice(obj._slice)
                assert ostop
                cm = _compute_range_length(start, stop, step) <= _compute_range_length(ostart, ostop, ostep)
        return cm
