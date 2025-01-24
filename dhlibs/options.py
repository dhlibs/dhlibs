from __future__ import annotations

from decimal import Decimal

from typing_extensions import Sequence, TypeAlias, TypeVar, Union, overload

_AllowedTypes: TypeAlias = Union[str, int, float, complex, Decimal, None, Sequence["_AllowedTypes"], "Options"]

D = TypeVar("D")
_nope = object()


class Options:
    def __init__(
        self,
        doptions: dict[str, _AllowedTypes] | None = None,
        /,
        **options: _AllowedTypes,
    ) -> None:
        self.raw = options
        if doptions:
            self.raw.update(doptions)

    @overload
    def get(self, key: str, *, _orig_key: str | None = None) -> _AllowedTypes: ...
    @overload
    def get(self, key: str, default: D = ..., *, _orig_key: str | None = None) -> _AllowedTypes | D: ...

    def get(self, key: str, default: D = _nope, *, _orig_key: str | None = None) -> _AllowedTypes | D:
        if "." in key:
            _fail = object()
            state = self
            parts = key.split(".")
            for part in parts[:-1]:
                p = state.get(part, _fail, _orig_key=key)
                if p is _fail or not isinstance(p, Options):
                    if default is not _nope:
                        return default
                    else:
                        raise KeyError(_orig_key or key)
                else:
                    state = p
            return state.get(parts[-1], default, _orig_key=key)
        value = self.raw.get(key, default)
        if value is _nope:
            raise KeyError(_orig_key or key)
        return value

    def set(self, key: str, value: _AllowedTypes, *, _orig_key: str | None = None) -> None:
        if "." in key:
            _fail = object()
            state = self
            parts = key.split(".")
            for i, part in enumerate(parts[:-1]):
                p = state.get(part, _fail, _orig_key=".".join(parts[:i]))
                if p is _fail or not isinstance(p, Options):
                    raise KeyError(_orig_key or key)
                else:
                    state = p
            return state.set(parts[-1], value, _orig_key=_orig_key)
        self.raw[key] = value

    def delete(self, key: str, default: D = _nope, *, _orig_key: str | None = None) -> _AllowedTypes | D:
        if "." in key:
            _fail = object()
            state = self
            parts = key.split(".")
            for i, part in enumerate(parts[:-1]):
                p = state.get(part, _fail, _orig_key=".".join(parts[:i]))
                if p is _fail or not isinstance(p, Options):
                    raise KeyError(_orig_key or key)
                else:
                    state = p
            return state.delete(parts[-1], default, _orig_key=_orig_key)
        try:
            val = self.raw[key]
        except KeyError:
            if default is _nope:
                raise KeyError(_orig_key or key) from None
            return default
        del self.raw[key]
        return val

    def copy(self) -> Options:
        return Options(self.raw.copy())

    def __eq__(self, value: object) -> bool:
        if not isinstance(value, Options):
            return NotImplemented
        return self.raw == value.raw

    def __repr__(self) -> str:
        pairs: list[str] = []
        for key, value in self.raw.items():
            pairs.append(f"{key}={value!r}")
        return "{}({})".format(self.__class__.__name__, ", ".join(pairs))
