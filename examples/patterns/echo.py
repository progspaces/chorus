from chorus import run, spawn_with_proxy


class Echo:
    def reply(self, text):
        return text


def main():
    echo = spawn_with_proxy(Echo())
    text = echo.ask.reply("hello")
    print(f"recieved: {text}")
    echo.kill()


if __name__ == "__main__":
    run(main)
