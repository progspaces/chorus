"""Main actor API: spawn actors, send and receive messages, and get actor identity."""

from typing import Any, Callable

from .system import ActorFunction, ActorID, ActorSystem, thread_context


def spawn[**P](target: ActorFunction[P], *args: P.args, **kwargs: P.kwargs) -> ActorID:
    """Spawn a new actor.

    Args:
        target (ActorFunction): The function to run in the actor.

    Returns:
        ActorID: The id of the new actor.
    """
    return thread_context.actor.system.run(target, *args, **kwargs)


def send(actor_id: ActorID, message: Any) -> None:
    """Send an actor a message.

    Messages can be of any type. Convention is strings or tuples.
    String if the messages have no arguments.
    Tuples if they have arguments.

    Args:
        id (ActorID): The id of the target actor.
        message (Any): The message to send.

    Raises:
        ActorNotFoundError: if the actor is not present in the system.
    """
    actor = thread_context.actor.system.get_actor_record(actor_id)
    actor.mailbox.put(message)


def receive(
    predicate: Callable[[Any], bool] | None = None,
    block: bool = True,
    timeout: float | None = None,
) -> Any:
    """Recieve the next message in the mailbox.

    Blocks and waits until there is a message in the mailbox then gets it.

    Returns:
        Any: The next message in the mailbox.
    """
    return thread_context.actor.mailbox.get(predicate, block, timeout)


def me() -> ActorID:
    """Get the id of the current actor.

    Equivalent to self in Erlang.

    Returns:
        ActorID: The id of the current actor.
    """
    return thread_context.actor.id


def terminate(actor_id: ActorID) -> None:
    thread_context.actor.system.terminate(actor_id)


def print_actors() -> None:
    thread_context.actor.system.print_actors()


def add_to_local(actor_id: ActorID, key: str, value: Any) -> None:
    thread_context.actor.system.add_to_local(actor_id, key, value)


def get_from_local(actor_id: ActorID, key: str) -> Any:
    return thread_context.actor.system.get_from_local(actor_id, key)


def get_actor_system() -> ActorSystem:
    return thread_context.actor.system
