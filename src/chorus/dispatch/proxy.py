from abc import ABC, abstractmethod
from typing import Any

from ..runtime.system import ActorID
from ..messaging.exchange import ask, tell
from .messages import Call, Invoke, Kill, Raise, Return


class Dispatcher(ABC):
    @abstractmethod
    def dispatch(self, name: str, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError()

    def __getattr__(self, name: str):
        def missing(*args: Any, **kwargs: Any):
            return self.dispatch(name, *args, **kwargs)

        return missing


class Teller(Dispatcher):
    def __init__(self, target_id: ActorID):
        self.target_id = target_id

    def dispatch(self, name: str, *args: Any, **kwargs: Any) -> None:
        event = Invoke(name=name, args=args, kwargs=kwargs)
        tell(self.target_id, event)


class Asker(Dispatcher):
    def __init__(self, target_id: ActorID):
        self.target_id = target_id

    def dispatch(self, name: str, *args: Any, **kwargs: Any) -> Any:
        request = Call(name=name, args=args, kwargs=kwargs)
        response = ask(self.target_id, request)
        match response:
            case Return(result):
                return result
            case Raise(reason):
                raise reason
            case _:
                raise TypeError(f"Unexpected call response: {response!r}")


class Proxy:
    def __init__(self, target_id: ActorID):
        self.target_id = target_id
        self.teller = Teller(target_id)
        self.asker = Asker(target_id)

    @property
    def tell(self):
        return self.teller

    @property
    def ask(self):
        return self.asker

    def kill(self):
        tell(self.target_id, Kill())
