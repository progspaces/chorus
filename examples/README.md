# Examples

Run examples from the repository root with the package installed, for example:

```sh
python examples/runtime/echo.py
python examples/messaging/echo.py
python examples/dispatch/proxy_counter.py
```

- `runtime/`: actors, raw messages, mailboxes, main-thread execution, and Tkinter drawing.
- `messaging/`: typed events and correlated request/reply exchanges using `tell` and `ask`.
- `dispatch/`: method dispatch, server proxies, and integration with a Tkinter event loop.

The drawing examples and `dispatch/nonblocking_main.py` require Tkinter and a graphical desktop. Close the window to stop them.
