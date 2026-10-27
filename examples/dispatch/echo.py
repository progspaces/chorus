from typing import Any

from chorus import run, spawn_server


class EchoHandler:
    def echo(self, message: Any) -> Any:
        return message


def main():
    proxy = spawn_server(EchoHandler())
    result = proxy.ask.echo("hello")
    print(result)  # 'hello'
    proxy.kill()


if __name__ == "__main__":
    run(main)
