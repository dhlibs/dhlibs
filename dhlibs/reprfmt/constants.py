import types

from typing_extensions import Callable, TypeVar

NEVER_RENDER_TYPES: tuple[type, ...] = (
    types.FunctionType,
    types.MethodType,
    types.BuiltinFunctionType,
    types.WrapperDescriptorType,
    types.MethodWrapperType,
    types.MethodDescriptorType,
    types.ClassMethodDescriptorType,
)
MAX_RECURSIVE_RENDER_OBJLEVEL = 10
DispatchPredCallback = Callable[[object], bool]

T = TypeVar("T")

__all__ = ["NEVER_RENDER_TYPES", "T"]
