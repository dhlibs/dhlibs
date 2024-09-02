from typing_extensions import Any, Hashable, Mapping, Sequence, cast

from dhlibs.reprfmt.formatters.base import BaseFormatterProtocol
from dhlibs.reprfmt.options import Options

NoneType = type(None)


class BuiltinsReprFormatter(BaseFormatterProtocol):
    def _real_format(self, obj: object, /, *, options: Options, objlevel: int) -> str:  # noqa: ARG002
        try:
            return repr(obj)
        except Exception:
            return object.__repr__(obj)


class OnRecursiveFormatter(BaseFormatterProtocol):
    def _get_container_type(self, obj: object):
        if isinstance(obj, Sequence) and not isinstance(obj, (str, bytes)):
            return Sequence
        elif isinstance(obj, Mapping):
            return Mapping
        else:
            return None

    def _real_format(self, obj: object, /, *, options: Options, objlevel: int) -> str:
        from dhlibs.reprfmt.utils import pick_formatter

        if isinstance(obj, (str, int, bytes, bool, type(None))):
            return pick_formatter(obj, fallback=BuiltinsReprFormatter, options=self.options)._real_format(
                obj, options=options, objlevel=objlevel
            )

        is_not_using_indent = options.get("indent", None) is None
        if is_not_using_indent:
            return "..."
        else:
            if ct := self._get_container_type(obj):
                f = "[%s]" if ct is Sequence else "{%s}"
                return "%s(%s)" % (self._get_object_name(obj), f % "...")
            return f"<object {self._get_object_name(obj)!r} at {hex(id(obj)).upper()}>"


class NoneTypeFormatter(BaseFormatterProtocol):
    def _real_format(self, obj: object, /, *, options: Options, objlevel: int) -> str:  # noqa: ARG002
        if not isinstance(obj, NoneType):
            raise TypeError("not NoneType")
        return "None"


class SequenceFormatter(BaseFormatterProtocol):
    def _actual_format(self, obj: object, /, *, options: Options, objlevel: int) -> str:
        indent = options.get("indent", None)

        def _indent_fmt(level: int) -> str:
            if indent is None:
                return ""
            out = (indent * level) * " "
            return out

        elements: list[str] = []
        obj = cast(Sequence[Any], obj)
        nitems = len(obj)
        maxitems = options.get("maxitems", None)
        for index, item in enumerate(obj):
            elements.append(f"{_indent_fmt(objlevel)}{self._render_value(item, options, objlevel)}")
            if maxitems and index == maxitems - 1:
                remaining = nitems - maxitems
                if remaining:
                    e = f"[and {remaining} more items]" if indent is not None else "..."
                    elements.append(f"{_indent_fmt(objlevel)}{e}")
                break

        header = f"{self._get_object_name(obj)}(["
        delimeter = ","
        if indent is not None:
            delimeter += "\n"
        else:
            delimeter += " "
        footer = "])"
        if elements:
            footer = _indent_fmt(objlevel - 1) + footer
        if elements and indent is not None:
            header += "\n"
        if elements and indent is not None:
            footer = "\n" + footer
        return header + delimeter.join(elements) + footer


class MappingFormatter(BaseFormatterProtocol):
    def _actual_format(self, obj: object, /, *, options: Options, objlevel: int) -> str:
        indent = options.get("indent", None)

        def _indent_fmt(level: int) -> str:
            if indent is None:
                return ""
            out = (indent * level) * " "
            return out

        elements: list[str] = []
        obj = cast(Mapping[Hashable, Any], obj)
        nitems = len(obj)
        maxitems = options.get("maxitems", None)
        for index, (key, item) in enumerate(obj.items()):
            elements.append(
                f"{_indent_fmt(objlevel)}{self._render_value(key, options, objlevel)}: {self._render_value(item, options, objlevel)}"
            )
            if maxitems and index == maxitems - 1:
                remaining = nitems - maxitems
                if remaining:
                    e = f"[and {remaining} more items]" if indent is not None else "..."
                    elements.append(f"{_indent_fmt(objlevel)}{e}")
                break

        header = f"{self._get_object_name(obj)}({'{'}"
        delimeter = ","
        if indent is not None:
            delimeter += "\n"
        else:
            delimeter += " "
        footer = "})"
        if elements:
            footer = _indent_fmt(objlevel - 1) + footer
        if elements and indent is not None:
            header += "\n"
        if elements and indent is not None:
            footer = "\n" + footer
        return header + delimeter.join(elements) + footer
