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

from typing_extensions import Optional, Union, get_origin

from dhlibs.reprfmt.constants import DispatchPredCallback
from dhlibs.reprfmt.formatters.base import FormatterFactoryCallable


class Dispatcher:
    def __init__(self) -> None:
        self._type2fmt: dict[type[object], FormatterFactoryCallable] = {}
        self._pred2fmt: dict[DispatchPredCallback, FormatterFactoryCallable] = {}

    def dispatch_type(self, typ: type[object], fmt_factory: FormatterFactoryCallable) -> None:
        self._type2fmt[typ] = fmt_factory

    def dispatch_predicate(self, typ: DispatchPredCallback, fmt_factory: FormatterFactoryCallable) -> None:
        self._pred2fmt[typ] = fmt_factory

    def dispatch(
        self,
        pred: Union[type[object], DispatchPredCallback],
        fmt_factory: FormatterFactoryCallable,
    ) -> None:
        origin = get_origin(pred)
        if not origin and callable(pred) and not isinstance(pred, type):
            self.dispatch_predicate(pred, fmt_factory)
            return

        if origin is None:
            origin = pred

        if isinstance(origin, type):
            self.dispatch_type(origin, fmt_factory)
            return

        raise RuntimeError("not a type or callable")

    def select_factory(self, obj: object, /) -> Optional[FormatterFactoryCallable]:
        for typ, fmt in self._type2fmt.items():
            if isinstance(obj, typ):
                return fmt

        for pred, fmt in self._pred2fmt.items():
            if pred(obj):
                return fmt

        return None
