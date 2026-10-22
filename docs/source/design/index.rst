Design
======
Chorus is a Python package that implements a version of the `Actor model <https://en.wikipedia.org/wiki/Actor_model>`_ ontop of Python's built-in Threading package. This section of the documentation discusses the motivation and design of the package.

This section has the following parts:

* :doc:`actors` discusses the actor model, it's trade-offs, and alternatives.
* :doc:`chorus` explain the design of the implementation of the Erlang actors API that Chorus provides as it's core functionality.

Chorus is designed with the following concerns in mind:

1. Keep the API as consise and simple as possible. There should be a minimal set of orthogonal composible functionality.
2. Don't reinvent anything. Steal proven designs from other languages and libraries.
3. Don't make choices you don't need to. For example, the API will accept any Python value as a message.
4. Layer complexity. The package has a minimal core and functionality is built ontop of that with the dependencies going from top to bottom only.