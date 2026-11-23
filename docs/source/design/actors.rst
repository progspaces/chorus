
Actors
======
Actors structure communications between concurrently executing computations to avoid the need for shared state or global coordination.

These concerns are closely related to the concerns that object-oriented programming addresses. Both encapsulate state using message passing. In a sense, Actors are an extension of OOP into concurrency. One way to think of an actor is as an object that runs in its own thread.

The Erlang actors API
---------------------
The most successful implementation of actors is in the Erlang programming language. Erlang is a functional language with a syntax derived from Prolog which can make it a little hard to read coming from Python or Java. However, it is also a relatively small language. Its version of the actor model can be understood as consisting of the following concepts:

* Process - Erlang processes are light-weight threads. Not managed by the OS but by the Erlang runtime. Switching between different processes is very cheap compared to OS threads meaning Erlang can support orders of magnitude more concurrent computations.
* Mailbox - In order to communicate with each other, each Process has a Mailbox. This is just a queue that is specific to the process, on to which any process can put a message. Messages are normally tuples in Erlang. 
* spawn - This function takes in a function, creates a new process, and executes the function on the process. It returns a process id (a.k.a a pid).
* send - The takes in a pid and a message and pushes the message onto the Mailbox with that pid. Any process can call this. In Erlang, this is written ```id ! message````
* receive - This blocks the process and waits for a message to be added to the Mailbox for the current process. When it is, it unblocks and return the message. Receive has a pattern matching clause that matches the incoming message. 

The concurrency section of the Erlang documentation has [documentation](https://www.erlang.org/doc/system/conc_prog.html) for these ideas hand how they are used in Erlang.

Here is an example of an Erlang program from that website:

.. code-block:: Erlang

    -module(tut15).

    -export([start/0, ping/2, pong/0]).

    ping(0, Pong_PID) ->
        Pong_PID ! finished,
        io:format("ping finished~n", []);

    ping(N, Pong_PID) ->
        Pong_PID ! {ping, self()},
        receive
            pong ->
                io:format("Ping received pong~n", [])
        end,
        ping(N - 1, Pong_PID).

    pong() ->
        receive
            finished ->
                io:format("Pong finished~n", []);
            {ping, Ping_PID} ->
                io:format("Pong received ping~n", []),
                Ping_PID ! pong,
                pong()
        end.

    start() ->
        Pong_PID = spawn(tut15, pong, []),
        spawn(tut15, ping, [3, Pong_PID]).

The idea here is not to give a full description but the show where the Chorus API is coming from. The Chorus runtime API does its best to be a direct translation of these ideas into Python.

Limitations of Actors
---------------------
It is worth noting that actors do not solve all the concurrency issues:

*  Race conditions: they prevent race conditions where threads try to access the same data in different orders and this causes a bug, but actors can still execute in different orders, meaning logical race conditions are possible and require coordination (using request-reply messages, for example). An example (from an actor-based rendering system) might be that an actor updates a shape's properties before it is created by another actor and this fails.
*  Deadlocks: Actors can still get stuck waiting for a message that never arrives. Timeouts and the correct handling of timeouts can improve this, if adding those is worth the complexity.
*  Coordination of state: organising shared state (say a fact store) still requires protocols and some model of transactions. Actors give you kind of little computers that run in their own bits of the world and a way for them to talk to each other; they don't control what is said. It's a state isolation and addressing mechanism and that is about it.

Other Python Actor Libraries
----------------------------
There are already quite a few actor libraries for Python:

* `Thepian <thespianpy.com/doc/>`_ is a complete actor system for Python that has an API similar to `Akka <https://akka.io/>`_. Chorus borrows the idea of an ActorSystem from Thespian but does not require a class for each type of actor. Chorus also borrows the `ask` and `tell` concepts for here.
* `Pykka <https://pykka.readthedocs.io/stable/>`_ - another implementation of an Akka-style API. Seem very mature.
*  `python-actors <https://pythonhosted.org/actors/>`_ - a nice and simple actor library that multiplexes message handling onto worker threads.