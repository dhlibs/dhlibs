# This file is part of dhlibs (https://github.com/DinhHuy2010/dhlibs)
# Copyright (c) 2024 DinhHuy2010 (https://github.com/DinhHuy2010)
# SPDX-License-Identifier: MIT OR Apache-2.0 OR MPL-2.0

from __future__ import annotations

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
