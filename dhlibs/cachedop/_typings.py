# This file is part of dhlibs (https://github.com/DinhHuy2010/dhlibs)
# Copyright (c) 2024 DinhHuy2010 (https://github.com/DinhHuy2010)
# SPDX-License-Identifier: MIT OR Apache-2.0 OR MPL-2.0

from __future__ import annotations

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
