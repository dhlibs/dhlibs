# This file is part of dhlibs (https://github.com/DinhHuy2010/dhlibs)
# Copyright (c) 2024 DinhHuy2010 (https://github.com/DinhHuy2010)
# SPDX-License-Identifier: MIT OR Apache-2.0 OR MPL-2.0

from __future__ import annotations

import types

from typing_extensions import Callable, TypeVar

NEVER_RENDER_TYPES: tuple[type, ...] = (
    types.FunctionType,
    types.MethodType,
    types.BuiltinFunctionType,
    types.WrapperDescriptorType,
    types.MethodWrapperType,
    types.MethodDescriptorType,
    types.ClassMethodDescriptorType,
)
MAX_RECURSIVE_RENDER_OBJLEVEL = 10
DispatchPredCallback = Callable[[object], bool]

T = TypeVar("T")

__all__ = ["NEVER_RENDER_TYPES", "T"]
