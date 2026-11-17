import itertools
from dataclasses import dataclass, field
from typing import Any

from ..runtime.api import me, receive, send
from ..runtime.system import ActorID

next_exchange_id = itertools.count(1)


@dataclass
class Message:
    sender: ActorID = field(init=False)


@dataclass
class ExchangeMessage(Message):
    exchange_id: int = field(init=False)


def make_exchange_id() -> int:
    return next(next_exchange_id)


def tell(id: ActorID, message: Message) -> None:
    message.sender = me()
    send(id, message)


def ask(
    id: ActorID, request: ExchangeMessage, timeout: float | None = None
) -> ExchangeMessage:
    request.sender = me()
    request.exchange_id = make_exchange_id()
    send(id, request)

    def match_id(msg: Any) -> bool:
        return (
            isinstance(msg, ExchangeMessage) and msg.exchange_id == request.exchange_id
        )

    response: ExchangeMessage = receive(match_id, timeout=timeout)
    return response
