from dataclasses import dataclass, field
from typing import Any

from ..messaging.messages import Message, Request, Response


@dataclass
class Invoke(Message):
    name: str
    args: tuple[Any, ...] = ()
    kwargs: dict[str, Any] = field(default_factory=dict)


@dataclass
class Call(Request):
    name: str
    args: tuple[Any, ...] = ()
    kwargs: dict[str, Any] = field(default_factory=dict)


@dataclass
class Success(Response):
    result: Any


@dataclass
class Error(Response):
    reason: Any


@dataclass
class Kill(Message):
    pass
