"""
dhlibs.reprfmt
Generic and advanced representation (__repr__) functions,
formatters for Python objects.
"""

from dhlibs.reprfmt.core import format_repr
from dhlibs.reprfmt.deco import put_repr
from dhlibs.reprfmt.utils import register_formatter

__all__ = ["format_repr", "put_repr", "register_formatter"]
