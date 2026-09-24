from abc import ABC, abstractmethod
from typing import Any

from ..actors.system import ActorID
from ..protocol.calls import ask, kill, tell


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
        tell(self.target_id, name, *args, **kwargs)


class Asker(Dispatcher):
    def __init__(self, target_id: ActorID):
        self.target_id = target_id

    def dispatch(self, name: str, *args: Any, **kwargs: Any) -> Any:
        return ask(self.target_id, name, *args, **kwargs)


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
        kill(self.target_id)
