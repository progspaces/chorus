Guide
======
Chous contains three subpackages, arranged in layers, each building on the one below it:

1. **runtime** provides a minimal API for managing Python threads using the Actor model. Inspired by Elang, the API allows for the spawning of actors and for the sending and recieving of messags between them.
2. **messaging** provide a set of base classes for application-level message protocols to inherit from and functions for sending such messages and optionally waiting on resposes. This API is inspired by Akka's tell and ask semantics.
3. **dispatch** builds on messaging to provide a more object-oriented style of interface allowing for inter-actor method calling. This is enabled with a domain appropriate message vocabulary based on subclassing the message classes from the messaging package.

The functionality from the different layers is designed so that different actors within the same system can use functionality from each without them interfearing with each other. What follows is a discussion of the basic concepts in Chous followed by a guide to using each one of these layers.

Basic concepts
--------------
In the actor model, an actor is a concurrent computation that can do the following three things: send messages to other actors, create new actors, change its behaviour based on the messages it recieves.

Chous implementes a version of Actors on top of Python's threading package. Every actor is function running in its own thread. Every actor has an id that uniquely identifies it. Actors can create new actors, this is called spawing them. For communication, each actor has a associated mailbox - a queue of messages it has recieved. An actors can add messages (any Python values) into mailbox of other actors that they know the actors id. Actors can then query their mailbox to recieve messages.

The runtime package
-------------------
The runtime package provides a minimal API for managing actions. In Chous, the actors are managed by an ``ActorSystem`` instance. To start an actor, we can declare a function, instantiate an ``ActorSystem``, and then call the systems run method.

.. code-block:: python

    from chorus import ActorSystem

    def my_actor(text: str) -> None:
        print(text)

    system = ActorSystem()
    system.run(my_actor, "hello")

This runs the function ``my_actor`` in a new thread and associcates a mailbox with it. The run method returns an instance of ``ActorID`` representing the id of the actor that was spawned. The ``ActorSystem`` is responsible for ensuring all the ids are unique. Note that as this is a common pattern, Chorus provides a helper function called run that creates a new system and runs an actor.

.. code-block:: python

    from chorus import run

    def my_actor(text: str) -> None:
        print(text)

    # run returns the id of the actor and the system
    actor_id, system = run(my_actor, "hello")

Messaging
~~~~~~~~~
If an actor has the id of another actor, it can send them a message using the ``send`` function. This add the message to the target actors mailbox. The message can be any Python value (note - Erlang commonly uses tuples). To recieve the message, the other actor uses the ``recieve`` function. By default, this removes the oldest message out of the mailbox and returns it and if there are no messages in the mailbox, the recieve blocks until one arrives. Here is an example:

.. code-block:: python

    from chorus import ActorSystem

    def actor_one() -> None:
        message = recieve()
        print(message)

    def actor_two(other_id: ActorID) -> None:
        send(other_id, "Hello")

    system = ActorSystem()
    one_id = system.run(actor_one)
    two_id = system.run(one_id)

The first actor, ``actor_one``, recieves one message, prints it out and exits. The second actor, ``actor_two``, is passes ``actor_one``'s id when it is run and then uses that to send it the string ``"Hello"`` as a message. Once it has done that, it terminates. Note that when actor threads terminate, the actor system removes there id and performs appropriate clean up. The main thread does not have to outlive the actors. In Python, the main thread can finish, but Python waits for all non-daemon threads (this is a the default kind of thread) to finish before exiting the process.

Spawning new actors
~~~~~~~~~~~~~~~~~~~
Actors can spawn new actors using the ``spawn`` function. This takes in a function and it's arguments. These can be positional or keyword arguments. The ``spawn`` function returns the id of the new actor. Here is an example:

.. code-block:: python

    def printer() -> None:
        while True:
            message = recieve()
            print(message)

    def start() -> None:
        printer_id = spawn(printer)
        for idx in range(10):
            send(printer_id, f"Message {idx}")

    run(start)

In this example, the actor ``start`` is run from the main thread and then spawns the ``printer`` actor. It then send 10 strings as messages, which the printer prints to standard out.

Current Actor Id
~~~~~~~~~~~~~~~~
The ``ActorID`` of the current actor can be retrived using the function ``me``. Me is useful when an actor wants to include a its own id in a message so it can get a reply. Note that a similar function is called ``self`` in Erlang but this is already used conventionally in Python. Here is an example of using me:

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
In the pure actor model, everything is an actor. In Python, who knows? Generally the actor system instance is living on the main thread of the program and actors are run from there. This creates an unsatifying difference between the main thread and the actor threads. To reduce this, Chorus provides a way to add the main thread to an actor system. This associcates a mailbox with the main thread and allows it to send and recieve messages as well as spawn new actors without a reference to the actor system.

The function register_thread_as_actor takes in a system and registers the current thread as an actor on that system. To shutdown cleanly use unregister_thread_as_actor from that same thread using the same system. However, the common pattern is to surround a main function (of somekind) with these, so Chorus provides a helper implementing this pattern. It is called run_main. Here is an example:

.. code-block:: python

    from chorus import run_main

    def main() -> None:
        print("Hay there!")

    if __name__ == "main":
        run_main(main)

Note that unlike the run function, this does not spawn a new actor to execute main in. It is just function running on the main thread. However, the main thread is now an addressable actor, so main can send, recieve, and spawn and everything just works!

Timeouts
~~~~~~~~
The ``recieve`` function is is quite versitile. By default it blocks the thread but it can be put into a non-blocking mode by passing ``False`` to the ``block`` argument. In this mode, ``recieve`` function does not wait for a message to arrive and if there are no messages waiting, it returns ``None``. This is useful in a polling situation where the actor has other work to do while waiting on a message. In blocking mode, the function can also accept a ``timeout`` argument, specfied as the number of seconds to wait as a float. In this case, ``recieve`` will block for that number of seconds and then return ``None`` if no message is present.

Selective receive
~~~~~~~~~~~~~~~~~
Chous supports searching the mailbox for specific messages or types of messages. This mechanism is called selective receive (a term taken from Erlang). It enables the actor only receive some types of messages at specific points in its operation. For example, it might weight to recieve a conformation message that an image has been loaded before sending a message to draw the image. To perform selective receive, the ``recieve`` function takes in a predicate, a function that returns a boolean value, and returns the oldest message in mailbox that satifies the predicate. Here is an example:

.. code-block:: python

    from chorus import me, receive, run_main, send

    def main():
        # add some message to my own mailbox
        send(me(), "info")
        send(me(), "reply")

        # selectively recieve "reply"
        reply = receive(lambda msg: msg[0] == "reply")

        # print out "reply" then "info"
        print(f"Selected: {reply}")
        print(f"Remaining: {receive()}")

    run(main)
