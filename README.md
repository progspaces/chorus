# Chorus - A simple actor library for Python

Chorus is a Python package that provides a version of the Actor model of concurrency. It is built on top of Python's built-in threading package and each Actor has its own thread. Actors can send and receive messges from other actors as well as spawn new Actors.

The package has two layers:

- `chorus.runtime` a minimal API for managing Python threads using the Actor model, roughly based on Erlangs API. 
- `chorus.dispatch` provides message exchanges with `tell` and `ask`, dispatchers, and method-call proxies for actor services.

Import the public APIs directly from `chorus`:

```python
from chorus import receive, run, spawn, ask, tell, spawn_service
```

The top-level package brings together the runtime and dispatch APIs.
Internal modules import directly from defining modules to avoid circular imports.

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
from chorus import spawn_service, run

class EchoHandler:
    def echo(self, message: Any) -> Any:
        return message

def main():
    proxy = spawn_service(EchoHandler())
    try:
        result = proxy.ask.echo("hello")
        print(result)  # 'hello'
    finally:
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

- [runtime](./examples/runtime/): actors, raw messages, and main-thread execution.
- [dispatch](./examples/dispatch/): message exchanges, counters, proxies, and GUI event-loop integration.

To run an example from the repository root:

```sh
uv run examples/dispatch/proxy_counter.py
```

## License

This project is licensed under the [MIT licence](./LICENSE).
