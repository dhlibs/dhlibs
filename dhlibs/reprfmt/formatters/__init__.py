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

# pyright: strict
from __future__ import annotations

from dhlibs.reprfmt.formatters.base import BaseFormatterProtocol, FormatterFactoryCallable, FormatterProtocol
from dhlibs.reprfmt.formatters.default import DefaultFormatter
from dhlibs.reprfmt.formatters.others import (
    BuiltinsReprFormatter,
    MappingFormatter,
    NoneTypeFormatter,
    OnRecursiveFormatter,
    SequenceFormatter,
)
from dhlibs.reprfmt.formatters.useful import CustomReprFuncFormatter, NoIndentFormatter

__all__ = [
    "FormatterFactoryCallable",
    "FormatterProtocol",
    "BaseFormatterProtocol",
    "DefaultFormatter",
    "NoIndentFormatter",
    "BuiltinsReprFormatter",
    "OnRecursiveFormatter",
    "NoneTypeFormatter",
    "SequenceFormatter",
    "MappingFormatter",
    "CustomReprFuncFormatter",
]
