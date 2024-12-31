# This file is part of dhlibs (https://github.com/DinhHuy2010/dhlibs)
# Copyright (c) 2024 DinhHuy2010 (https://github.com/DinhHuy2010)
# SPDX-License-Identifier: MIT OR Apache-2.0 OR MPL-2.0

"""dhlibs.alias_callable - very simple module to create aliased callables"""

from __future__ import annotations

from functools import wraps

from typing_extensions import Callable, Optional

from dhlibs._typing import P, T


def alias_callable(
    callback: Callable[P, T],
    name: str,
    qualname: Optional[str] = None,
    doc: Optional[str] = None,
) -> Callable[P, T]:
    if not callable(callback):
        raise TypeError("'callback' is not callable")

    @wraps(callback)
    def _(*args: P.args, **kwargs: P.kwargs) -> T:
        return callback(*args, **kwargs)

    _.__name__ = name
    if qualname is None:
        t = callback.__qualname__[:]
        _.__qualname__ = ".".join([*t.split(".")[:-1], name])
    else:
        _.__qualname__ = qualname
    if doc is not None:
        _.__doc__ = doc
    return _
