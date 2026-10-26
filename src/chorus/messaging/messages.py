from dataclasses import dataclass, field

from ..runtime.system import ActorID


@dataclass
class Message:
    sender: ActorID = field(init=False)


@dataclass
class Event(Message):
    pass


@dataclass
class Request(Message):
    exchange_id: int = field(init=False)


@dataclass
class Response(Message):
    exchange_id: int = field(kw_only=True)
