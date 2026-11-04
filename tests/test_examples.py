import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
OUTPUTS = {
    "dispatch/counter.py": "3",
    "dispatch/echo.py": "hello",
    "dispatch/proxy_counter.py": "3",
    "messaging/echo.py": "received: hello",
    "runtime/counter.py": "Counter is at 3",
    "runtime/echo.py": "received: hello",
    "runtime/main.py": "received: hello",
    "runtime/ping_pong.py": "Pong: Stopping...",
    "runtime/terminate.py": "terminated successfully.",
}


@pytest.mark.parametrize("example,expected", OUTPUTS.items())
def test_example(example, expected):
    result = subprocess.run(
        [sys.executable, str(ROOT / "examples" / example)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert result.returncode == 0, result.stderr
    # Uncaught actor thread exceptions can still leave a zero process exit code.
    assert result.stderr == ""
    assert expected in result.stdout


@pytest.mark.parametrize("close_immediately", [False, True])
def test_drawing_example(close_immediately):
    # Exercise real actors and dispatch without requiring a display or Tk install.
    script = """
import runpy
import sys
import threading
import time
from types import SimpleNamespace

roots = []
canvases = []

class Root:
    def __init__(self):
        self.callbacks = []
        self.closed = False
        self.destroyed = False
        roots.append(self)

    def protocol(self, name, callback):
        assert name == 'WM_DELETE_WINDOW'
        self.close = callback

    def after(self, delay, callback):
        self.callbacks.append(callback)

    def mainloop(self):
        deadline = time.monotonic() + 0.15
        while sys.argv[1] == 'False' and time.monotonic() < deadline:
            self.callbacks.pop(0)()
            time.sleep(0.001)
        self.close()
        assert self.closed

    def quit(self):
        self.closed = True

    def destroy(self):
        self.destroyed = True

class Canvas:
    def __init__(self, root, width, height):
        self.circles = 0
        self.moves = 0
        canvases.append(self)

    def pack(self):
        pass

    def create_oval(self, x1, y1, x2, y2, fill):
        assert threading.current_thread() is threading.main_thread()
        assert not roots[0].destroyed
        self.circles += 1
        return self.circles

    def move(self, circle_id, dx, dy):
        assert threading.current_thread() is threading.main_thread()
        assert not roots[0].destroyed
        assert 1 <= circle_id <= self.circles
        self.moves += 1

sys.modules['tkinter'] = SimpleNamespace(Tk=Root, Canvas=Canvas)
example = runpy.run_path('examples/dispatch/drawing.py', run_name='__main__')
assert roots[0].destroyed
assert canvases[0].circles == example['NUM_CIRCLES']
if sys.argv[1] == 'False':
    assert canvases[0].moves > 0
"""
    result = subprocess.run(
        [sys.executable, "-c", script, str(close_immediately)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert result.returncode == 0, result.stderr
    assert result.stderr == ""
