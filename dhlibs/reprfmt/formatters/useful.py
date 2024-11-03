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

from typing_extensions import Any, Callable, Optional

from dhlibs.reprfmt.formatters.base import BaseFormatterProtocol
from dhlibs.reprfmt.formatters.default import DefaultFormatter
from dhlibs.reprfmt.options import Options


class NoIndentFormatter(DefaultFormatter):
    def _actual_format(self, obj: object, /, *, options: Options, objlevel: int) -> str:
        options = options.merge(Options(indent=None))
        return super()._actual_format(obj, options=options, objlevel=objlevel)


class CustomReprFuncFormatter(BaseFormatterProtocol):
    def __init__(
        self,
        *,
        options: Optional[Options] = None,
        func: Optional[Callable[[Any, Options, int], str]] = None,
    ) -> None:
        super().__init__(options=options)
        self._fn = func

    def _actual_format(self, obj: Any, /, *, options: Options, objlevel: int) -> str:
        if self._fn is None:
            return super()._render_value(obj, options, objlevel - 1)
        return self._fn(obj, options, objlevel)
