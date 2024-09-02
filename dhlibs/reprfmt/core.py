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
