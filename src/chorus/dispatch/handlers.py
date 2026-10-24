import inspect
from typing import Any

from ..messaging import tell
from ..runtime import receive, spawn
from .messages import Call, Invoke, Kill, Raise, Return
from .proxy import Proxy

# The router works by getting a Invoke or Call message and finding an object in a
# chain that can accept that message as a method call.
# In the case of a Call, it then sends a response

# the chain is a list of objects, refered to as handlers


def can_handle(
    handler: object, name: str, args: tuple[Any, ...], kwargs: dict[str, Any]
) -> bool:
    method = getattr(handler, name, None)

    if not callable(method):
        return False

    try:
        inspect.signature(method).bind(*args, **kwargs)
        return True
    except TypeError, ValueError:
        return False


def find_handler(
    handlers: list[object], name: str, args: tuple[Any, ...], kwargs: dict[str, Any]
) -> object | None:
    for handler in handlers:
        if can_handle(handler, name, args, kwargs):
            return handler  # stops on the first one that can handle
    return None


def dispatch(
    handlers: list[object], name: str, args: tuple[Any, ...], kwargs: dict[str, Any]
) -> Any:
    handler = find_handler(handlers, name, args, kwargs)
    if handler:
        method = getattr(handler, name)  # default omitted as method is there
        return method(*args, **kwargs)
    else:
        raise ValueError("Cannot find a handler to dispatch the method on.")


def dispatch_invoke(message: Invoke, handlers: list[object]) -> None:
    try:
        dispatch(handlers, message.name, message.args, message.kwargs)
    except Exception as e:
        print(f"Unable to route Invoke: {message}.")
        print(e)


def dispatch_call(message: Call, handlers: list[object]) -> None:
    try:
        result = dispatch(handlers, message.name, message.args, message.kwargs)
        reply = Return(result)
        reply.exchange_id = message.exchange_id
        tell(message.sender, reply)
    except Exception as reason:
        error = Raise(reason)
        error.exchange_id = message.exchange_id
        tell(message.sender, error)


def process_messages(handlers: list[object], keep_running=False) -> bool:
    # todo - I am unsure thow to handle timeouts here
    # currently the receive will just block forever or not block
    while True:
        message = receive(block=keep_running)
        match message:
            case Invoke():
                dispatch_invoke(message, handlers)
            case Call():
                dispatch_call(message, handlers)
            case Kill():
                # this exits the loop and returns False
                # meaning that the actor should terminate
                return False
            case None:
                # this can only happen when block is false
                # it tells any outer event-loop that the queue has been
                # processed successfully
                return True
            case _:
                print(f"Cannot route unknowns message: {message}")


def server(handlers: list[object]):
    process_messages(handlers, keep_running=True)


def process_pending(handlers: list[object]):
    return process_messages(handlers, keep_running=False)


def spawn_server_with_proxy(handlers: list[object]) -> Proxy:
    actor_id = spawn(server, handlers)
    return Proxy(actor_id)
