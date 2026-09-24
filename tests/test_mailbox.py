import time
from threading import Timer
from typing import Any

import pytest

from chorus.actors.mailbox import Mailbox


def test_get_ordered():
    mailbox = Mailbox()

    # add some stuff
    mailbox.put("hello")
    mailbox.put("there")

    # check we get them in order
    msg1 = mailbox.get()
    msg2 = mailbox.get()

    # assert they are as expected
    assert msg1 == "hello", "First message shoud be hello."
    assert msg2 == "there", "Second message shoud be there."


def test_selective_get():
    mailbox = Mailbox()

    # add four numbers
    mailbox.put("one")
    mailbox.put("two")
    mailbox.put("three")
    mailbox.put("four")

    # create a function that selects the third message
    def pred(msg: Any) -> bool:
        return msg == "three"

    # check we get them in order
    message = mailbox.get(pred)

    # asset it is the correct message
    assert message == "three", "Expected message to be three."


def test_nonblocking():
    mailbox = Mailbox()

    def hello():
        mailbox.put("hello")

    timer = Timer(1, hello)
    timer.start()

    # check we get them in order
    first_message = mailbox.get(block=False)
    assert first_message is None, (
        f"First message should be None. Actually is {first_message}."
    )
    time.sleep(2)

    second_message = mailbox.get()
    assert second_message == "hello", "Second message should be hello."


def test_timeout():
    mailbox = Mailbox()

    def hello():
        mailbox.put("hello")

    timer = Timer(2, hello)
    timer.start()

    # this tests to see if a TimeoutError is raise
    with pytest.raises(TimeoutError):
        mailbox.get(timeout=1)
