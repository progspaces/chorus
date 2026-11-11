import math
import time
import tkinter as tk
from random import randint, uniform
from statistics import mean, median

import matplotlib.pyplot as plt

from chorus import Proxy, me, process_pending, run_main, send, spawn
from chorus.runtime.api import receive
from chorus.runtime.system import ActorID, ActorNotFoundError

FRAMES_PER_SECOND = 30
NS_PER_FRAME = 1_000_000_000 // FRAMES_PER_SECOND

WIDTH = 800
HEIGHT = 600
NUM_CIRCLES = 10
SPEED = 1.0


class FrameTimer:
    def __init__(self) -> None:
        self.frame_times: list[int] = []
        self.then_ns: int | None = None

    def on_frame(self) -> None:
        now_ns = time.perf_counter_ns()
        if self.then_ns is not None:
            self.frame_times.append(now_ns - self.then_ns)
        self.then_ns = now_ns

    def print_summary(self) -> None:
        NS_PER_MS = 1_000_000
        print("Frame times")
        print("-----------")
        print("mean ms:\t", mean(self.frame_times) / NS_PER_MS)
        print("median ms:\t", median(self.frame_times) / NS_PER_MS)
        print("min ms:\t", min(self.frame_times) / NS_PER_MS)
        print("max ms:\t", max(self.frame_times) / NS_PER_MS)

    def plot(self):
        plt.plot(self.frame_times)
        plt.show()


def random_position():
    x = randint(0, WIDTH)
    y = randint(0, HEIGHT)
    return x, y


def random_direction():
    angle = uniform(0, math.tau)
    dx = math.cos(angle)
    dy = math.sin(angle)
    return dx, dy


def draw_circle(canvas: Proxy):
    # Create a cicile at a random point in the window.
    radius = 16
    x, y = random_position()
    circle_id = canvas.ask.create_oval(
        x - radius, y - radius, x + radius, y + radius, fill="blue"
    )

    # Create a random unit vector to act a velocity.
    dx, dy = random_direction()

    # Loop every 60th of a second.
    running = True
    while running:
        match receive(block=False):
            case "kill":
                running = False
            case None:
                pass
            case _:
                print("Unknown message")

        # Move the circle by the velocity.
        try:
            canvas.tell.move(circle_id, dx * SPEED, dy * SPEED)
        except ActorNotFoundError:
            # TODO: this stops all the shutdown spam but we should handle else where
            pass

        # Wait until the next frame.
        time.sleep(1 / 60)


def main():
    # Setup a tkinter canvas.
    root = tk.Tk()

    # Fix for MacOS not exiting the mainloop on quit.
    if root.tk.call("tk", "windowingsystem") == "aqua":
        root.createcommand("tk::mac::Quit", root.destroy)

    canvas = tk.Canvas(root, width=800, height=600)
    canvas.pack()

    # Spawn some actors that will draw the circles.
    circles: list[ActorID] = []
    for _ in range(NUM_CIRCLES):
        actor_id = spawn(draw_circle, Proxy(me()))
        circles.append(actor_id)

    now_ns = time.perf_counter_ns()
    next_frame_ns = now_ns + NS_PER_FRAME

    # Time the main loop
    timer = FrameTimer()

    # Declare the event loop.
    def process_draw_messages():
        nonlocal next_frame_ns
        timer.on_frame()
        process_pending([canvas])
        now_ns = time.perf_counter_ns()
        if next_frame_ns < now_ns:
            delta_ns = now_ns - next_frame_ns
            num_missed_frames = delta_ns // NS_PER_FRAME + 1
            next_frame_ns += num_missed_frames * NS_PER_FRAME
        delta_ns = next_frame_ns - now_ns

        # round up so if there is a sub ms delay, we get some delay
        delay_ms = max(0, math.ceil(delta_ns / 1_000_000))
        root.after(delay_ms, process_draw_messages)

    # Start the event loop immediately.
    root.after(0, process_draw_messages)
    root.mainloop()

    # Log the frame rate metrics.
    timer.print_summary()
    timer.plot()

    # Kill all the actors.
    for actor_id in circles:
        send(actor_id, "kill")


if __name__ == "__main__":
    # Setup the main thread as a actor and call main.
    run_main(main)
