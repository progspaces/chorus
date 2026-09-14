from typing import Any, Tuple

from .actor import ActorFunction, ActorSystem, set_local_actor
from .id import ActorID


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


def setup_main_thread():
    system = ActorSystem()
    actor = system.next_actor()
    set_local_actor(actor)

    # doesn't do the teardown but is it needed?
