"""Main actor API: spawn actors, send and receive messages, and get actor identity."""

from collections.abc import Callable
from typing import Any

from .system import ActorFunction, ActorID, ActorSystem, thread_context


def current_system() -> ActorSystem:
    return thread_context.actor.system


def spawn[**P](target: ActorFunction[P], *args: P.args, **kwargs: P.kwargs) -> ActorID:
    """Spawn a new actor.

    Args:
        target: The function to run in the actor.
        args: Positional arguments to be passed to target function.
        kwargs: Keyword arguments to be passed to target function.

    Returns:
        The id of the new actor.
    """
    return current_system().start(target, *args, **kwargs)


def send(actor_id: ActorID, message: Any) -> None:
    """Send an actor a message.

    Messages can be of any type. Convention is strings or tuples.
    String if the messages have no arguments.
    Tuples if they have arguments.

    Args:
        actor_id: The id of the target actor.
        message: The message to send.

    Raises:
        ActorNotFoundError: if the actor is not present in the system.
    """
    actor = current_system().get_actor_record(actor_id)
    actor.mailbox.put(message)


def receive(
    predicate: Callable[[Any], bool] | None = None,
    block: bool = True,
    timeout: float | None = None,
) -> Any:
    """Receive the next message in the mailbox.

    Blocks and waits until there is a message in the mailbox then gets it.

    Args:
        predicate: A condition to use to select a message. Accepts any message by
        default.
        block: Whether to block until there is a message. Defaults to True.
        timeout: How long to block for, in seconds. Blocks indefinitely by default.

    Returns:
        The next message in the mailbox.
    """
    return thread_context.actor.mailbox.get(predicate, block, timeout)


def me() -> ActorID:
    """Return the id of the current actor.

    Equivalent to self in Erlang.
    """
    return thread_context.actor.actor_id


def terminate(actor_id: ActorID) -> None:
    current_system().terminate(actor_id)


def actors_str() -> str:
    return str(current_system())
