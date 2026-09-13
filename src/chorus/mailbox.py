from dataclasses import dataclass, field
from queue import Queue
from typing import Any


@dataclass
class Mailbox:
    """Mailbox implements a queue of messages used for each actor.

    This wraps the Python queue so that the whole queue interface is not
    exposed and to make the implementation open to extension in the future.
    For example, we might want to add Erlang style selective receive.
    """

    queue: Queue[Any] = field(default_factory=Queue[Any])

    def put(self, message: Any):
        """Add a message to the mailbox.

        This operation does not block.

        Args:
            message (Any): A value to use as a message.
        """
        self.queue.put_nowait(message)

    def get(self) -> Any:
        """Retrive the next message in the queue.

        This operation will block until a message arrives.

        Returns:
            Any: The value of the message.
        """
        return self.queue.get()
