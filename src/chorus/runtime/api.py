"""Main actor API: spawn actors, send and receive messages, and get actor identity."""

from typing import Any, Callable

from .system import ActorFunction, ActorID, thread_context


def spawn[**P](target: ActorFunction[P], *args: P.args, **kwargs: P.kwargs) -> ActorID:
    """Spawn a new actor.

    Args:
        target (ActorFunction): The function to run in the actor.

    Returns:
        ActorID: The id of the new actor.
    """
    aid: ActorID = thread_context.actor.system.run(target, *args, **kwargs)
    return aid


class ActorUnavailableException(Exception):
    def __init__(self, actor_id: ActorID, message: Any) -> None:
        super().__init__()
        self.actor_id = actor_id
        self.message = message


def send(id: ActorID, message: Any) -> None:
    """Send an actor a message.

    Messages can be of any type. Convention is strings or tuples.
    String if the messages have no arguments.
    Tuples if they have arguments.

    Args:
        id (ActorID): The id of the target actor.
        message (Any): The message to send.
    """
    actors = thread_context.actor.system.actors
    try:
        target = actors[id]
    except KeyError:
        raise ActorUnavailableException(id, message)
    else:
        target.mailbox.put(message)


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
    mailbox = thread_context.actor.mailbox
    return mailbox.get(predicate, block, timeout)


def me() -> ActorID:
    """Get the id of the current actor.

    Equivalent to self in Erlang.

    Returns:
        ActorID: The id of the current actor.
    """
    aid: ActorID = thread_context.actor.id
    return aid


def terminate(actor_id: ActorID) -> None:
    thread_context.actor.system.terminate(actor_id)
