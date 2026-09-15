import time
import tkinter as tk

from chorus import me, receive, run_main, send, spawn

root = tk.Tk()
canvas = tk.Canvas(root, width=800, height=600)
canvas.pack()


def cicle_actor(main_id):
    x, y = 0, 0
    while True:
        # pause for a second
        time.sleep(0.1)

        # draw a circle
        send(main_id, ("circle", x, y, 16))

        # move
        x += 1
        y += 1


def process_draw_messages():
    while True:
        match receive(block=False):
            case ("circle", x, y, r):
                canvas.create_oval(
                    x - r,
                    y - r,
                    x + r,
                    y + r,
                )
            case None:
                break
            case _:
                print("Error: unknown message")

    root.after(16, process_draw_messages)


def main():
    cicle_id = spawn(cicle_actor, me())
    send(cicle_id, ("main_id", me()))
    root.after(16, process_draw_messages)
    root.mainloop()


if __name__ == "__main__":
    run_main(main)
