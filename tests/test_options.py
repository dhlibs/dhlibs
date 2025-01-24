from __future__ import annotations

import pytest

from dhlibs.options import Options


@pytest.fixture(scope="session")
def common_opts():
    opts = Options(a=1, b=2, c=Options({"a": -1.2j}))
    return opts


def test_options(common_opts: Options):
    opts = common_opts.copy()
    assert opts.get("a") == 1
    assert opts.get("b") == 2
    assert opts.get("c") == Options({"a": -1.2j})
    assert opts.get("c.a") == -1.2j
    with pytest.raises(KeyError):
        assert opts.get("d")
    with pytest.raises(KeyError):
        assert opts.get("d.e.f")
    assert opts.get("d", None) is None
    assert opts.get("d.e.f", None) is None
    opts.set("e", Options())
    opts.set("e.d", 2)
    assert opts.delete("e.d") == 2
    with pytest.raises(KeyError):
        assert opts.delete("e.e")
    with pytest.raises(KeyError):
        assert opts.delete("e.e.a.b")
    with pytest.raises(KeyError):
        assert opts.set("e.e.a.b", None)
    assert opts.delete("e.f", None) is None


def test_options_eq(common_opts: Options):
    other = Options(a=1, b=2, c=Options({"a": -1.2j}))
    assert common_opts != 0
    assert common_opts == other


def test_options_repr(common_opts: Options):
    opts = common_opts.copy()
    opts.set("e", Options())
    assert repr(opts) == "Options(a=1, b=2, c=Options(a=(-0-1.2j)), e=Options())"
