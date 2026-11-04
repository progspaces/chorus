import itertools
from typing import Any

from ..runtime.api import me, receive, send
from ..runtime.system import ActorID
from .messages import Message, Request, Response

next_exchange_id = itertools.count(1)


def make_exchange_id() -> int:
    return next(next_exchange_id)


def tell(id: ActorID, message: Message) -> None:
    message.sender = me()
    send(id, message)


def ask(id: ActorID, request: Request, timeout: float | None = None) -> Response:
    request.sender = me()
    request.exchange_id = make_exchange_id()
    send(id, request)

    def match_id(msg: Any) -> bool:
        return isinstance(msg, Response) and msg.exchange_id == request.exchange_id

    response: Response = receive(match_id, timeout=timeout)
    return response
