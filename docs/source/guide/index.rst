Guide
======
Chorus contains three subpackages, arranged in layers, each building on the one below it:

1. **runtime** provides a minimal API for managing Python threads using the Actor model. Inspired by Erlang, the API allows for the spawning of actors and for the sending and receiving of messages between them.
2. **messaging** provides a set of base classes for application-level message protocols to inherit from and functions for sending such messages and optionally waiting on responses. This API is inspired by Akka's tell and ask semantics.
3. **dispatch** builds on messaging to provide a more object-oriented style of interface allowing for inter-actor method calling. This is enabled with a domain-appropriate message vocabulary based on subclassing the message classes from the messaging package.

The functionality from the different layers is designed so that different actors within the same system can use functionality from each without them interfering with each other. What follows is a discussion of the basic concepts in Chorus followed by a guide to using each one of these layers.

Basic concepts
--------------
In the actor model, an actor is a concurrent computation that can do the following three things: send messages to other actors, create new actors, and change its behaviour based on the messages it receives.

Chorus implements a version of Actors on top of Python's threading package. Every actor is a function running in its own thread. Every actor has an id that uniquely identifies it. Actors can create new actors; this is called spawning them. For communication, each actor has an associated mailbox - a queue of messages it has received. An actor can add messages (any Python values) into the mailboxes of other actors whose ids it knows. Actors can then query their mailbox to receive messages.

The runtime package
-------------------
The runtime package provides a minimal API for managing actions. In Chorus, the actors are managed by an ``ActorSystem`` instance. To start an actor, we can declare a function, instantiate an ``ActorSystem``, and then call the system's run method.

.. code-block:: python

    from chorus import ActorSystem

    def my_actor(text: str) -> None:
        print(text)

    system = ActorSystem()
    system.run(my_actor, "hello")

This runs the function ``my_actor`` in a new thread and associates a mailbox with it. The run method returns an instance of ``ActorID`` representing the id of the actor that was spawned. The ``ActorSystem`` is responsible for ensuring all the ids are unique. Note that as this is a common pattern, Chorus provides a helper function called run that creates a new system and runs an actor.

.. code-block:: python

    from chorus import run

    def my_actor(text: str) -> None:
        print(text)

    # run returns the id of the actor and the system
    actor_id, system = run(my_actor, "hello")

Messaging
~~~~~~~~~
If an actor has the id of another actor, it can send them a message using the ``send`` function. This adds the message to the target actor's mailbox. The message can be any Python value (note - Erlang commonly uses tuples). To receive the message, the other actor uses the ``receive`` function. By default, this removes the oldest message out of the mailbox and returns it, and if there are no messages in the mailbox, receive blocks until one arrives. Here is an example:

.. code-block:: python

    from chorus import ActorSystem

    def actor_one() -> None:
        message = receive()
        print(message)

    def actor_two(other_id: ActorID) -> None:
        send(other_id, "Hello")

    system = ActorSystem()
    one_id = system.run(actor_one)
    two_id = system.run(one_id)

The first actor, ``actor_one``, receives one message, prints it out and exits. The second actor, ``actor_two``, is passed ``actor_one``'s id when it is run and then uses that to send it the string ``"Hello"`` as a message. Once it has done that, it terminates. Note that when actor threads terminate, the actor system removes their ids and performs appropriate cleanup. The main thread does not have to outlive the actors. In Python, the main thread can finish, but Python waits for all non-daemon threads (this is the default kind of thread) to finish before exiting the process.

Spawning new actors
~~~~~~~~~~~~~~~~~~~
Actors can spawn new actors using the ``spawn`` function. This takes in a function and its arguments. These can be positional or keyword arguments. The ``spawn`` function returns the id of the new actor. Here is an example:

.. code-block:: python

    def printer() -> None:
        while True:
            message = receive()
            print(message)

    def start() -> None:
        printer_id = spawn(printer)
        for idx in range(10):
            send(printer_id, f"Message {idx}")

    run(start)

In this example, the actor ``start`` is run from the main thread and then spawns the ``printer`` actor. It then sends 10 strings as messages, which the printer prints to standard out.

Current Actor ID
~~~~~~~~~~~~~~~~
The ``ActorID`` of the current actor can be retrieved using the function ``me``. Me is useful when an actor wants to include its own id in a message so it can get a reply. Note that a similar function is called ``self`` in Erlang but this is already used conventionally in Python. Here is an example of using me:

.. code-block:: python

    from chorus import me, receive, run, send, spawn

    def child():
        sender, msg = receive():
        send(sender, "Hello!")

    def parent():
        replier_id = spawn(replier)
        send(replier_id, (me(), "Good Morning."))

    run(parent)

