import math
import time
import tkinter as tk
from random import randint, uniform
from statistics import mean, median

import matplotlib.pyplot as plt

TICK_LENGTH = 2

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
            diff = now_ns - self.then_ns
            self.frame_times.append(diff)
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


def create_circle(canvas):
    # Create a cicile at a random point in the window.
    radius = 16
    x, y = random_position()
    circle_id = canvas.create_oval(
        x - radius, y - radius, x + radius, y + radius, fill="blue"
    )
    # Create a random unit vector to act a velocity.
    dx, dy = random_direction()

    return circle_id, (dx, dy)


def update_circle(canvas, circle_id, dir):
    # Move the circle by the velocity.
    dx, dy = dir
    x0, y0, x1, y1 = canvas.coords(circle_id)
    canvas.coords(circle_id, x0 + dx, y0 + dy, x1 + dx, y1 + dy)


def main():
    # Setup a tkinter canvas.
    root = tk.Tk()

    # Fix for MacOS not exiting the mainloop on quit.
    if root.tk.call("tk", "windowingsystem") == "aqua":
        root.createcommand("tk::mac::Quit", root.destroy)

    canvas = tk.Canvas(root, width=800, height=600)
    canvas.pack()

    # create the balls
    circles = [create_circle(canvas) for _ in range(NUM_CIRCLES)]

    # Time the main loop
    timer = FrameTimer()

    # Declare the event loop.
    def process_draw_messages():
        timer.on_frame()
        for circle in circles:
            update_circle(canvas, *circle)
        root.after(TICK_LENGTH, process_draw_messages)

    # Start the event loop immediately.
    root.after(0, process_draw_messages)
    root.mainloop()

    # process the frame timings
    timer.print_summary()
    timer.plot()


if __name__ == "__main__":
    main()
