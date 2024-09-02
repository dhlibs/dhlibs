from typing_extensions import Any, Union

from dhlibs.reprfmt.constants import T


class Options:
    def __init__(self, **options: Any) -> None:
        self._options = options

    def get(self, key: str, default: T) -> Union[Any, T]:
        return self._options.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self._options[key] = value

    def delete(self, key: str) -> None:
        self._options.pop(key, None)

    def merge(self, other: "Options") -> "Options":
        merged = self._options.copy()
        merged.update(other._options)
        return self.__class__(**merged)

    def __repr__(self) -> str:
        return "%s(%s)" % (
            self.__class__.__name__,
            ", ".join("%s=%r" % p for p in self._options.items()),
        )
