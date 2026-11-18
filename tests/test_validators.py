from app.validators import is_localhost_host, validate_ssh_port
import pytest


@pytest.mark.parametrize(
    "host,ok",
    [
        ("localhost", True),
        ("127.0.0.1", True),
        ("::1", True),
        ("LOCALHOST", True),
        ("192.168.1.10", False),
        ("evil.example", False),
        ("", False),
    ],
)
def test_localhost_only(host, ok):
    assert is_localhost_host(host) is ok


def test_validate_ssh_port():
    assert validate_ssh_port(22) == 22
    with pytest.raises(ValueError):
        validate_ssh_port(0)
    with pytest.raises(ValueError):
        validate_ssh_port(70000)
