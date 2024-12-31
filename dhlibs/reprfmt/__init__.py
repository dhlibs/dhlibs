# This file is part of dhlibs (https://github.com/DinhHuy2010/dhlibs)
# Copyright (c) 2024 DinhHuy2010 (https://github.com/DinhHuy2010)
# SPDX-License-Identifier: MIT OR Apache-2.0 OR MPL-2.0

"""
dhlibs.reprfmt
Generic and advanced representation (__repr__) functions,
formatters for Python objects.
"""

from __future__ import annotations

from dhlibs.reprfmt.core import format_repr
from dhlibs.reprfmt.deco import put_repr
from dhlibs.reprfmt.utils import register_formatter

__all__ = ["format_repr", "put_repr", "register_formatter"]
