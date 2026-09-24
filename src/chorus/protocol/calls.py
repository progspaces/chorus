from typing import Any

from ..actors.api import me, receive, send
from ..actors.system import ActorID
from .messages import Call, End, Error, Request, Response, make_request_id


def tell(id: ActorID, name: str, *args: Any, **kwargs: Any) -> None:
    """_summary_

    Args:
        id (ActorID): The id of the actor to send the message to.
        name (str): The name of the message.

    args and kwargs are used for the corresponding fields in the Call message.

    Raises:
        ActorUnavailableException if the actor id is not in the system.

    Returns:
        Any: _description_
    """
    request_id = make_request_id()
    request = Call(
        request_id=request_id, sender=me(), name=name, args=args, kwargs=kwargs
    )
    send(id, request)


def ask(id: ActorID, name: str, *args: Any, **kwargs: Any) -> Any:
    ask_with_timeout(id, name, 0.0, *args, **kwargs)


def ask_with_timeout(
    id: ActorID, name: str, timeout: float = 0.0, /, *args: Any, **kwargs: Any
) -> Any:
    request_id = make_request_id()
    request = Request(
        request_id=request_id, sender=me(), name=name, args=args, kwargs=kwargs
    )
    send(id, request)

    def match_id(msg: Any) -> bool:
        return isinstance(msg, (Response, Error)) and msg.request_id == request_id

    response = receive(match_id, timeout=timeout)
    match response:  # TODO: work out how to fix this
        case Response(_, _, result):
            return result
        case Error(_, _, reason, exception):
            if exception:
                raise exception
            else:
                raise RuntimeError(reason)
        case _:
            print(f"Unknown message returned from ask: {response}")


def kill(id: ActorID) -> None:
    send(id, End())
