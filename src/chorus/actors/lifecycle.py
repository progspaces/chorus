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


def setup_main_thread() -> tuple[ActorSystem, ActorID]:
    """Helper that sets up an ActorSystem and setup the main thread as an actor."""
    system = ActorSystem()
    main_actor = system.next_actor()
    set_local_actor(main_actor)
    return system, main_actor.id


def shutdown_main_thread(system: ActorSystem, main_actor_id: ActorID) -> None:
    system.remove_actor(main_actor_id)


def run_main(func: ActorFunction, *args: Any, **kwargs: Any) -> None:
    """Create an actor for the main thread and then run the passesd function.

    This helper abstracts a common pattern used when programs are started.
    It let's you just do something like:

    if __name__ == "__main__":
        start(main)

    The start is like run but

    Args:
        func (_type_): _description_
    """
    system, actor = setup_main_thread()
    try:
        func(*args, **kwargs)
    finally:
        shutdown_main_thread(system, actor)
        raise
