# This file is part of dhlibs (https://github.com/DinhHuy2010/dhlibs)
# Copyright (c) 2024 DinhHuy2010 (https://github.com/DinhHuy2010)
# SPDX-License-Identifier: MIT OR Apache-2.0 OR MPL-2.0

# pyright: basic
from __future__ import annotations

import operator

import pytest
import typing_extensions

from dhlibs import cachedop
from dhlibs.cachedop._typings import AuditEvent
from dhlibs.cachedop._utils import keymaker
from dhlibs.cachedop.audit import Auditer


@pytest.fixture(name="cached_add")
def add_fixture():
    return cachedop.cached_opfunc(operator.add)


@pytest.fixture(name="auditer")
def auditer_fixture():
    return Auditer()


def test_basic_calc(cached_add):
    assert cached_add(1, 2) == 3
    assert cached_add(1, 2, 3) == 6
    assert cached_add(1, 2, 5, 9) == 1 + 2 + 5 + 9


def test_cache_calls(cached_add):
    info = cached_add.cache_info()
    assert info.size == 0
    cached_add(2, 5)
    info = cached_add.cache_info()
    assert info.size == 1
    assert info.misses == 1
    cached_add(2, 5)
    info = cached_add.cache_info()
    assert info.size == 1
    assert info.hits == 1


def test_keymaker():
    def weird(yes: tuple[int, ...]) -> str:
        return str(yes)

    maker = keymaker(weird, order_matters=True)
    assert maker.make_key((1, 2)) == str((1, 2))
    assert maker.make_key((2, 1)) == str((2, 1))


def test_keymaker_order_is_not_matter():
    def weird(yes: tuple[int, ...]) -> str:
        return str(yes)

    maker = keymaker(weird, order_matters=False)
    assert maker.make_key((1, 2)) == maker.make_key((2, 1)) == str((1, 2))


def test_auditer(auditer):
    calls = 0
    cached_called = 0

    def on_call(event: AuditEvent, args: typing_extensions.Mapping[str, typing_extensions.Any]) -> None:  # noqa: ARG001
        nonlocal calls
        calls += 1

    def on_hits_and_misses(event: AuditEvent, args: typing_extensions.Mapping[str, typing_extensions.Any]) -> None:  # noqa: ARG001
        nonlocal cached_called
        cached_called += 1

    auditer.register(on_call, AuditEvent.CALL)
    auditer.register(on_hits_and_misses, [AuditEvent.HIT, AuditEvent.MISS])
    cached_add = cachedop.cached_opfunc(operator.add, auditer=auditer)
    cached_add(1, 2)
    cached_add(1, 2)
    assert calls == 1
    assert cached_called == 2
