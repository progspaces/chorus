import tkinter as tk
from threading import Event

from chorus import ActorID, me, receive, run_main, send, spawn


def circle_actor(main_id: ActorID, stop: Event, finished: Event):
    x, y = 0, 0
    try:
        while not stop.wait(0.1):
            send(main_id, ("circle", x, y, 16))
            x += 1
            y += 1
    finally:
        finished.set()


def main():
    root = tk.Tk()
    canvas = tk.Canvas(root, width=800, height=600)
    canvas.pack()
    stop = Event()
    finished = Event()
    spawn(circle_actor, me(), stop, finished)

    def process_draw_messages():
        while True:
            match receive(block=False):
                case ("circle", x, y, r):
                    canvas.create_oval(x - r, y - r, x + r, y + r)
                case None:
                    break
                case _:
                    print("Error: unknown message")
        root.after(16, process_draw_messages)

    try:
        root.after(16, process_draw_messages)
        root.mainloop()
    finally:
        stop.set()
        finished.wait()


if __name__ == "__main__":
    run_main(main)
