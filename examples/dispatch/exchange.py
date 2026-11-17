from dataclasses import dataclass

from chorus import ExchangeMessage, Message, ask, receive, spawn, tell
from chorus.runtime.system import ActorSystem


@dataclass
class Echo(ExchangeMessage):
    text: str


@dataclass
class Echoed(ExchangeMessage):
    text: str


@dataclass
class Stop(Message):
    pass


def echo():
    while True:
        match receive():
            case Echo() as request:
                response = Echoed(request.text)
                response.exchange_id = request.exchange_id
                tell(request.sender, response)
            case Stop():
                return


def main():
    echo_id = spawn(echo)
    try:
        response = ask(echo_id, Echo("hello"), timeout=2)
        print(f"received: {response.text}")
    finally:
        tell(echo_id, Stop())


if __name__ == "__main__":
    with ActorSystem():
        main()
