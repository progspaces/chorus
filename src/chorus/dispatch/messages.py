from dataclasses import dataclass, field
from typing import Any

from .exchange import ExchangeMessage, Message


@dataclass
class Call(ExchangeMessage):
    name: str
    args: tuple[Any, ...] = ()
    kwargs: dict[str, Any] = field(default_factory=dict)
    reply: bool = False


@dataclass
class Success(ExchangeMessage):
    result: Any


@dataclass
class Error(ExchangeMessage):
    reason: Any


@dataclass
class Kill(Message):
    pass
