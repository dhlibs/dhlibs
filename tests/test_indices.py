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

from dhlibs.indices import indices as indices_range


def test_empty_range():
    a = indices_range(())
    assert len(list(a)) == 0


def test_simple_range():
    b = indices_range(10)
    assert list(b) == list(range(10))
    assert len(b) == 10
    assert b.get(0) == 0
    assert b.get(9) == 9
    with pytest.raises(IndexError):
        b.get(10)


def test_step_range():
    c = indices_range(stop=10, step=2)
    assert list(c) == [0, 2, 4, 6, 8]
    assert len(c) == 5
    assert c.get(2) == 4
    assert c.get(-1) == 8
    with pytest.raises(IndexError):
        c.get(5)


def test_slice_range():
    d = indices_range(slice(2, 100, 10))
    assert list(d) == list(range(2, 100, 10))
    assert len(d) == len(list(range(2, 100, 10)))
    assert d.get(0) == 2
    assert d.get(-1) == 92


def test_large_step_range():
    e = indices_range(start=10, stop=1000, step=20)
    assert list(e[:5]) == [10, 30, 50, 70, 90]
    assert len(e) == 50
    assert e.get(0) == 10
    assert e.get(24) == 490
    assert e.get(-1) == 990
    with pytest.raises(IndexError):
        e.get(50)


def test_infinite_range():
    f = indices_range(start=10, step=20)
    assert list(f[:5]) == [10, 30, 50, 70, 90]
    with pytest.raises(ValueError):
        len(f)
    with pytest.raises(IndexError):
        f.get(-1)


def test_reverse_range():
    b = indices_range(10)
    r = b.reverse()
    assert list(r) == list(reversed(range(10)))
    e = indices_range(start=10, stop=1000, step=20)
    er = e.reverse()
    assert list(er) == list(reversed(range(10, 1000, 20)))


def test_indices_subrange():
    e = indices_range(start=10, stop=100, step=10)
    subrange = e.indices(slice(1, 4))
    assert list(subrange) == [20, 30, 40]


def test_contains():
    e = indices_range(start=10, stop=100, step=10)
    assert 50 in e
    assert 55 not in e


def test_len_errors():
    f = indices_range(start=10, step=20)
    with pytest.raises(ValueError, match="cannot compute length of an infinite range"):
        len(f)


def test_get_errors():
    e = indices_range(10)
    with pytest.raises(IndexError, match="index out of range"):
        e.get(11)


def test_slice_property():
    e = indices_range(start=10, stop=100, step=10)
    assert e.slice == slice(10, 100, 10)


def test_copy():
    e = indices_range(start=10, stop=100, step=10)
    copy_e = e.copy()
    assert list(e) == list(copy_e)
    assert e is not copy_e
