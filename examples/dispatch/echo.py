from typing import Any

from chorus import ActorSystem, spawn_service


class EchoHandler:
    def echo(self, message: Any) -> Any:
        return message


def main():
    proxy = spawn_service(EchoHandler())
    try:
        result = proxy.ask.echo("hello")
        print(result)  # 'hello'
    finally:
        proxy.kill()


if __name__ == "__main__":
    with ActorSystem():
        main()
