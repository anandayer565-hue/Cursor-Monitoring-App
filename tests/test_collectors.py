"""Parser and mocked SSH collector tests."""

from app.collectors import (
    collect_metrics,
    parse_cpu,
    parse_disk,
    parse_load,
    parse_memory,
    parse_network,
    parse_ncpu,
    parse_ports,
    parse_processes,
    parse_uptime,
)
from app.ssh_client import SSHCredentials, SSHError, connect_ssh
from unittest.mock import MagicMock
import pytest


def test_parsers():
    assert parse_cpu("42.50\n") == 42.5
    assert parse_memory("80.00 800 1000")["percent"] == 80.0
    assert parse_load("0.10 0.20 0.30 1/2 3")["1m"] == 0.1
    assert parse_uptime("12345.67") == 12345
    assert parse_disk("55 100 200")["percent"] == 55.0
    assert parse_network("10 20") == {"rx_bytes": 10, "tx_bytes": 20}
    assert parse_ncpu("4\n") == 4
    assert len(parse_ports("LISTEN 0 128 127.0.0.1:5000\n")) == 1
    procs = parse_processes("PID USER %CPU %MEM COMMAND\n1 root 0.0 0.1 systemd\n")
    assert procs[0]["command"] == "systemd"


def test_connect_requires_auth():
    with pytest.raises(SSHError):
        connect_ssh(SSHCredentials("127.0.0.1", 22, "u"))


def test_connect_success_mocked():
    fake_client = MagicMock()
    factory = MagicMock(return_value=fake_client)
    client = connect_ssh(
        SSHCredentials("127.0.0.1", 22, "u", password="p"),
        client_factory=factory,
    )
    fake_client.connect.assert_called_once()
    kwargs = fake_client.connect.call_args.kwargs
    assert kwargs["allow_agent"] is False
    assert kwargs["password"] == "p"
    assert client is fake_client


def test_connect_failure_mocked():
    fake_client = MagicMock()
    fake_client.connect.side_effect = OSError("refused")
    factory = MagicMock(return_value=fake_client)
    with pytest.raises(SSHError):
        connect_ssh(
            SSHCredentials("127.0.0.1", 22, "u", password="p"),
            client_factory=factory,
        )


def test_collect_metrics_mocked():
    outputs = {
        "grep 'cpu '": "10.00",
        "MemTotal": "50.00 500 1000",
        "loadavg": "0.5 0.4 0.3 1/100 1",
        "uptime": "100",
        "df -P": "40 1 2",
        "net/dev": "9 8",
        "ss -lntuH": "LISTEN :22",
        "ps -eo": "PID USER %CPU %MEM COMMAND\n1 u 1.0 2.0 bash\n",
        "nproc": "2",
    }

    def run(_client, command):
        for key, val in outputs.items():
            if key in command:
                return val
        return ""

    connect = MagicMock(return_value=MagicMock())
    creds = SSHCredentials("127.0.0.1", 22, "u", password="p")
    data = collect_metrics(creds, connect=connect, run=run)
    assert data["cpu_percent"] == 10.0
    assert data["cpu_count"] == 2
    assert data["processes"][0]["command"] == "bash"
    connect.return_value.close.assert_called_once()
