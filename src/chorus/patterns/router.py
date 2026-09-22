from typing import Any

from ..kernel.actor import me, receive, send, spawn
from .messages import (
    End,
    Error,
    Request,
    Response,
)
from .proxy import Proxy


def route(req: Request, handler: Any) -> None:
    """Take a request and dispatch it to a handler.

    Args:
        req (Request): The request message to dispatch.
        handler (Any): The handler object to call the methods of.
    """
    method = getattr(handler, req.name, None)
    if callable(method):
        result = method(*req.args, *req.kwargs)
        res = Response(req.request_id, me(), result)
        return send(req.sender, res)

    # fall through for error
    reason = f"Request could not be routed on object: {handler}"
    error = Error(req.request_id, me(), reason)
    send(req.sender, error)


def spawn_with_proxy(handler: Any) -> Proxy:
    """Spawns a new actor, routes all the messages to the handler object, and returns a Proxy.

    Args:
        handler (Any): The handler object.

    Returns:
        Proxy: A proxy to the actor.
    """

    def actor_func():
        running = True
        while running:
            message = receive()
            match message:
                case Request():
                    route(message, handler)
                case End():
                    running = False
                case _:
                    print(f"Unknown message: {message}")

    actor_id = spawn(actor_func)
    return Proxy(actor_id)
