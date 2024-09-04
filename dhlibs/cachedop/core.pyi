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

from typing_extensions import Callable, Optional, Protocol, overload, type_check_only

from dhlibs.cachedop._typings import CacheInfo, KeyCallableType, OperatorCallableType
from dhlibs.cachedop._utils import keymaker
from dhlibs.cachedop.audit import Auditer

__all__ = ["cached_opfunc"]

@type_check_only
class _cachemap_protocol(Protocol):
    def __init__(self, keymaker: keymaker, maxsize: Optional[int], removal_limit: Optional[int]) -> None: ...
    def cleancache(self) -> None: ...
    def getcache(self, args: tuple[int, ...]) -> Optional[int]: ...
    def setcache(self, args: tuple[int, ...], value: int) -> int: ...
    def cacheinfo(self) -> CacheInfo: ...
    def clearcache(self) -> None: ...

@type_check_only
class _cached_opfunc_protocol(Protocol):
    __wrapped__: OperatorCallableType
    __cache__: _cachemap_protocol

    def cache_info(self) -> CacheInfo: ...
    def __call__(self, *args: int) -> int: ...
    def cache_clear(self) -> None: ...
    def __repr__(self) -> str: ...

@overload
def cached_opfunc(op: OperatorCallableType, /) -> _cached_opfunc_protocol: ...
@overload
def cached_opfunc(
    op: OperatorCallableType,
    /,
    *,
    key: Optional[KeyCallableType] = None,
    maxsize: Optional[int] = None,
    removal_limit: Optional[int] = None,
    order_matters: bool = False,
    recursive: bool = True,
    auditer: Optional[Auditer] = None,
) -> _cached_opfunc_protocol: ...
@overload
def cached_opfunc(
    op: None = None,
    /,
    *,
    key: Optional[KeyCallableType] = None,
    maxsize: Optional[int] = None,
    removal_limit: Optional[int] = None,
    order_matters: bool = False,
    recursive: bool = True,
    auditer: Optional[Auditer] = None,
) -> Callable[[OperatorCallableType], _cached_opfunc_protocol]: ...
