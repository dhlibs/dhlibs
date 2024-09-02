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


from typing_extensions import Hashable, Optional

from dhlibs.cachedop._typings import KeyCallableType


class keymaker:
    def __init__(self, key: Optional[KeyCallableType] = None, order_matters: bool = True) -> None:
        self._key = key if key is not None else hash
        self._order_matters = order_matters
        self._cache: dict[tuple[int, ...], Hashable] = {}

    def make_key(self, args: tuple[int, ...]) -> Hashable:
        if not self._order_matters:
            args = tuple(sorted(args))
        if key := self._cache.get(args):
            return key
        key = self._key(args)
        self._cache[args] = key
        return key


def determine_maxsize_args(maxsize: Optional[int], removal_limit: Optional[int]):
    if maxsize is None:
        return (None, None)
    if maxsize < 0:
        raise ValueError("maxsize cannot be zero or negative")
    if removal_limit is None:
        return (maxsize, maxsize // 3)
    if removal_limit < 0 or removal_limit > maxsize:
        raise ValueError("removal limit cannot be zero, negative or higher than maxsize")
    return (maxsize, removal_limit)
