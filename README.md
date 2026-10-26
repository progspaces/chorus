# Chorus - A simple actor library for Python

Chorus implements an Erlang-like actor API on top of Python's threading package. Actors run in their own threads, spawn other actors, and communicate through mailboxes.

The package has three layers:

- `chorus.runtime` manages actors and sends and receives arbitrary Python values.
- `chorus.messaging` provides message base classes and request/reply exchanges with `tell` and `ask`.
- `chorus.dispatch` dispatches messages to methods on handler objects and provides proxies for calling them.

These APIs are also available directly from the `chorus` top-level package.

## Installation

Chorus requires Python 3.14 or later. To add it to a project using uv:

```sh
uv add git+https://github.com/davemor/chorus.git
```

then:

```python
import chorus
```

For development, run this from a checkout:

```sh
uv sync --group dev --group docs
```

## Runtime: actors and messages

An `ActorSystem` manages actors. Its `run(target, *args, **kwargs)` method starts a function in a new actor thread and returns its `ActorID`. The helper `run(target, *args, **kwargs)` creates a new system and returns `(actor_id, system)`.

Inside an actor, `spawn` starts another actor in the same system, `me` returns the current actor's ID, and `send` delivers a Python value to another actor's mailbox. By default, `receive` waits for and removes the oldest message.

```python
from chorus import me, receive, run_main, send, spawn


def echo():
    sender, text = receive()
    send(sender, text)


def main():
    echo_id = spawn(echo)
    send(echo_id, (me(), "hello"))
    print(receive())  # hello


if __name__ == "__main__":
    run_main(main)
```

`run_main` runs the function on the main thread, registering that thread as an actor while the function runs. This allows it to use `spawn`, `send`, and `receive`, and is useful when integrating with a GUI event loop.

`receive` also supports selective and non-blocking reads:

- `receive(predicate)` returns the oldest matching message, leaving other messages queued.
- `receive(block=False)` returns `None` if no matching message is available.
- `receive(timeout=2)` waits up to two seconds and raises `TimeoutError` if no matching message arrives.

## Messaging: tell and ask

The messaging layer provides `Event`, `Request`, and `Response`, all derived from `Message`. `tell` sends a message without waiting for a reply. `ask` sends a request and waits for a response with the same `exchange_id`.

`ask` assigns the request's exchange ID. The responder passes that ID as a required keyword argument when constructing a response:

```python
from chorus import Event, Request, Response, ask, receive, run_main, spawn, tell


class Ping(Request):
    pass


class Pong(Response):
    pass


class Stop(Event):
    pass


def worker():
    ping = receive()
    tell(ping.sender, Pong(exchange_id=ping.exchange_id))
    receive(lambda message: isinstance(message, Stop))


def main():
    worker_id = spawn(worker)
    try:
        reply = ask(worker_id, Ping(), timeout=2)
        print(type(reply).__name__)  # Pong
    finally:
        tell(worker_id, Stop())


if __name__ == "__main__":
    run_main(main)
```

`ask` returns the response object. It raises `TimeoutError` if a supplied timeout expires.

## Dispatch: method calls through a proxy

`spawn_server_with_proxy` starts an actor that dispatches messages to a list of handler objects and returns a `Proxy`. The first handler with a matching callable method and compatible arguments handles the message.

```python
from chorus import run_main, spawn_server_with_proxy


class Echo:
    def reply(self, text):
        return text


def main():
    echo = spawn_server_with_proxy([Echo()])
    try:
        print(echo.ask.reply("hello"))  # hello
    finally:
        echo.kill()


if __name__ == "__main__":
    run_main(main)
```

`proxy.tell.method(...)` sends an `Invoke` message without waiting. `proxy.ask.method(...)` sends a `Call`, waits for a reply, and returns the result or raises the exception reported by the handler. The dispatch layer uses `Success` and `Error` responses internally. `proxy.kill()` sends a `Kill` event to stop the server.

For actors with their own event loop, `process_pending(handlers)` processes queued dispatch messages without blocking.

## Exampless

The [examples](./examples) are grouped by layer:

- [runtime](./examples/runtime/): actors, raw messages, main-thread execution, and drawing.
- [messaging](./examples/messaging/): message subclasses and request/reply exchanges.
- [dispatch](./examples/dispatch/): counters, proxies, and GUI event-loop integration.

To run an example from the repository root:

```sh
uv run examples/dispatch/proxy_counter.py
```

The drawing examples require Tkinter and a graphical desktop.

## Documentation

The guide and API reference are in [docs/source](./docs/source/). To build them with the required theme and extensions:

```sh
uv run --group dev --group docs sphinx-build -b html docs/source docs/_build/html
```

Open `docs/_build/html/index.html` to read the generated documentation.

## License

This project is licensed under the [MIT licence](./LICENSE).
