import math
import time
import tkinter as tk
from random import randint, uniform
from statistics import mean, median

import matplotlib.pyplot as plt

from chorus import Proxy, me, process_pending, run_main, spawn
from chorus.runtime.api import get_actor_system

TICK_LENGTH = 16

WIDTH = 800
HEIGHT = 600
NUM_CICLES = 10
SPEED = 1.0


class FrameTimer:
    def __init__(self) -> None:
        self.frame_times: list[int] = []
        self.actor_queue_len: list[int] = []
        self.then_ns: int | None = None

    def on_frame(self) -> None:
        now_ns = time.perf_counter_ns()
        if self.then_ns is not None:
            diff = now_ns - self.then_ns
            self.frame_times.append(diff)
            queue_lens = [
                len(actor.mailbox.messages)
                for actor in get_actor_system().actors.values()
            ]
            self.actor_queue_len.append(queue_lens)
            # if diff < 25_000_000:
            #     print(f"diff < 25_000_000 on frame {len(self.frame_times)}")
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
        # plt.plot(self.frame_times)
        # plt.show()

        queue_lens = [list(l) for l in zip(*self.actor_queue_len)]
        for qls in queue_lens:
            plt.plot(qls)
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
    while True:
        # Move the circle by the velocity.
        canvas.tell.move(circle_id, dx * SPEED, dy * SPEED)

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
    for _ in range(NUM_CICLES):
        spawn(draw_circle, Proxy(me()))

    # Time the main loop
    timer = FrameTimer()

    # Declare the event loop.
    def process_draw_messages():
        timer.on_frame()
        process_pending([canvas])
        root.after(TICK_LENGTH, process_draw_messages)

    # Start the event loop immediately.
    root.after(0, process_draw_messages)
    root.mainloop()

    # process the frame timings
    timer.print_summary()
    timer.plot()


if __name__ == "__main__":
    # Setup the main thread as a actor and call main.
    run_main(main)
