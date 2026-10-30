import time

from chorus import run_main, spawn, terminate


def counter():
    count = 0
    while True:
        print(f"count is {count}")
        count += 1


def main():
    counter_id = spawn(counter)
    time.sleep(0.005)
    terminate(counter_id)
    # print("main complete!")


if __name__ == "__main__":
    run_main(main)
