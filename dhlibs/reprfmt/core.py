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

from __future__ import annotations

from typing_extensions import Optional

from dhlibs.reprfmt.formatters import FormatterFactoryCallable, FormatterProtocol
from dhlibs.reprfmt.options import Options
from dhlibs.reprfmt.utils import pick_formatter


def format_repr(
    obj: object,
    /,
    *,
    indent: Optional[int] = None,
    fullname_included: bool = False,
    formatter: Optional[FormatterProtocol] = None,
    format_factory: Optional[FormatterFactoryCallable] = None,
    options: Optional[Options] = None,
) -> str:
    doptions = Options(indent=indent, fullname_included=fullname_included)
    if formatter is None:
        if format_factory is not None:
            formatter = format_factory(options=doptions)
        else:
            formatter = pick_formatter(obj, options=doptions)
    return formatter.format(obj, options=options)


__all__ = ["format_repr"]
