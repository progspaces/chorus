import time
from collections import deque
from collections.abc import Callable
from threading import Condition
from typing import Any

# this object is used when the queue is EMPTY
# this avoids falsey messages like [] being missed
EMPTY = object()


class Mailbox:
    """Mailbox implements a queue of messages used for each actor."""

    def __init__(self) -> None:
        self.messages: deque[Any] = deque()
        self.condition = Condition()

    def put(self, message: Any) -> None:
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
        predicate: Callable[[Any], bool] | None = None,
        block: bool = True,
        timeout: float | None = None,
    ) -> Any:
        """Gets a message from the mailbox.

        The default behaviour is get the oldest message out of the mailbox.
        If there isn't one, the method blocks indefinitely until on arrives.
        If block is False it means non-blocking and return immediately (timeout
        is ignored).
        If block is True the behaviour is determined by timeout parameter.
        If timeout is None, this mean block indefinitely.
        Otherwise block for that number of seconds.
        Note that this means that if timeout is 0.0, this is the same as non-blocking.
        Selective receive is supported by passing a predicate that matches message.

        Args:
            predicate: A condition to use to select a message. Accepts any message by
            default.
            block: Whether to block until there is a message. Defaults to True.
            timeout: How long to block for, in seconds. Blocks indefinitely by default.

        Raises:
            TimeoutError: The get timed out waiting for a message.

        Returns:
            The message or None.
        """
        # if there is a timeout, work out when the deadline is
        deadline = time.monotonic() + timeout if timeout is not None else None

        def get_next_message() -> Any:
            """Pop the next message in the messages queue.

            This does not block.

            Returns:
                The message if there is one, or EMPTY if not.
            """
            if predicate:
                # the queue is organised oldest at front
                for idx, message in enumerate(self.messages):
                    if predicate(message):
                        del self.messages[idx]
                        return message
                return EMPTY
            if self.messages:
                return self.messages.popleft()
            return EMPTY

        # while there are no message
        with self.condition:
            while (message := get_next_message()) is EMPTY:
                if not block:
                    # if there is no messages are we are not blocking
                    message = None
                    break
                if not deadline:
                    # if there is no message or timeout
                    # wait until the queue changes
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
                    self.condition.wait(remaining)

        # return the oldest message (new messages are added on the right)
        return message
