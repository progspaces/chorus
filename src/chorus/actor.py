import itertools
from dataclasses import dataclass, field
from threading import Thread, local
from typing import Any, Callable

from .id import ActorID
from .mailbox import Mailbox

# an actor function is a function that can have any args and returns None
ActorFunction = Callable[..., None]

# Threads that run the actors can access information about the actor they are
# running using the local function.
# See https://docs.python.org/3/library/threading.html#thread-local-data.
# This allows for the implementation of the API without need for an actor
# object reference.
thread_context = local()


@dataclass
class Actor:
    """Holds all the information about a specific actor.

    For convinience there is also a reference to the ActorSystem that is
    running the actor.
    """

    id: ActorID
    mailbox: Mailbox = field(default_factory=Mailbox)
    system: ActorSystem | None = None


class ActorSystem:
    """A container for the actors."""

    def __init__(self) -> None:
        self.next_id = itertools.count(1)
        self.actors: dict[ActorID, Actor] = {}

    def run(self, target: ActorFunction, *args: Any, **kwargs: Any) -> ActorID:
        """Creates a new actor in the system based on the function that is passed in.

        Args:
            target (ActorFunction): The function to run as the actor.

        Returns:
            ActorID: The actor id object, used to send messages to the actor.
        """
        id = ActorID(next(self.next_id))  # get the next actor id
        actor = Actor(id=id, system=self)  # construct the actor
        self.actors[id] = actor  # add the actor to the actors dictionary

        # This function runs in the thread.
        # It's job is to setup the environment for the actor and handle
        # clean up. Cause it is defined inside the spawn method, we can use
        # the *args, **kwargs, and self.actors without passing them to
        # run_actor.
        def run_actor():
            thread_context.actor = actor
            try:
                # run the actor function
                target(*args, **kwargs)
            finally:
                # remove the actor from the list of actors
                del self.actors[actor.id]
                # delete the actor from the local thread store.
                del thread_context.actor

        # initialise the thread
        thread = Thread(target=run_actor)

        # start the thread
        try:
            thread.start()
        except Exception:
            # if it fails remove it for the actors list
            del self.actors[id]
            raise
        return id


def spawn(target: ActorFunction, *args: Any, **kwargs: Any) -> ActorID:
    return thread_context.actor.system.run(target, *args, **kwargs)


def send(id: ActorID, message: Any) -> None:
    target = thread_context.actor.system.actors[id]
    target.mailbox.put(message)


def receive() -> Any:
    return thread_context.actor.mailbox.get()


def me() -> ActorID:
    return thread_context.actor.id
