# Chorus - A simple actor library for Python

Chorus is a Python package that provides a version of the Actor model of concurrency. It is built ontop of Python's built-in threading package and each Actor has its own thread. Actors can send and recieve messges from other actors as well as spawn new Actors.

The package has three layers:

- `chorus.runtime` a minimal API for managing Python threads using the Actor model, roughly based on Erlangs API. 
- `chorus.messaging` provides message base classes and request/reply exchanges with `tell` and `ask`.
- `chorus.dispatch` provides an object-oriented API for sending and receiving messages between actors.

There APIs can be imported directly from the ``chorus`` top-level package.

## Examples
Here is an example of the `chorus.runtime` API in action. One actor spawns another and that one echos back every messaged if the message has a `sender_id`, otherwise is ends.
```python
from chorus import me, receive, run, send, spawn


def echo():
    match receive():
        case (sender_id, msg):
            send(sender_id, msg)
            echo()
        case _:
            print("Echo: any other message means end.")


def main():
    echo_id = spawn(echo)
    send(echo_id, (me(), "hello"))
    msg = receive()
    print(f"received: {msg}")
    send(echo_id, "end")


if __name__ == "__main__":
    run(main)
```
Here is that same echo example using the `chorus.dispatch` API:
```python
from typing import Any
from chorus import run, spawn_server

class EchoHandler:
    def echo(self, message: Any) -> Any:
        return message

def main():
    proxy = spawn_server(EchoHandler())
    result = proxy.ask.echo("hello")
    print(result)  # 'hello'
    proxy.kill()

if __name__ == "__main__":
    run(main)
```

## Installation
Chorus requires Python 3.12 or later. The package name on Pypi is `chorus-actors`. To add it to a project using uv:

```sh
uv add chorus-actors
```

Or install it with pip:

```sh
python -m pip install chorus-actors
```

## Documentation
The documentation can be found [here](https://chorus-actors.readthedocs.io/en/latest/).

## Examples:
The [examples](./examples) are grouped by layer:

- [runtime](./examples/runtime/): actors, raw messages, main-thread execution, and drawing.
- [messaging](./examples/messaging/): message subclasses and request/reply exchanges.
- [dispatch](./examples/dispatch/): counters, proxies, and GUI event-loop integration.

To run an example from the repository root:

```sh
uv run examples/dispatch/proxy_counter.py
```

## License

This project is licensed under the [MIT licence](./LICENSE).
