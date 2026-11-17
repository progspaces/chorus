from dataclasses import dataclass

from chorus import spawn_service
from chorus.runtime.system import ActorSystem


@dataclass
class Counter:
    n: int

    def increment(self):
        self.n = self.n + 1

    def get(self):
        return self.n


def main():
    # spawn the counter actor
    counter = spawn_service(Counter(n=0))

    try:
        # increment the counter 3 times
        counter.tell.increment()
        counter.tell.increment()
        counter.tell.increment()

        # get the count
        count = counter.ask.get()
        print(count)
    finally:
        counter.kill()


if __name__ == "__main__":
    with ActorSystem():
        main()
