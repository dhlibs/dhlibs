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

from dhlibs.reprfmt.formatters.base import BaseFormatterProtocol
from dhlibs.reprfmt.options import Options


class DefaultFormatter(BaseFormatterProtocol):
    def _actual_format(self, obj: object, /, *, options: Options, objlevel: int) -> str:
        indent = options.get("indent", None)

        def _indent_fmt(level: int) -> str:
            if indent is None:
                return ""
            out = (indent * level) * " "
            return out

        objmembers = self._get_members_from_object(obj)
        header = f"{self._get_object_name(obj)}("
        if objmembers and indent is not None:
            header += "\n"
        elements: list[str] = []
        footer = _indent_fmt(objlevel - 1) + ")"

        if objmembers and indent is not None:
            footer = "\n" + footer
        delimeter = ","
        if indent is not None:
            delimeter += "\n"
        else:
            delimeter += " "

        for key, value in objmembers.items():
            elements.append(f"{_indent_fmt(objlevel)}{key}={self._render_value(value, options, objlevel)}")

        body = delimeter.join(elements)
        return header + body + footer
