Design
======
Chorus is a Python package that implements a version of the `Actor model <https://en.wikipedia.org/wiki/Actor_model>`_ on top of Python's built-in Threading package. This section of the documentation discusses the motivation and design of the package.

This section has the following parts:

.. toctree::
   :hidden:

   actors
   chorus

* :doc:`actors` discusses the actor model, its trade-offs, and alternatives.
* :doc:`chorus` explains the design of the implementation of the Erlang actors API that Chorus provides as its core functionality.

Chorus is designed with the following concerns in mind:

1. Keep the API as concise and simple as possible. There should be a minimal set of orthogonal, composable functionality.
2. Don't reinvent anything. Steal proven designs from other languages and libraries.
3. Don't make choices you don't need to. For example, the API will accept any Python value as a message.
4. Layer complexity. The package has a minimal core and functionality is built on top of that with the dependencies going from top to bottom only.
