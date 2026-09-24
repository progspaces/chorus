import itertools
from dataclasses import dataclass
from typing import Any, Tuple

from ..actors.system import ActorID

next_request_id = itertools.count(1)


def make_request_id() -> int:
    """Generate a new unique id for a request-response communication.

    Returns:
        int: The id, which is just an int.
    """
    return next(next_request_id)


# standard message classes
@dataclass
class Call:  # monologue
    """A call is a one way message.
    It does not expect a response."""

    request_id: int
    sender: ActorID
    name: str
    args: Tuple[Any, ...]
    kwargs: dict[str, Any]


@dataclass
class Request:  # dialogue
    """A request is the start of a two way message.
    It does expect a response."""

    request_id: int
    sender: ActorID
    name: str
    args: Tuple[Any, ...]
    kwargs: dict[str, Any]


@dataclass
class Response:
    """A response is the end of a two way message."""

    request_id: int
    sender: ActorID
    result: Any


@dataclass
class Error:
    """The response from a request might also be an error."""

    request_id: int
    sender: ActorID
    reason: str
    exception: Exception | None = None


@dataclass
class End:
    pass
