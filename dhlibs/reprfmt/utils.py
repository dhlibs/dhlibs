# pyright: strict

from inspect import getfile, getmodulename

from typing_extensions import TYPE_CHECKING, Mapping, Optional, Sequence, Union, cast

from dhlibs.reprfmt.formatters.base import FormatterFactoryCallable, FormatterProtocol
from dhlibs.reprfmt.formatters.default import DefaultFormatter
from dhlibs.reprfmt.formatters.others import (
    BuiltinsReprFormatter,
    MappingFormatter,
    NoneTypeFormatter,
    SequenceFormatter,
)
from dhlibs.reprfmt.options import Options

if TYPE_CHECKING:
    from dhlibs.reprfmt.deco import ReprCallbackDescriptor

from dhlibs.reprfmt.constants import DispatchPredCallback
from dhlibs.reprfmt.dispatchers import Dispatcher


def _is_class_deco_by_reprfmt(typ: type[object], /) -> bool:
    from dhlibs.reprfmt.deco import ReprCallbackDescriptor

    if not getattr(typ, "__use_reprfmt__", False):
        return False
    return isinstance(getattr(typ, "__repr__", None), ReprCallbackDescriptor)


_dispatcher = Dispatcher()


def register_formatter(
    pred: Union[type[object], DispatchPredCallback],
    fmt_factory: FormatterFactoryCallable,
) -> None:
    _dispatcher.dispatch(pred, fmt_factory)


def _init_formatter() -> None:
    for _ in (str, int, bytes, bool):
        _dispatcher.dispatch(_, BuiltinsReprFormatter)
    _dispatcher.dispatch(type(None), NoneTypeFormatter)
    _dispatcher.dispatch(Sequence, SequenceFormatter)
    _dispatcher.dispatch(Mapping, MappingFormatter)


_init_formatter()


def pick_formatter_factory(
    obj: object,
    *,
    fallback: FormatterFactoryCallable = DefaultFormatter,
    dispatcher: Optional[Dispatcher] = None,
) -> FormatterFactoryCallable:
    fac = (_dispatcher if dispatcher is None else dispatcher).select_factory(obj)
    return fac if fac is not None else fallback


def pick_formatter(
    obj: object,
    /,
    *,
    fallback: FormatterFactoryCallable = DefaultFormatter,
    options: Optional[Options] = None,
) -> FormatterProtocol:
    clsofobj = type(obj)
    if _is_class_deco_by_reprfmt(clsofobj):
        # decorated by put_repr()
        ck = cast("ReprCallbackDescriptor", clsofobj.__repr__)
        f = ck.get_fmt(obj)
        if options:
            f = f.__class__(options=f.options.merge(options))
        return f
    dispatcher = options.get("dispatcher", None) if options else None
    fac = pick_formatter_factory(obj, fallback=fallback, dispatcher=dispatcher)
    return fac(options=options)


def getmodname(obj: object) -> str:
    cls = type(obj)
    modname = cls.__module__
    if modname == "__main__":
        try:
            file = getfile(cls)
        except (TypeError, OSError):
            pass
        else:
            modname = getmodulename(file) or modname
    return modname
