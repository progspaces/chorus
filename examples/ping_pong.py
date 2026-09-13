# port of the ping pong examples from
# https://www.cosmiclearn.com/erlang/message-passing.php

from chorus import ActorID, ActorSystem, me, receive, send


def pong():
    match receive():
        case ("ping", ping_id):
            print("Pong: Got Ping. Replying...")
            send(ping_id, "pong")
            pong()
        case "stop":
            print("Pong: Stopping...")
        case _:
            print("Pong: unknown message received.")


def ping(n: int, pong_id: ActorID):
    if n <= 0:
        send(pong_id, "stop")
        print("Ping: Game over!")
    else:
        send(pong_id, ("ping", me()))
        match receive():
            case "pong":
                print(f"Ping: Got Pong. Remaining: {n}.")
                ping(n - 1, pong_id)
            case _:
                print("Ping: unknown message received.")


def main():
    system = ActorSystem()
    pong_id = system.run(pong)
    ping_id = system.run(ping, 3, pong_id)

    print(f"Ping pong is running. pong_id: {pong_id}, ping_id: {ping_id}")


if __name__ == "__main__":
    main()
