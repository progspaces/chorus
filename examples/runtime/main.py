from chorus import me, receive, run_main, send, spawn


# this example is about how to treat the main thread like an actor
def echo():
    match receive():
        case (sender_id, msg):
            send(sender_id, msg)
            echo()
        case _:
            print("Echo: any other message means end.")


def main():
    # the main thread can use the actor functions
    echo_id = spawn(echo)
    send(echo_id, (me(), "hello"))
    msg = receive()  # note - this is now blocking the main thread!
    print(f"received: {msg}")
    send(echo_id, "end")


if __name__ == "__main__":
    run_main(main)
