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


from collections import defaultdict
from enum import Enum, auto

from typing_extensions import Any, Callable, Hashable, NamedTuple, Optional, Sequence, TypeAlias, Union


class AuditEvent(Enum):
    HIT = auto()
    MISS = auto()
    CALL = auto()
    CLEAN = auto()
    REMOVE_KEY = auto()


CacheInfo = NamedTuple(
    "cachedop_cacheinfo",
    [("size", int), ("hits", int), ("misses", int), ("cleanup_count", int)],
)
OperatorCallableType: TypeAlias = Callable[[int, int], int]
KeyCallableType: TypeAlias = Callable[[tuple[int, ...]], Hashable]


AuditCallableType: TypeAlias = Callable[[AuditEvent, dict[str, Any]], None]
AuditDefaultDict: TypeAlias = defaultdict[AuditEvent, list[AuditCallableType]]
AuditEvents: TypeAlias = Optional[Union[AuditEvent, Sequence[AuditEvent]]]
