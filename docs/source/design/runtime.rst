Runtime
=======
Runtime provides the building blocks for the rest of the Chorus APIs. It implements
part of Erlang's processes API on top of Python's built-in threading package.
These are OS threads, managed and scheduled by the operating system, unlike
Erlang's processes, which are managed by its BEAM virtual machine. Python threads
share an address space, whereas Erlang processes do not. In Erlang, messages are
copied when they are added to a mailbox. In Chorus, Python objects are passed by
reference, so immutable values, such as frozen dataclasses, are good choices for
messages. BEAM is a custom VM designed for actors; Python is not.

The three core operations are ``spawn``, ``send``, and ``receive``. Each actor has
its own thread and mailbox.

The data model
--------------
The 

spawn: create an actor
----------------------
``spawn(target, *args, **kwargs)`` takes in a target function and any arguments to pass to that function. It then does the following:

1. 


send: put a message in another actor's mailbox
----------------------------------------------
``send(actor_id, message)``


receive: take a message from the current actor's mailbox
--------------------------------------------------------
``receive(predicate=None, block=True, timeout=None)``