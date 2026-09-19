from abc import ABC, abstractmethod
from typing import Any

from chorus import ActorID, ask, kill, tell


class Dispatcher(ABC):
    @abstractmethod
    def dispatch(self, name, *args, **kwargs) -> Any:
        raise NotImplementedError()

    def __getattr__(self, name):
        def missing(*args, **kwargs):
            return self.dispatch(name, *args, **kwargs)

        return missing


class Teller(Dispatcher):
    def __init__(self, target_id: ActorID):
        self.target_id = target_id

    def dispatch(self, name, *args, **kwargs) -> Any:
        return tell(self.target_id, name, *args, **kwargs)


class Asker(Dispatcher):
    def __init__(self, target_id: ActorID):
        self.target_id = target_id

    def dispatch(self, name, *args, **kwargs) -> Any:
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
