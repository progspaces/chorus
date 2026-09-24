import itertools
from dataclasses import dataclass, field
from threading import Thread, local
from typing import Any, Callable

from .mailbox import Mailbox

# an actor function is a function that can have any args and returns None
ActorFunction = Callable[..., None]


@dataclass(frozen=True)
class ActorID:
    """Identifies an actor in the system.
    Equivilent to an Erlang PID.

    If we move to a distributed system, this can be exteneded to a more
    complex address. Also we could us it as an adapter to fake method style
    sends. E.g. my_actor.send(()) rather then send(my_actor, ()).
    """

    identifier: int

    def __str__(self) -> str:
        return str(self.identifier)


@dataclass
class ActorRecord:
    """Holds all the information about a specific actor.

    For convinience there is also a reference to the ActorSystem that is
    running the actor.
    """

    id: ActorID
    system: ActorSystem
    mailbox: Mailbox = field(default_factory=Mailbox)


# a thread local object to hold each threads instance of the Actor class
# See https://docs.python.org/3/library/threading.html#thread-local-data.
thread_context = local()


def set_local_actor(actor: ActorRecord):
    """Set the actor for this thread.

    Useful when setting the actor for the main thread.

    Args:
        actor (Actor): The actor to use for this thread.
    """
    thread_context.actor = actor


class ActorSystem:
    """A container for the actors."""

    def __init__(self) -> None:
        self.next_id = itertools.count(1)
        self.actors: dict[ActorID, ActorRecord] = {}

    def next_actor(self):
        id = ActorID(next(self.next_id))
        actor = ActorRecord(id=id, system=self)
        self.actors[id] = actor
        return actor

    def remove_actor(self, actor_id: ActorID) -> None:
        del self.actors[actor_id]
        del thread_context.actor

    def run(self, target: ActorFunction, *args: Any, **kwargs: Any) -> ActorID:
        """Creates a new actor in the system based on the function that is passed in.

        Args:
            target (ActorFunction): The function to run as the actor.

        Returns:
            ActorID: The actor id object, used to send messages to the actor.
        """

        actor = self.next_actor()

        def run_actor():
            set_local_actor(actor)
            try:
                target(*args, **kwargs)
            finally:
                self.remove_actor(actor.id)

        # initialise the thread to target the run_actor function
        thread = Thread(target=run_actor)

        try:
            # start the thread
            thread.start()
        except Exception:
            # if it fails remove it for the actors list
            del self.actors[actor.id]
            raise
        return actor.id
