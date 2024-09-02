from typing_extensions import Callable, Optional, Union, cast, overload

from dhlibs.reprfmt.constants import T
from dhlibs.reprfmt.dispatchers import Dispatcher
from dhlibs.reprfmt.formatters import DefaultFormatter, FormatterFactoryCallable, FormatterProtocol
from dhlibs.reprfmt.options import Options
from dhlibs.reprfmt.utils import pick_formatter_factory


class RCDBoundMethod:
    def __init__(self, rcd: "ReprCallbackDescriptor", obj: object) -> None:
        self._rcd = rcd
        self._obj = obj

    def __call__(self) -> str:
        return self._rcd(self._obj)

    def __repr__(self) -> str:
        clsname = type(self._obj).__qualname__
        return f"<bound method {clsname}.__repr__ of {clsname} (reprfmt)>"


class ReprCallbackDescriptor:
    def __init__(
        self,
        *,
        owner: type[object],
        fmt: Optional[FormatterProtocol],
        fmt_factory: Optional[FormatterFactoryCallable],
        options: Options,
    ) -> None:
        self._fmt = fmt
        self._fmt_factory = fmt_factory
        self._options = options
        self.__owner__ = owner
        self.__name__ = "__repr__"
        self.__qualname__ = f"{owner.__qualname__}.{self.__name__}"

    def get_fmt(self, obj: object) -> FormatterProtocol:
        if self._fmt is None:
            options = self._options
            if self._fmt_factory is not None:
                fmtf = self._fmt_factory
            else:
                fmtf = pick_formatter_factory(
                    obj, dispatcher=cast(Optional[Dispatcher], options.get("dispatcher", None))
                )
            self._fmt = fmtf(options=options)
        return self._fmt

    def __call__(self, obj: object) -> str:
        fmt = self.get_fmt(obj)
        return fmt.format(obj)

    def __get__(self, inst: Optional[object], owner: type[object]):
        if inst is None:
            return self
        return RCDBoundMethod(self, inst)

    def __repr__(self) -> str:
        return f"<reprfmt {self.__name__} method for {self.__owner__.__qualname__}>"


@overload
def put_repr(cls: type[T], /) -> type[T]: ...
@overload
def put_repr(
    cls: type[T],
    /,
    *,
    indent: Optional[int] = None,
    fullname_included: bool = False,
    formatter: Optional[FormatterProtocol] = None,
    format_factory: FormatterFactoryCallable = DefaultFormatter,
    options: Optional[Options] = None,
) -> type[T]: ...
@overload
def put_repr(
    cls: None = None,
    /,
    *,
    indent: Optional[int] = None,
    fullname_included: bool = False,
    formatter: Optional[FormatterProtocol] = None,
    format_factory: FormatterFactoryCallable = DefaultFormatter,
    options: Optional[Options] = None,
) -> Callable[[type[T]], type[T]]: ...


def put_repr(
    cls: Optional[type[T]] = None,
    /,
    *,
    indent: Optional[int] = None,
    fullname_included: bool = False,
    formatter: Optional[FormatterProtocol] = None,
    format_factory: Optional[FormatterFactoryCallable] = None,
    options: Optional[Options] = None,
) -> Union[Callable[[type[T]], type[T]], type[T]]:
    doptions = Options(indent=indent, fullname_included=fullname_included)
    if options is not None:
        doptions = doptions.merge(options)

    def decorator(cls: type[T]) -> type[T]:
        reprfn = ReprCallbackDescriptor(owner=cls, fmt=formatter, fmt_factory=format_factory, options=doptions)
        setattr(cls, "__repr__", reprfn)
        setattr(cls, "__use_reprfmt__", True)
        return cls

    if cls is None:
        return decorator
    return decorator(cls)
