from dataclasses import dataclass

from chorus import run, spawn_with_proxy


@dataclass
class Counter:
    n: int

    def incroment(self):
        self.n = self.n + 1

    def get(self):
        return self.n


def main():
    # spawn the counter actor
    counter = spawn_with_proxy(Counter(n=0))

    # incroment the counter 3 times
    counter.tell.incroment()
    counter.tell.incroment()
    counter.tell.incroment()

    # get the count
    count = counter.ask.get()
    print(count)

    # kill the counter
    counter.kill()


if __name__ == "__main__":
    run(main)
