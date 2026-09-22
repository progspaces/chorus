import time
from collections import deque
from threading import Condition
from typing import Any, Callable


class Mailbox:
    """Mailbox implements a queue of messages used for each actor."""

    def __init__(self) -> None:
        self.messages: deque[Any] = deque()
        self.condition = Condition()

    def put(self, message: Any):
        """Add a message to the mailbox.

        This operation does not block.

        Args:
            message (Any): A value to use as a message.
        """
        with self.condition:
            self.messages.append(message)  # add new ones to the back
            self.condition.notify()  # notify threads that are waiting

    def get(
        self,
        predicate: Callable[..., bool] | None = None,
        block: bool = True,
        timeout: float | None = None,
    ) -> Any:
        """Gets a message from the mailbox.

        The default behaviour is get the oldest message out of the mailbox.
        If there isn't one, the method blocks indefinately until on arrives.
        This blocking can be turned off so it returns None if there are no messages.
        A timeout can be specified for this blocking.
        Selective receive is supported by passing a predicate function that matches message.

        Args:
            predicate (Callable[..., bool] | None, optional): A condition to use to select a message. Defaults to None.
            block (bool, optional): Should it block until there is a message. Defaults to True.
            timeout (float | None, optional): How long it should block for. Defaults to None.

        Raises:
            TimeoutError: The get timed out waiting for a message.

        Returns:
            Any: The message or None.
        """

        # if there is a timeout, work out when the deadline is
        deadline = time.monotonic() + timeout if timeout else None

        def get_next_message():
            """Pop the next message in the messages queue.
            Return None if there isn't one.
            Do not block.
            """
            if predicate:
                # the queue is organised oldest at front
                for idx, message in enumerate(self.messages):
                    if predicate(message):
                        del self.messages[idx]
                        return message
                return None
            else:
                if self.messages:
                    return self.messages.popleft()
                else:
                    return None

        # while there are no message
        while not (message := get_next_message()):
            if not block:
                # if there is no messages are we are not blocking
                break
            elif not deadline:
                # if there is no message or timeout
                # wait until the queue changes
                with self.condition:
                    self.condition.wait()
            else:
                # if there are no messages and we are blocking with a timeout
                # workout the remaining time
                remaining = deadline - time.monotonic()

                # if it is less than or equal to zero, throw an exception
                if remaining <= 0:
                    raise TimeoutError

                # otherwise block until message is added to queue or we run
                # out of remaining time on the timeout
                with self.condition:
                    self.condition.wait(remaining)

        # return the oldest message (new messages are added on the right)
        return message
