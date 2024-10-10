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

from dhlibs.indices import GotInfiniteRange, NoRangeFound, OutOfRange, indices

JSON_DATA = {
    "slice": {"type": "slice", "slice": {"start": 0, "stop": 2, "step": 1}},
    "ref": {
        "slice": {"type": "indexes", "values": [1, 3, 5, 7]},
        "ref": {
            "slice": {"type": "indexes", "values": [10, 20, 40, 50, 80, 120, 150]},
            "ref": {
                "slice": {
                    "type": "slice",
                    "slice": {"start": 0, "stop": 5000, "step": 10},
                }
            },
        },
    },
}


def test_empty_range():
    a = indices(())
    assert len(list(a)) == 0


def test_simple_range():
    b = indices(10)
    assert list(b) == list(range(10))
    assert len(b) == 10
    assert b.get(0) == 0
    assert b.get(9) == 9
    with pytest.raises(OutOfRange):
        b.get(10)


def test_step_range():
    c = indices(stop=10, step=2)
    assert list(c) == [0, 2, 4, 6, 8]
    assert len(c) == 5
    assert c.get(2) == 4
    assert c.get(-1) == 8
    with pytest.raises(OutOfRange):
        c.get(5)


def test_slice_range():
    d = indices(slice(2, 100, 10))
    assert list(d) == list(range(2, 100, 10))
    assert len(d) == len(list(range(2, 100, 10)))
    assert d.get(0) == 2
    assert d.get(-1) == 92


def test_large_step_range():
    e = indices(start=10, stop=1000, step=20)
    assert list(e[:5]) == [10, 30, 50, 70, 90]
    assert len(e) == 50
    assert e.get(0) == 10
    assert e.get(24) == 490
    assert e.get(-1) == 990
    with pytest.raises(OutOfRange):
        e.get(50)


def test_infinite_range():
    f = indices(start=10, step=20)
    assert list(f[:5]) == [10, 30, 50, 70, 90]
    assert f[::2].get(100) == 4010
    assert f[::1][10] == 210
    with pytest.raises(GotInfiniteRange):
        len(f)
    with pytest.raises(GotInfiniteRange):
        f.get(-1)
    with pytest.raises(GotInfiniteRange):
        next(f[::-1])
    with pytest.raises(GotInfiniteRange):
        f.reverse()


def test_reverse_range():
    b = indices(10)
    r = b.reverse()
    assert list(r) == list(reversed(range(10)))
    e = indices(start=10, stop=1000, step=20)
    er = e.reverse()
    assert list(er) == list(reversed(range(10, 1000, 20)))


def test_indices_subrange():
    e = indices(start=10, stop=100, step=10)
    subrange = e.indices(slice(1, 4))
    assert list(subrange) == [20, 30, 40]

def test_indices_subrange_advanced():
    e = indices(start=10, stop=100, step=10)
    subrange = e.indices(slice(1, None, 2))
    assert list(subrange[:3]) == [20, 40, 60]
    assert list(subrange[:20][:3]) == [20, 40, 60]

def test_getitem_fail():
    e = indices()
    with pytest.raises(TypeError):
        e[None] # type: ignore

def test_contains():
    e = indices(start=10, stop=100, step=10)
    assert 50 in e
    assert 55 not in e


def test_len_errors():
    f = indices(start=10, step=20)
    with pytest.raises(GotInfiniteRange, match="cannot compute length of an infinite range"):
        len(f)


def test_get_errors():
    e = indices(10)
    with pytest.raises(OutOfRange, match="index out of range"):
        e.get(11)


def test_slice_property():
    e = indices(start=10, stop=100, step=10)
    assert e.slice == slice(10, 100, 10)


def test_copy():
    e = indices(start=10, stop=100, step=10)
    copy_e = e.copy()
    assert list(e) == list(copy_e)
    assert e is not copy_e


def test_eq_indices():
    a = indices()
    b = indices()
    assert a == b


def test_advanced_eq_indices():
    a = indices()
    b = a[:5000:10]
    c = b[10, 20, 40, 50, 80, 120, 150]
    d = c[1, 3, 5, 7]
    e = d[:2]
    b = indices()
    b2 = b[:5000:10]
    c2 = b2[10, 20, 40, 50, 80, 120, 150]
    d2 = c2[1, 3, 5, 7]
    e2 = d2[:2]
    assert e != b
    assert e == e2
    assert e.reference is not None and e.reference == d
    assert e2.reference is not None and e2.reference == d2


def test_ne_indices():
    a = indices()
    b = indices(10)
    assert a != b


def test_gt_indices():
    a = indices(1000)
    b = indices(100)
    assert a > b


def test_ge_indices_equal():
    a = indices(stop=1000, step=10)
    b = indices(stop=1000, step=10)
    c = indices(stop=1000, step=20)
    assert a >= b
    assert a >= c


def test_lt_indices():
    a = indices(stop=100, step=20)
    b = indices(stop=1000, step=10)
    assert a < b


def test_le_indices_equal():
    a = indices(100)
    b = indices(100)
    assert a <= b


def test_reverse():
    a = indices(100)
    b = a.reverse()
    assert list(b) == list(reversed(a))


def test_tuple():
    a = indices(stop=100, step=2)
    b = a[10, 20, 45]
    assert list(b[:2]) == [20, 40]
    assert b.get(2) == b[2] == 90


def test_tuple_contains():
    a = indices(stop=100, step=2)
    b = a[10, 20, 45]
    assert 40 in b


def test_tuple_reverse():
    a = indices(stop=100, step=2)
    b = a[10, 20, 45].reverse()
    assert b == a[45, 20, 10]
    assert list(b) == list(a[45, 20, 10]) == [90, 40, 20]


def test_tuple_noref():
    a = indices((0, 1, 2))
    with pytest.raises(NoRangeFound):
        list(a)
    with pytest.raises(GotInfiniteRange):
        a[::-1].get(1)


def test_new_slice_impl():
    a = indices()
    b = a[:5000:10]
    c = b[10, 20, 40, 50, 80, 120, 150]
    d = c[1, 3, 5, 7]
    e = d[:2]
    assert list(e) == [200, 500]


def test_for_json():
    a = indices()
    b = a[:5000:10]
    c = b[10, 20, 40, 50, 80, 120, 150]
    d = c[1, 3, 5, 7]
    e = d[:2]
    assert e.for_json() == JSON_DATA


def test_from_json():
    a = indices.from_json(JSON_DATA)
    assert a.for_json() == JSON_DATA
    assert list(a) == [200, 500]