In this example, the ``parent`` sends the ``child`` its id using the `me` function, allowing the ``child`` to send one back (which is ignored).

Main thread as actor
~~~~~~~~~~~~~~~~~~~~
In the pure actor model, everything is an actor. In Python, who knows? Generally the actor system instance is living on the main thread of the program and actors are run from there. This creates an unsatisfying difference between the main thread and the actor threads. To reduce this, Chorus provides a way to add the main thread to an actor system. This associates a mailbox with the main thread and allows it to send and receive messages as well as spawn new actors without a reference to the actor system.

The function register_thread_as_actor takes in a system and registers the current thread as an actor on that system. To shut down cleanly, use unregister_thread_as_actor from that same thread using the same system. However, the common pattern is to surround a main function (of some kind) with these, so Chorus provides a helper implementing this pattern. It is called run_main. Here is an example:

.. code-block:: python

    from chorus import run_main

    def main() -> None:
        print("Hey there!")

    if __name__ == "main":
        run_main(main)

Note that unlike the run function, this does not spawn a new actor to execute main in. It is just a function running on the main thread. However, the main thread is now an addressable actor, so main can send, receive, and spawn and everything just works!

Timeouts
~~~~~~~~
The ``receive`` function is quite versatile. By default, it blocks the thread but it can be put into a non-blocking mode by passing ``False`` to the ``block`` argument. In this mode, the ``receive`` function does not wait for a message to arrive, and if there are no messages waiting, it returns ``None``. This is useful in a polling situation where the actor has other work to do while waiting on a message. In blocking mode, the function can also accept a ``timeout`` argument, specified as the number of seconds to wait as a float. In this case, ``receive`` will block for that number of seconds and then return ``None`` if no message is present.

Selective receive
~~~~~~~~~~~~~~~~~
Chorus supports searching the mailbox for specific messages or types of messages. This mechanism is called selective receive (a term taken from Erlang). It enables the actor to only receive some types of messages at specific points in its operation. For example, it might wait to receive a confirmation message that an image has been loaded before sending a message to draw the image. To perform selective receive, the ``receive`` function takes in a predicate, a function that returns a boolean value, and returns the oldest message in the mailbox that satisfies the predicate. Here is an example:

.. code-block:: python

    from chorus import me, receive, run_main, send

    def main():
        # add some messages to my own mailbox
        send(me(), "info")
        send(me(), "reply")

        # selectively receive "reply"
        reply = receive(lambda msg: msg[0] == "reply")

        # print out "reply" then "info"
        print(f"Selected: {reply}")
        print(f"Remaining: {receive()}")

    run(main)

The messaging package
---------------------
The messaging package provides two things that sit on top of the functionality provided by the runtime package: a set of base classes that can be inherited from to create protocols for different applications and two functions that exploit these classes to send and (optionally) block waiting on a response. These functions make coordinating interactions between actors in which there is some dependency more concise.

Message classes
~~~~~~~~~~~~~~~
The message package provides a set of base classes that can be inherited by messages used by applications. Figure :numref:`fig-message-hierarchy` shows this message class hierarchy.

.. _fig-message-hierarchy:

.. mermaid::
   :caption: Message class hierarchy

   classDiagram
       Message <|-- Event
       Message <|-- Request
       Message <|-- Response

       class Message {
           +ActorID sender
       }

       class Request {
           +int exchange_id
       }

       class Response {
           +int exchange_id
       }

This hierarchy has ``Message`` at the top. ``Message`` includes the id of the sender, allowing for all messages to be replied to if required. ``Message`` has three subclasses: ``Event`` is a message that does not expect a reply, ``Request`` is a message that does expect a reply and ``Response`` is the reply. 

``Request`` and ``Response`` both contain an ``exchange_id`` which is a unique identifier for the request-reponse exchange between the actors. This identifier can be tested for using selective recieve in order to locate the response to a specific request inside a mailbox. Something like this works:

.. code-block:: python

    def match_id(msg: Any) -> bool:
        # assume that request is in scope
        return isinstance(msg, Response) and msg.exchange_id == request.exchange_id

    response = receive(match_id)

However, this is considered such a useful pattern that the package provides an abstraction: ask.

Tell and ask
~~~~~~~~~~~~
The ``tell`` and ``ask`` functions wrap send and receive to use the above messaging classes. This is useful for (some degree) of type checking. ``tell`` means send the message to the target actor and do not expect a response. ``ask`` means send the message to the target actor and wait for the response before continuing. The response is a response object with the same exchange_id (as discussed above). Here is a short example:

