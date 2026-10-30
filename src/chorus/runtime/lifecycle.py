from functools import wraps
from typing import Tuple

from .system import ActorFunction, ActorID, ActorSystem, set_local_actor


def run[**P](
    target: ActorFunction[P], *args: P.args, **kwargs: P.kwargs
) -> Tuple[ActorID, ActorSystem]:
    """Run starts the target function as an actor in a new ActorSystem.

    This helper abstracts a common pattern used when programs are started.
    It let's you just do something like:

    if __name__ == "__main__":
        run(main)

    where main is the function for an actor.

    Args:
        target (ActorFunction): The function to run in the actor.

    Returns:
        Tuple[ActorID, ActorSystem]: The id of the new actor and the system.
    """
    system = ActorSystem()
    id = system.run(target, *args, **kwargs)
    return id, system


def register_thread_as_actor(system: ActorSystem) -> ActorID:
    actor = system.next_actor()
    set_local_actor(actor)
    return actor.id


def unregister_thread_as_actor(system: ActorSystem, main_actor_id: ActorID) -> None:
    system.remove_actor(main_actor_id)


def run_main[**P](func: ActorFunction[P], *args: P.args, **kwargs: P.kwargs) -> None:
    """Create an actor for the main thread and then run the passed function.

    This helper abstracts a common pattern used when programs are started.
    It let's you just do something like:

    if __name__ == "__main__":
        run_main(main)

    Args:
        func (ActorFunction): A function to act as our main.
    """
    system = ActorSystem()
    actor = register_thread_as_actor(system)
    try:
        func(*args, **kwargs)
    finally:
        unregister_thread_as_actor(system, actor)


def actors_entry(runner):
    # todo: this seems like an end-boss for type hints
    def decorate(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return runner(func, *args, **kwargs)

        return wrapper

    return decorate
