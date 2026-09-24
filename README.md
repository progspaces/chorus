# Chorus - A simple actors library for Python
This libray implements an Erlang-like API ontop of Python's threading package. Actors can spawn new actors and send and recieve messages. Using these operations, Chorus supports an simple messaging protocol and object-like message dispatch.

## Two small examples
Here is a simple echo exmaple using the basic API:

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
    print(f"recieved: {msg}")
    send(echo_id, "end")

if __name__ == "__main__":
    run(main)
```
And here is the same example using the object-like API:

```python
from chorus import run, spawn_with_proxy

class Echo:
    def reply(self, text):
        return text

def main():
    echo = spawn_with_proxy(Echo())
    text = echo.ask.reply("hello")
    print(f"recieved: {text}")
    echo.kill()

if __name__ == "__main__":
    run(main)
```

## Installation
Chorus is not on PyPI at the moment. To add it to a project, install it from GitHub with:
```bash
uv add git@github.com:progspaces/chorus.git
```

## Quick start
In Chorus, an actor is a function running it's own thread. The actors are managed by an `ActorSystem` instance. To start and actor, we can declare an function and a system and call run:

```python
from chorus import ActorSystem

def my_actor(text: str) -> None:
    print(text)

system = ActorSystem()
system.run(my_actor, "hello")
```

Note that as this is a common pattern, Chorus provides a helper function called `run` that creates a new system and runs an actor.

Actor can send and recieve messages from other actors. Actors are addressed using their id which is represented with the class `ActorID`. The `send` function takes a target id and a message, which can be of any type (conventionally this would be a tuple) and delivers that message to the target actor. The target actor can call `recieve` which will return the message. Messages are returned from `recieve` in the order they are revieved the actor (oldest first). `recieve` blocks the thread until a message is available.

Actors can create new actors using the `spawn` function. Like the `run` method on ActorSystem, this takes in a function and it's agruments (*args, and *kwargs) and returns an `ActorID`.

A common pattern is to send the id of the sender as part of the message, in order that the other actor can send a message back in response. This requires an actor to know it's own id. The function `me()` is used to get this.

Here is a larger example, showing these functions at work:

```python
from chorus import me, receive, run, send, spawn


def counter(n: int):
    match receive():
        case "incroment":
            counter(n + 1)
        case ("get", sender_id):
            send(sender_id, ("count", n))
        case _:
            print("Counter: unknown message.")


def main():
    # spawn the counter actor
    counter_id = spawn(counter, 0)

    # incroment the counter 3 times
    send(counter_id, "incroment")
    send(counter_id, "incroment")
    send(counter_id, ("get", me()))

    # retrieve the count
    match receive():
        case ("count", n):
            print(f"Counter is at {n}")
        case _:
            print("main: unknown message.")


if __name__ == "__main__":
    run(main)
```

## More Examples
The [examples](./examples/) folder contains some examples of how to use Chorus.

## Documentation
More comprehensive documentation can be found in the [/docs](./docs/_build/html/index.html) folder.

```bash
uv run --group docs sphinx-build -b html docs/source docs/_build/html
```

## License
This project is licenced under the MIT licence.
