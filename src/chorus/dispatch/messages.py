from dataclasses import dataclass, field
from typing import Any

from ..messaging.messages import Error, Event, Request, Success


@dataclass
class Invoke(Event):
    name: str
    args: tuple[Any, ...] = ()
    kwargs: dict[str, Any] = field(default_factory=dict)


@dataclass
class Call(Request):
    name: str
    args: tuple[Any, ...] = ()
    kwargs: dict[str, Any] = field(default_factory=dict)


@dataclass
class Return(Success):
    result: Any


@dataclass
class Raise(Error):
    reason: Any


@dataclass
class Kill(Event):
    pass
