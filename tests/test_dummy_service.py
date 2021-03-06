import os
import signal
from typing import Any
from run_test_service_helper import start_service


def test_dummy_service(monkeypatch: Any, capsys: Any, loop: Any) -> None:
    services, future = start_service('tests/services/dummy_service.py', monkeypatch)

    assert services is not None
    assert len(services) == 1
    instance = services.get('test_dummy')
    assert instance is not None
    assert instance.start is True
    assert instance.started is True
    assert instance.stop is False

    os.kill(os.getpid(), signal.SIGINT)
    loop.run_until_complete(future)

    assert instance.stop is True


def test_dummy_service_without_py_ending(monkeypatch: Any, capsys: Any, loop: Any) -> None:
    services, future = start_service('tests/services/dummy_service', monkeypatch)

    instance = services.get('test_dummy')
    assert instance is not None

    os.kill(os.getpid(), signal.SIGINT)
    loop.run_until_complete(future)
