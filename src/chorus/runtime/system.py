from __future__ import annotations

import ctypes
import itertools
import threading
from dataclasses import dataclass, field
from typing import Any, Callable

from .mailbox import Mailbox

# An actor function is a function that can have any args and returns None.
# Its args can be anything, and we specify this using the ParamSpec P.
# This allows type-checkers to verify that we give it the inputs it expects.
type ActorFunction[**P] = Callable[P, None]


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


class ActorNotFoundError(LookupError):
    def __init__(self, actor_id: ActorID) -> None:
        self.actor_id = actor_id
        super().__init__(f"Actor {actor_id} not found")


class ActorTermination(Exception):
    def __init__(self) -> None:
        super().__init__("Actor terminated.")


@dataclass
class ActorRecord:
    """Holds all the information about a specific actor.

    For convinience there is also a reference to the ActorSystem that is
    running the actor.
    """

    id: ActorID
    system: ActorSystem
    mailbox: Mailbox = field(default_factory=Mailbox)
    thread_id: int | None = None
    local_store: dict[str, Any] = field(default_factory=dict)


class ThreadContext(threading.local):
    """Container for thread-local data including the current thread's actor.

    The threading.local class can be instantiated to produce an object that
    stores any data we want, but in such a way that when we access it the only
    data returned is what was stored by this thread.

    This subclass has the same behaviour, only asserting that certain members
    have particular types, as shown.
    """

    actor: ActorRecord


# Single instance of this class, imported by other modules
thread_context = ThreadContext()


def set_local_actor(actor: ActorRecord) -> None:
    """Set the actor for this thread.

    Useful when setting the actor for the main thread.

    Args:
        actor (Actor): The actor to use for this thread.
    """
    thread_context.actor = actor
    actor.thread_id = threading.get_ident()


class ActorSystem:
    """A container for the actors."""

    def __init__(self) -> None:
        self.next_id = itertools.count(0)
        self.actors: dict[ActorID, ActorRecord] = {}

    def next_actor(self) -> ActorRecord:
        id = ActorID(next(self.next_id))
        actor = ActorRecord(id=id, system=self)
        self.actors[id] = actor
        return actor

    def remove_actor(self, actor_id: ActorID) -> None:
        del self.actors[actor_id]
        del thread_context.actor

    def run[**P](
        self, target: ActorFunction[P], *args: P.args, **kwargs: P.kwargs
    ) -> ActorID:
        """Creates a new actor in the system based on the function that is passed in.

        Args:
            target (ActorFunction): The function to run as the actor.

        Returns:
            ActorID: The actor id object, used to send messages to the actor.
        """
        actor = self.next_actor()

        def run_actor() -> None:
            set_local_actor(actor)
            try:
                target(*args, **kwargs)
            except ActorTermination:
                print(f"Actor {actor.id} terminated successfully.")
            finally:
                self.remove_actor(actor.id)

        # initialise the thread to target the run_actor function
        thread = threading.Thread(target=run_actor)

        try:
            # start the thread
            thread.start()
        except Exception:
            # if it fails remove it for the actors list
            del self.actors[actor.id]
            raise
        return actor.id

    def get_actor_record(self, actor_id: ActorID) -> ActorRecord:
        if actor_id not in self.actors:
            raise ActorNotFoundError(actor_id)
        return self.actors[actor_id]

    def print_actors(self) -> None:
        print("Actor ID, Thread Id")
        print("---------------------")
        for id, record in self.actors.items():
            print(id, record.thread_id)

    def terminate(self, actor_id: ActorID) -> None:
        actor = self.get_actor_record(actor_id)

        if actor.thread_id is None:
            # thread has not started, so no action needed
            return

        thread_id = ctypes.c_long(actor.thread_id)
        exec_type = ctypes.py_object(ActorTermination)

        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, exec_type)

        if res == 0:
            raise ValueError("Invalid thread id.")
        elif res != 1:
            ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, None)
            raise SystemError("PyThreadState_SetAsyncExc failed")

    def add_to_local(self, actor_id: ActorID, key: str, value: Any) -> None:
        actor_record = self.get_actor_record(actor_id)
        actor_record.local_store[key] = value

    def get_from_local(self, actor_id: ActorID, key: str) -> Any:
        actor_record = self.get_actor_record(actor_id)
        return actor_record.local_store[key]
