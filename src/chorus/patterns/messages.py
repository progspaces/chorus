import itertools
from dataclasses import dataclass
from typing import Any, Tuple

from ..kernel.actor import ActorID

next_request_id = itertools.count(1)


def make_request_id() -> int:
    return next(next_request_id)


# standard message classes
@dataclass
class Request:
    request_id: int
    sender: ActorID
    name: str
    args: Tuple[Any, ...]
    kwargs: dict[str, Any]


@dataclass
class Response:
    request_id: int
    sender: ActorID
    result: Any


@dataclass
class Error:
    request_id: int
    sender: ActorID
    reason: str


@dataclass
class End:
    pass
