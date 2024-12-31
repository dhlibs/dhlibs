# This file is part of dhlibs (https://github.com/DinhHuy2010/dhlibs)
# Copyright (c) 2024 DinhHuy2010 (https://github.com/DinhHuy2010)
# SPDX-License-Identifier: MIT OR Apache-2.0 OR MPL-2.0

from __future__ import annotations

from typing_extensions import Any, Mapping

from dhlibs.alias_callable import alias_callable
from dhlibs.cachedop._typings import AuditCallableType, AuditDefaultDict, AuditEvent, AuditEvents


def _resolve_events(events: AuditEvents) -> list[AuditEvent]:
    out: list[AuditEvent] = []
    if events is None:
        out.extend(getattr(AuditEvent, name) for name in AuditEvent._member_names_)
    elif isinstance(events, AuditEvent):
        out.append(events)
    else:
        out.extend(events)
    return out


class Auditer:
    def __init__(self) -> None:
        self._events = AuditDefaultDict(list)

    def register(self, callback: AuditCallableType, on_events: AuditEvents = None) -> None:
        for event in _resolve_events(on_events):
            self._events[event].append(callback)

    def clear(self, events: AuditEvents) -> None:
        for event in _resolve_events(events):
            self._events[event].clear()

    def audit(self, event: AuditEvent, args: Mapping[str, Any]):
        args = dict(args)
        for callback in self._events[event]:
            callback(event, args)


audit = Auditer()
register_audit_callback = alias_callable(audit.register, "register_audit_callback", qualname="register_audit_callback")