.. code-block:: python

    from chorus import Event, Request, Response, ask, receive, run_main, spawn, tell

    # Inherit from the base classes to create 
    # an application specific set of messages.
    class Ping(Request):
        pass


    class Pong(Response):
        pass


    class Stop(Event):
        pass


    def worker():
        # Send a ping back for every pong.
        # Loop until told to stop.
        while True:
            match receive():
                case Ping() as ping:
                    pong = Pong(exchange_id = ping.exchange_id)
                    tell(ping.sender, pong)
                case Stop():
                    print('Stopping worker.')


    def main():
        worker_id = spawn(worker)
        pong = ask(worker_id, Ping())  # Wait for a reply.
        print(f'Got pong from actor {pong.sender}')
        tell(worker_id, Stop())  # Send without waiting.


    run_main(main)

Hopefully, this demonstrates the utility of this approach. We are now using typed messages that can be easily used in ``match`` expressions and can use ``ask`` to wait on responses mimicing a function call and allowing for limited coordination between actors.

The dispatch package
--------------------
The dispatch package builds on the messages package to provide a more object-oriented style syntax for message sending and handing. This is actived though two concepts: **proxies** and **handlers**.

Proxies
~~~~~~~
Proxy is a class that wraps an ActorID and provides methods to ``tell``, ``ask``, or ``kill`` that actor. The ``tell`` and ``ask`` methods are getters that return objects that wrap any method call on them as messages and sends them to the target actor using either ``tell`` or ``ask``. This allows for a calling style such as:

.. code-block:: python

    # a variation on the pervious example
    worker_id = spawn(working_actor)
    worker = Proxy(worker_id)
    pong = worker.ask.ping()
    print(f'Got pong from actor {pong.sender}')
    worker.kill()

Under the hood, proxy makes use of a custom message vocabulary based on the messaging package base classes.

Handlers
~~~~~~~~
A handler is an object that handles messages. Chours provide infrastucture to register a list of handlers for an Actor. When setup in this way, Chours repreatedly calls ``recieve`` on the actor thread and then looks to see if there is a method on a handler that matches that name and arguments provided in the message. If it does, it calls that method. If it cannot find a method to dispatch to then the message is ignored.

This dispatch mechanism can be used in one of two ways. These are called **server mode** and **message process** mode. Server mode takes over control of the actors thread and sits in a loop recieving messages and dispatching them to the handler list. Message process mode, does not sit in a loop, it just clears the mailbox and attempts to dispatch all the messages. It is suitable for situations where the thread is doing more things than just processing messages from its mailbox.

The helper function ``spawn_server_with_proxy`` function takes in a list of handlers, spawns an new actor in server mode with that handler list, then returns a proxy object wrapping the new actors ActorID. Here is a simple example of its use:

.. code-block:: python

    from dataclasses import dataclass

    from chorus import run, spawn_server_with_proxy


    # declare our handler object
    @dataclass
    class Counter:
        n: int

        def increment(self):
            self.n = self.n + 1

        def get(self):
            return self.n


    def main():
        # spawn the counter actor
        counter = spawn_server_with_proxy([Counter(n=0)])

        # increment the counter 3 times
        counter.tell.increment()
        counter.tell.increment()
        counter.tell.increment()

        # get the count
        count = counter.ask.get()
        print(count)

        # kill the counter
        counter.kill()


    if __name__ == "__main__":
        run(main) 


Using Chorus with Typer
-----------------------
A common pattern is to use `run` and `run_main` to start a main entry point for an application using Chorus. These functions accept target functions to run as the main entry point: one uses a new thread and another uses the main thread. Both register the thread as an actor.

However, this pattern does not play well with command line parsing. Typer is a popular CLI library that uses type annotations to create a CLI interface. To do this it needs to wrap the programs main function.

To resolve this, Chorus provides a decorator called `actors_entry` that can be used to wrap the main entry point of for the actors. It takes as an argument, which of the Chorus run functions to use (`run` or `run_main`). Here is an example of its use with Typer:

.. code-block:: python

    from chorus import actors_entry, run_main
    import typer

    def greeter(name: str) -> None:
        print(f"Hello, {name}!")

    @actors_entry(run_main)
    def main(name: str, count: int = 1) -> None:
        for _ in range(count):
            spawn(name)

    if __name__ == "__main__":
        typer.run(main)

This exmaple runs the function `main` as the entry point for Typer to take the command line arguments from and also uses Chorus's `run_main` to run the `main` function as an actor on the main thread. The number of actors to spawn is passed in as the count argument into a Typer generated command line tool. Note - this is not included as an example in `examples` so to avoid making Typer a dependency.