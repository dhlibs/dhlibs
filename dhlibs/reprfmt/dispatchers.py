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
