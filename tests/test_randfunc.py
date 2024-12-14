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

from __future__ import annotations

import random

import pytest

from dhlibs.randfunc import NoNewValueFound, make_rf_unique


@pytest.fixture(autouse=True)
def set_random_seed():
    random.seed(42)  # Set the seed for all tests in this file

def test_make_rf_unique():
    """Test `make_rf_unique` as a decorator."""

    @make_rf_unique(tries=15)
    def random_func() -> int:
        return random.randint(0, 10)

    seen: set[int] = set()
    for _ in range(11):  # 11 unique integers, range 0-10
        result = random_func()
        assert result not in seen  # Ensure uniqueness.
        seen.add(result)

    with pytest.raises(NoNewValueFound):
        random_func()  # Exhausted all possible unique values.


def test_make_rf_unique_with_arguments():
    """Test `make_rf_unique` with a callable accepting arguments."""

    @make_rf_unique(tries=20)
    def add_offset(x: int, offset: int = 0) -> int:
        return x + offset

    unique_adder = add_offset

    seen: set[int] = set()
    for i in range(20):  # Create 20 unique results based on the input arguments.
        result = unique_adder(10, i)
        assert result not in seen
        seen.add(result)

    # Deliberately force a collision by reusing arguments.
    with pytest.raises(NoNewValueFound):
        unique_adder(10, 5)


def test_clear_memo():
    """Test `clear_memo` functionality."""

    @make_rf_unique(tries=20)
    def random_func() -> int:
        return random.randint(0, 10)

    seen: set[int] = set()
    for _ in range(11):  # Exhaust all unique values.
        result = random_func()
        seen.add(result)

    with pytest.raises(NoNewValueFound):
        random_func()  # No values left.

    random_func.clear_memo()  # Clear the memoization.

    seen_after_clear: set[int] = set()
    for _ in range(11):  # Generate all unique values again.
        result = random_func()
        seen_after_clear.add(result)

    assert seen == seen_after_clear  # Verify values match post-clear.


def test_memo_info():
    """Test `memo_info` correctness."""

    @make_rf_unique
    def random_func() -> int:
        return random.randint(0, 10)

    for _ in range(5):  # Generate 5 unique values.
        random_func()

    info = random_func.memo_info()
    assert info.size == 5  # Memoized 5 values.
    assert info.hits == 0  # No duplicates encountered yet.
    assert info.misses == 5  # Each call produced a unique value.


def test_invalid_callable():
    """Test behavior when an invalid callable is provided."""
    with pytest.raises(TypeError):
        _ = make_rf_unique("not_a_function")  # type: ignore


def test_invalid_tries_value():
    """Test behavior when an invalid tries value is provided."""
    def dummy_func(x: int) -> int:
        return x

    with pytest.raises(ValueError):
        _ = make_rf_unique(tries=0)(dummy_func)