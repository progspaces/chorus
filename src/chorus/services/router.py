from typing import Any

from ..actors.api import ActorUnavailableException, me, receive, send, spawn
from ..actors.system import ActorID
from ..protocol.messages import (
    Call,
    End,
    Error,
    Request,
    Response,
)
from .proxy import Proxy


def invoke(handler: object | list[object], message: Call | Request) -> Any:
    """Invoke the first callable match, searching handler lists in order.

    Once a method matches, its result or exception ends dispatch.
    """
    handlers = handler if isinstance(handler, list) else [handler]
    for candidate in handlers:
        method = getattr(candidate, message.name, None)
        if callable(method):
            return method(*message.args, **message.kwargs)
    raise AttributeError(f"Method: '{message.name}' missing on handler.")


def route_call(message: Call, handler: object | list[object]) -> None:
    try:
        invoke(handler, message)
    except Exception as e:
        print(f"Unable to route call: {message}.")
        print(e)
        return


def deliver_response(target_id: ActorID, response: Response | Error):
    try:
        send(target_id, response)
    except ActorUnavailableException as e:
        print(
            f"The actor that sent the message is no longer availible. ID is {e.actor_id}"
        )


def route_request(message: Request, handler: object | list[object]) -> None:
    try:
        result = invoke(handler, message)
    except Exception as e:
        response: Response | Error = Error(
            request_id=message.request_id,
            sender=me(),
            reason=f"Handler failed for message: {message.name}",
            exception=e,
        )
    else:
        response = Response(request_id=message.request_id, sender=me(), result=result)

    deliver_response(message.sender, response)


def handle_all_messages(handlers: object | list[object]) -> None:
    """Route all messages currently in the mailbox to the first matching handler.

    Args:
        handlers: A single handler or a list searched in order for a callable
            matching the message name. Errors in a matching method do not fall
            through to later handlers.
    """
    should_check_for_messages = True
    while should_check_for_messages:
        message = receive(block=False)
        match message:
            case Call():
                route_call(message, handlers)
            case Request():
                route_request(message, handlers)
            case End():
                print(f"Actor: {me()} recieved End message.")
                # TODO: it's not clear what to do here is
                # raise ActorKilledException()
            case None:
                # receive will return None when there are no messages
                should_check_for_messages = False
            case _:
                print(f"Cannot route unknowns message: {message}")


def spawn_with_proxy(handler: object | list[object]) -> Proxy:
    """Spawn an actor routing messages to the first matching handler.

    Args:
        handler: A single handler or a list searched in order for a callable
            matching the message name. Errors in a matching method do not fall
            through to later handlers.

    Returns:
        Proxy: A proxy to the actor.
    """

    def actor_func():
        running = True
        while running:
            message = receive()
            match message:
                case Call():
                    route_call(message, handler)
                case Request():
                    route_request(message, handler)
                case End():
                    running = False
                case _:
                    print(f"Cannot route unknowns message: {message}")

    actor_id = spawn(actor_func)
    return Proxy(actor_id)
