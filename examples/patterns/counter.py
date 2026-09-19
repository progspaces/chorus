from dataclasses import dataclass

from chorus import ask, kill, run, spawn_with_proxy, tell


@dataclass
class Counter:
    n: int

    def incroment(self):
        self.n = self.n + 1

    def get(self):
        return self.n


def main():
    # spawn the counter actor
    counter_id = spawn_with_proxy(Counter(n=0)).target_id

    # incroment the counter 3 times
    tell(counter_id, "incroment")
    tell(counter_id, "incroment")
    tell(counter_id, "incroment")

    # get the count
    count = ask(counter_id, "get")
    print(count)

    # kill the counter
    kill(counter_id)


if __name__ == "__main__":
    run(main)
