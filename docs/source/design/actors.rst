
Actors
======
The Actors structure communications between concurrently executing computations to avoid the need for shared state or global coordination.

These concerns are closely related to the concerns the object-oriented programming addresses. Both encapsulate state using message passing. In a sense, Actors are an extension of OOP into concurrency. One way to think of an actor is as an object that runs in it's own thread.

The Erlang actors API
---------------------
The most successful implementation of actors is in the Erlang programming langauge. Erlang is a function lanaguage with a syntax derived from Prolog which can make it a little hard to read comming from Python or Java. However, it is also a relatively small lanaguage. It's version of the actor model can be understood as consisting of the following concepts:

* Process
* Mailbox
* spawn
* send
* recieve

Here is an example from the Erlang website:

Discuss OTP and how it can be distributed.

Limitations of Actors
---------------------
It is worth noting that actors do not solve all the concurrency issues:

*  Race conditions: they prevent race conditions where threads try to access the same data in different orders and this causes a bug but actors can still execute is different orders meaning logical race conditions are possible and require coordination (using request-reply messages for example). An example (from an actor based rendering system) might be an actor updates a shapes properties before it is created by another actor and this fails.
*  Deadlocks: Actors can still get stuck waiting for a message that never arrives. Timeouts and the correct handling of timeouts can improve this, if adding those is worth the complexity.
*  Coordination of state: orginising shared state (say a fact store) still requires protocols and some model of transactions. Actors gives you kind of little computers that run in their own bits of the world and a way for them to talk to each other, it doesn't control what is said. It's a state isolation and addressing mechanism and that is about it.

Alternatives to Actors
----------------------
There are 

Other Python Actor Libraries
----------------------------
