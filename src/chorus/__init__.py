# import from the kernel package
from .kernel.actor import (
    Actor,
    ActorID,
    ActorSystem,
    me,
    receive,
    send,
    set_local_actor,
    spawn,
)

# import from the patterns package
from .patterns.calls import ask, kill, tell
from .patterns.messages import End, Error, Request, Response
from .patterns.proxy import Proxy
from .patterns.router import spawn_with_proxy
from .patterns.run import run, run_main, setup_main_thread
