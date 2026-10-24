import tkinter as tk
from threading import Event

from chorus import ActorID, Invoke, me, process_pending, run_main, spawn, tell


def circle_actor(main_id: ActorID, stop: Event, finished: Event):
    x, y = 0, 0
    try:
        while not stop.wait(0.1):
            tell(
                main_id,
                Invoke(name="create_oval", args=(x - 16, y - 16, x + 16, y + 16)),
            )
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
        process_pending([canvas])
        root.after(16, process_draw_messages)

    try:
        root.after(16, process_draw_messages)
        root.mainloop()
    finally:
        stop.set()
        finished.wait()


if __name__ == "__main__":
    run_main(main)
