import itertools
from typing import Any

from ..runtime.api import me, receive, send
from ..runtime.system import ActorID
from .messages import Event, Request, Response

next_exchange_id = itertools.count(1)


def make_exchange_id() -> int:
    return next(next_exchange_id)


def tell(id: ActorID, event: Event) -> None:
    event.sender = me()
    send(id, event)


def ask(id: ActorID, request: Request, timeout: float | None = None) -> Response:
    request.sender = me()
    request.exchange_id = make_exchange_id()
    send(id, request)

    def match_id(msg: Any) -> bool:
        # todo: there is a type checking issue but I don't know how to fix it
        return isinstance(msg, Response) and msg.exchange_id == request.exchange_id

    return receive(match_id, timeout=timeout)
