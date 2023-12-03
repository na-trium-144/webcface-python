from conftest import self_name, DummyServer
from webcface.client import Client
from time import sleep


def test_client_connection_by_start(client: Client, dummy_server: DummyServer) -> None:
    sleep(0.01)
    assert not dummy_server.connected
    assert not client.connected
    client.start()
    sleep(0.01)
    assert dummy_server.connected
    assert client.connected
