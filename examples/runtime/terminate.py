import time

from chorus import spawn, terminate
from chorus.runtime.system import ActorSystem


def counter():
    count = 0
    while True:
        print(f"count is {count}")
        count += 1
    print("This is not printed.")


def main():
    with ActorSystem():
        counter_id = spawn(counter)
        time.sleep(0.005)
        terminate(counter_id)
        print("main complete!")


if __name__ == "__main__":
    main()
