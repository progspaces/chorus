from dataclasses import dataclass

from chorus import (
    Call,
    Error,
    Invoke,
    Kill,
    Success,
    ask,
    run,
    spawn_server_with_proxy,
    tell,
)


@dataclass
class Counter:
    n: int

    def increment(self):
        self.n = self.n + 1

    def get(self):
        return self.n


def main():
    # spawn the counter actor
    counter_id = spawn_server_with_proxy([Counter(n=0)]).target_id

    # increment the counter 3 times
    tell(counter_id, Invoke(name="increment"))
    tell(counter_id, Invoke(name="increment"))
    tell(counter_id, Invoke(name="increment"))

    # get the count
    response = ask(counter_id, Call(name="get"))
    match response:
        case Success(result):
            print(result)
        case Error(reason):
            raise reason

    # kill the counter
    tell(counter_id, Kill())


if __name__ == "__main__":
    run(main)
