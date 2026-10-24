from typing import Any, Tuple

from .system import ActorFunction, ActorID, ActorSystem, set_local_actor


def run(
    target: ActorFunction, *args: Any, **kwargs: Any
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


def run_main(func: ActorFunction, *args: Any, **kwargs: Any) -> None:
    """Create an actor for the main thread and then run the passesd function.

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
