from chorus import me, receive, send, setup_main_thread, spawn


# this example is about how to treat the main thread like an actor
def echo():
    match receive():
        case (sender_id, msg):
            send(sender_id, msg)
            echo()
        case _:
            print("Echo: any other message means end.")


def main():
    # this call sets up an actors system and adds the main thread to it
    # the main thread can now spawn actors, send and receive messages
    setup_main_thread()

    # echo example on the main thread
    echo_id = spawn(echo)
    send(echo_id, (me(), "hello"))
    msg = receive()
    print(f"recieved: {msg}")
    send(echo_id, "end")


if __name__ == "__main__":
    main()
