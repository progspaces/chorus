from dataclasses import dataclass

from chorus import (
    Call,
    Error,
    Kill,
    Success,
    ask,
    spawn_service,
    tell,
)
from chorus.runtime.system import ActorSystem


@dataclass
class Counter:
    n: int

    def increment(self):
        self.n = self.n + 1

    def get(self):
        return self.n


def main():
    with ActorSystem():
        # spawn the counter actor
        counter_id = spawn_service(Counter(n=0)).target_id

        try:
            # increment the counter 3 times
            tell(counter_id, Call(name="increment"))
            tell(counter_id, Call(name="increment"))
            tell(counter_id, Call(name="increment"))

            # get the count
            response = ask(counter_id, Call(name="get", reply=True), timeout=2)
            match response:
                case Success(result):
                    print(result)
                case Error(reason):
                    raise reason
        finally:
            tell(counter_id, Kill())


if __name__ == "__main__":
    main()
