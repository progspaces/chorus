import math
import time
import tkinter as tk
from random import randint, uniform

from chorus import me, process_pending, run_main, spawn
from chorus.dispatch.proxy import Proxy

WIDTH = 800
HEIGHT = 600
NUM_CICLES = 10
SPEED = 1.0


def random_position():
    x = randint(0, WIDTH)
    y = randint(0, HEIGHT)
    return x, y


def random_unit_vector():
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
    dx, dy = random_unit_vector()

    # Loop every 60th of a second.
    while True:
        # Move the circle by the velocity.
        canvas.tell.move(circle_id, dx * SPEED, dy * SPEED)

        # Wait until the next frame.
        time.sleep(1 / 60)


def main():
    # Setup a tkinter canvas.
    root = tk.Tk()
    canvas = tk.Canvas(root, width=800, height=600)
    canvas.pack()

    # Spawn some actors that will draw the circles.
    for _ in range(NUM_CICLES):
        spawn(draw_circle, Proxy(me()))

    # Declare the event loop.
    def process_draw_messages():
        process_pending([canvas])
        root.after(16, process_draw_messages)

    # Start the event loop.
    root.after(16, process_draw_messages)
    root.mainloop()


if __name__ == "__main__":
    run_main(main)
