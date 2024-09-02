# This file is part of dhlibs (https://github.com/DinhHuy2010/dhlibs)
#
# MIT License
#
# Copyright (c) 2024 DinhHuy2010 (https://github.com/DinhHuy2010)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""dhlibs.alias_callable - very simple module to create aliased callables"""

from functools import wraps

from typing_extensions import Callable, Optional, ParamSpec, TypeVar

P = ParamSpec("P")
T = TypeVar("T")


def alias_callable(
    callback: Callable[P, T],
    name: str,
    qualname: Optional[str] = None,
    doc: Optional[str] = None,
) -> Callable[P, T]:
    if not callable(callback):
        raise TypeError("'callback' is not callable")

    @wraps(callback)
    def _(*args: P.args, **kwargs: P.kwargs) -> T:
        return callback(*args, **kwargs)

    _.__name__ = name
    if qualname is None:
        t = callback.__qualname__[:]
        _.__qualname__ = ".".join([*t.split(".")[:-1], name])
    else:
        _.__qualname__ = qualname
    if doc is not None:
        _.__doc__ = doc
    return _
