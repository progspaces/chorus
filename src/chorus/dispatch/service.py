from chorus.dispatch.dispatcher import Dispatcher
from chorus.dispatch.proxy import Proxy
from chorus.runtime.api import spawn


def spawn_service(*args: object) -> Proxy:
    def actor_func() -> None:
        Dispatcher(list(args)).loop()

    actor_id = spawn(actor_func)
    return Proxy(actor_id)
