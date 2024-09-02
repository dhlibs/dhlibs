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
