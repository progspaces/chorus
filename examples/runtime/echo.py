from chorus import me, receive, send, spawn
from chorus.runtime.system import ActorSystem


def echo():
    match receive():
        case (sender_id, msg):
            send(sender_id, msg)
            echo()
        case _:
            print("Echo: any other message means end.")


def main():
    with ActorSystem():
        echo_id = spawn(echo)
        send(echo_id, (me(), "hello"))
        msg = receive()
        print(f"received: {msg}")
        send(echo_id, "end")


if __name__ == "__main__":
    main()
