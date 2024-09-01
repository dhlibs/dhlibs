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

import pytest

from dhlibs.alias_callable import alias_callable


def example_function(a: int, b: int) -> int:
    """This is an example function."""
    return a + b

def test_alias_creation():
    # Create an alias for example_function
    alias = alias_callable(example_function, "alias_function", doc="This is an alias function.")
    
    # Check alias name
    assert alias.__name__ == "alias_function"
    
    # Check alias qualified name
    expected_qualname = ".".join(example_function.__qualname__.split(".")[:-1] + ["alias_function"])
    assert alias.__qualname__ == expected_qualname

    # Check alias docstring
    assert alias.__doc__ == "This is an alias function."

def test_alias_functionality():
    # Create an alias for example_function
    alias = alias_callable(example_function, "alias_function")
    
    # Check that the alias calls the original function correctly
    assert alias(2, 3) == example_function(2, 3)
    assert alias(5, 7) == example_function(5, 7)

def test_non_callable_error():
    # Test TypeError is raised if callback is not callable
    with pytest.raises(TypeError, match="'callback' is not callable"):
        alias_callable("not_a_function", "alias_function") # type: ignore
