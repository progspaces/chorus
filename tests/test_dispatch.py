import pytest

from chorus import (
    ActorSystem,
    Call,
    Invoke,
    Kill,
    Raise,
    Return,
    ask,
    me,
    process_pending,
    receive,
    register_thread_as_actor,
    run_main,
    spawn_server_with_proxy,
    tell,
    unregister_thread_as_actor,
)


class Counter:
    def __init__(self):
        self.value = 0

    def increment(self, amount=1, *, multiplier=1):
        self.value += amount * multiplier
        return self.value

    def fail(self):
        raise ValueError("counter failure")


def test_pending_dispatch_does_not_block_and_processes_invocations():
    def main():
        counter = Counter()
        assert process_pending([counter]) is True
        tell(me(), Invoke("increment", args=(3,), kwargs={"multiplier": 2}))
        assert process_pending([counter]) is True
        assert counter.value == 6
        tell(me(), Kill())
        assert process_pending([counter]) is False

    run_main(main)


def test_server_correlates_success_and_error_responses():
    def main():
        proxy = spawn_server_with_proxy([Counter()])
        try:
            response = ask(proxy.target_id, Call("increment"), timeout=2)
            assert isinstance(response, Return)
            assert response.result == 1
            response = ask(proxy.target_id, Call("fail"), timeout=2)
            assert isinstance(response, Raise)
            assert isinstance(response.reason, ValueError)
        finally:
            proxy.kill()

    run_main(main)


def test_proxy_passes_arguments_and_unwraps_responses():
    def main():
        proxy = spawn_server_with_proxy([Counter()])
        try:
            proxy.tell.increment(2, multiplier=3)
            assert proxy.ask.increment(4, multiplier=2) == 14
            with pytest.raises(ValueError, match="counter failure"):
                proxy.ask.fail()
        finally:
            proxy.kill()

    run_main(main)


def test_main_thread_registration_and_cleanup():
    system = ActorSystem()
    actor_id = register_thread_as_actor(system)
    try:
        assert me() == actor_id
    finally:
        unregister_thread_as_actor(system, actor_id)
    assert not system.actors
    with pytest.raises(AttributeError):
        me()

    with pytest.raises(ValueError, match="main failure"):
        run_main(lambda: (_ for _ in ()).throw(ValueError("main failure")))
    with pytest.raises(AttributeError):
        receive(block=False)
