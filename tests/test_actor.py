from queue import Queue
from typing import Any

from chorus import ActorSystem, receive


def test_spawn():
    def actor():
        pass

    system = ActorSystem()
    id = system.run(actor)
    assert id.identifier == 1, "Actor ids should start at 1."


def test_send_receive():
    hello_message = "hello"
    received: Queue[Any] = Queue()

    def actor():
        received.put(receive())

    system = ActorSystem()
    id = system.run(actor)
    system.send(id, hello_message)
    assert received.get(timeout=2) == hello_message, "Message should be hello."
