from typing import Any

from chorus.runtime.system import ActorID

from .exchange import ask, tell
from .messages import Call, Error, Kill, Success


class Teller:
    def __init__(self, target_id: ActorID):
        self.target_id = target_id

    def __getattr__(self, name: str) -> Any:
        def missing(*args: Any, **kwargs: Any) -> Any:
            message = Call(name=name, args=args, kwargs=kwargs, reply=False)
            tell(self.target_id, message)

        return missing


class Asker:
    def __init__(self, target_id: ActorID):
        self.target_id = target_id

    def __getattr__(self, name: str) -> Any:
        def missing(*args: Any, **kwargs: Any) -> Any:
            request = Call(name=name, args=args, kwargs=kwargs, reply=True)
            response = ask(self.target_id, request)
            match response:
                case Success(result):
                    return result
                case Error(reason):
                    raise reason
                case _:
                    raise TypeError(f"Unexpected call response: {response!r}")

        return missing


class Proxy:
    def __init__(self, target_id: ActorID):
        self.target_id = target_id
        self.teller = Teller(target_id)
        self.asker = Asker(target_id)
        # TODO: pass the timeout in here

    @property
    def tell(self) -> Teller:
        return self.teller

    @property
    def ask(self) -> Asker:
        return self.asker

    def kill(self) -> None:
        tell(self.target_id, Kill())
