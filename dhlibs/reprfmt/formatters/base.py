# pyright: strict

import inspect

from typing_extensions import Any, Optional, Protocol

from dhlibs.reprfmt.constants import MAX_RECURSIVE_RENDER_OBJLEVEL, NEVER_RENDER_TYPES
from dhlibs.reprfmt.options import Options


class FormatterFactoryCallable(Protocol):
    def __call__(self, *, options: Optional[Options] = None) -> "FormatterProtocol": ...


class FormatterProtocol(Protocol):
    def __init__(self, *, options: Optional[Options] = None) -> None: ...
    @property
    def options(self) -> Options: ...
    @property
    def fullname_included(self) -> bool: ...
    def _get_object_name(self, obj: object, /) -> str:
        objcls = type(obj)
        if self.fullname_included:
            from dhlibs.reprfmt.utils import getmodname

            modname = getmodname(obj)
            return f"{modname}.{objcls.__qualname__}"
        return objcls.__name__

    def _real_format(self, obj: object, /, *, options: Options, objlevel: int) -> str: ...

    def format(self, obj: object, /, *, options: Optional[Options] = None) -> str:
        passed = self.options
        if options is not None:
            passed = passed.merge(options)

        return self._real_format(obj, options=passed, objlevel=1)


class BaseFormatterProtocol(FormatterProtocol):
    _objids: set[int] = set()

    def __init__(self, *, options: Optional[Options] = None) -> None:
        if options is None:
            options = Options()
        self._options = options

    @property
    def options(self) -> Options:
        return self._options

    @property
    def fullname_included(self) -> bool:
        return self._options.get("fullname_included", False)

    def _is_name_mangled(self, obj: object, name: str) -> bool:
        return name.startswith("_%s__" % type(obj).__name__)

    def _is_name_internal(self, obj: object, name: str) -> bool:
        return self._is_name_mangled(obj, name) or name.startswith("_")

    def _render_value(self, subobj: object, options: Options, objlevel: int) -> str:
        from dhlibs.reprfmt.formatters.others import BuiltinsReprFormatter, OnRecursiveFormatter
        from dhlibs.reprfmt.utils import pick_formatter

        maxlevel = options.get("recursive_maxlevel", MAX_RECURSIVE_RENDER_OBJLEVEL)
        if id(subobj) in self._objids and objlevel >= maxlevel:
            f = OnRecursiveFormatter(options=self.options)
        else:
            f = pick_formatter(subobj, fallback=BuiltinsReprFormatter, options=self.options)
        passed = f.options.merge(options)
        return f._real_format(subobj, options=passed, objlevel=objlevel + 1)

    def _get_members_from_object(self, obj: object, /) -> dict[str, object]:
        attrs: dict[str, Any] = {}
        for name, val in inspect.getmembers(obj):
            if self._is_name_internal(obj, name):
                continue
            if isinstance(val, NEVER_RENDER_TYPES):
                continue
            attrs[name] = val
        return attrs

    def _actual_format(self, obj: object, /, *, options: Options, objlevel: int) -> str:
        raise NotImplementedError

    def _real_format(self, obj: object, /, *, options: Options, objlevel: int) -> str:
        self._objids.add(id(obj))
        return self._actual_format(obj, options=options, objlevel=objlevel)
