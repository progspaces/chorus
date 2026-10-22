import time
import tkinter as tk

from chorus import ActorID, me, run_main, send, spawn
from chorus.services.router import handle_all_messages

root = tk.Tk()
canvas = tk.Canvas(root, width=800, height=600)
canvas.pack()


def cicle_actor(main_id: ActorID):
    x, y = 0, 0
    while True:
        # pause for a second
        time.sleep(0.1)

        # draw a circle
        send(main_id, ("circle", x, y, 16))

        # move
        x += 1
        y += 1


def handle_drawing_messages():
    handle_all_messages(canvas)
    root.after(16, handle_drawing_messages)


def main():
    cicle_id = spawn(cicle_actor, me())
    send(cicle_id, ("main_id", me()))
    root.after(16, handle_drawing_messages)
    root.mainloop()


if __name__ == "__main__":
    run_main(main)
