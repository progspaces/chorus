from typing import Any

from ..kernel.actor import ActorID, me, receive, send
from .messages import End, Error, Request, Response, make_request_id


def tell(id: ActorID, name: str, *args, **kwargs) -> Any:
    request_id = make_request_id()
    request = Request(
        request_id=request_id, sender=me(), name=name, args=args, kwargs=kwargs
    )
    send(id, request)


def ask(id: ActorID, name: str, *args, **kwargs) -> Any:
    request_id = make_request_id()
    request = Request(
        request_id=request_id, sender=me(), name=name, args=args, kwargs=kwargs
    )
    send(id, request)

    def match_id(msg: Any) -> bool:
        return isinstance(msg, (Response, Error)) and msg.request_id == request_id

    response = receive(match_id)
    match response:
        case Response(_, _, result):
            return result
        case Error(_, _, reason):
            raise RuntimeError(reason)


def kill(id: ActorID) -> None:
    send(id, End())
