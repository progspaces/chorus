from dataclasses import dataclass

from chorus import Event, Request, Response, ask, receive, run, spawn, tell


@dataclass
class Echo(Request):
    text: str


@dataclass
class Echoed(Response):
    text: str


@dataclass
class Stop(Event):
    pass


def echo():
    while True:
        match receive():
            case Echo() as request:
                response = Echoed(request.text, exchange_id=request.exchange_id)
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
    run(main)
