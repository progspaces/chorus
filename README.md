# Chorus - A simple actor library for Python

Chorus is a Python package that provides a version of the Actor model of concurrency. It is built ontop of Python's built-in threading package and each Actor has its own thread. Actors can send and recieve messges from other actors as well as spawn new Actors.

The package has three layers:

- `chorus.runtime` a minimal API for managing Python threads using the Actor model, roughly based on Erlangs API. 
- `chorus.messaging` provides message base classes and request/reply exchanges with `tell` and `ask`.
- `chorus.dispatch` provides an object-oriented API for sending and receiving messages between actors.

There APIs can be imported directly from the ``chorus`` top-level package.

## Installation
Chorus requires Python 3.14 or later. To add it to a project using uv:

```sh
uv add git+https://github.com/davemor/chorus.git
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