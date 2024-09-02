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
