# This file is part of dhlibs (https://github.com/DinhHuy2010/dhlibs)
# Copyright (c) 2024 DinhHuy2010 (https://github.com/DinhHuy2010)
# SPDX-License-Identifier: MIT OR Apache-2.0 OR MPL-2.0

from __future__ import annotations

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
        alias_callable("not_a_function", "alias_function")  # type: ignore
