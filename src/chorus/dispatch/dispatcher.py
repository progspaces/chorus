import logging
from email import message
from typing import Any

from chorus.dispatch.exchange import ExchangeMessage, tell
from chorus.dispatch.messages import Call, Error, Kill, Success
from chorus.runtime import receive

logger = logging.getLogger(__name__)


class Dispatcher:
    def __init__(self, handlers: list[object]) -> None:
        self.handlers = handlers
        self.running = False

    def _find_hander(self, name: str) -> object | None:
        for handler in self.handlers:
            method = getattr(handler, name, None)
            if callable(method):
                return handler
        return None

    def _dispatch(self, msg: Call) -> Any:
        handler = self._find_hander(msg.name)
        if handler:
            method = getattr(handler, msg.name)
            return method(*msg.args, **msg.kwargs)
        raise ValueError(f"No handler for {msg.name!r} found.")

    def _handle_call(self, msg: Call) -> None:
        def reply(reply: ExchangeMessage) -> None:
            if msg.reply:
                reply.exchange_id = msg.exchange_id
                tell(msg.sender, reply)

        try:
            result = self._dispatch(msg)
            reply(Success(result))
        except Exception as reason:
            reply(Error(reason))

    def _process_mailbox(self, block: bool = False) -> bool:
        while True:
            match receive(block=block):
                case Call() as msg:
                    self._handle_call(msg)
                case Kill():
                    return False
                case None:
                    return True
                case _:
                    logger.info(f"Cannot route unknowns message: {message}")

    def loop(self) -> None:
        self._process_mailbox(block=True)

    def process_pending(self) -> None:
        self._process_mailbox(block=False)
