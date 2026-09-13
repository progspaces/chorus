from chorus import ActorSystem, me, receive, send, spawn


def echo():
    match receive():
        case (sender_id, msg):
            send(sender_id, msg)
            echo()
        case _:
            print("Echo: any other message means end.")


def main():
    echo_id = spawn(echo)
    send(echo_id, (me(), "hello"))
    msg = receive()
    print(f"recieved: {msg}")
    send(echo_id, "end")


if __name__ == "__main__":
    ActorSystem().run(main)
