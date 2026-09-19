from chorus import me, receive, run, send, spawn


def counter(n: int):
    match receive():
        case "incroment":
            counter(n + 1)
        case ("get", sender_id):
            send(sender_id, ("count", n))
        case _:
            print("Counter: unknown message.")


def main():
    # spawn the counter actor
    counter_id = spawn(counter, 0)

    # incroment the counter 3 times
    send(counter_id, "incroment")
    send(counter_id, "incroment")
    send(counter_id, ("get", me()))

    # retrieve the count
    match receive():
        case ("count", n):
            print(f"Counter is at {n}")
        case _:
            print("main: unknown message.")


if __name__ == "__main__":
    run(main)
