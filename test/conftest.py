import threading
from typing import Optional
from pytest import fixture
from SimpleWebSocketServer import SimpleWebSocketServer, WebSocket
from webcface.client_data import SyncDataStore2, SyncDataStore1, ClientData
from webcface.client import Client
from webcface.message import MessageBase, unpack, pack

self_name = "test"
test_port = 47530


@fixture
def s2() -> SyncDataStore2[str]:
    return SyncDataStore2[str](self_name)


@fixture
def s1() -> SyncDataStore1[str]:
    return SyncDataStore1[str](self_name)


@fixture
def data() -> ClientData:
    return ClientData(self_name)


@fixture
def client():
    wcli = Client(self_name, "127.0.0.1", test_port)
    yield wcli
    wcli.close()


class DummyServer:
    wss_recv: list[MessageBase]
    connected: bool
    connected_socket: Optional[WebSocket]
    server: SimpleWebSocketServer
    server_thread: threading.Thread

    def __init__(self) -> None:
        self.wss_recv = []
        self.connected = False
        self.closing = False
        self.connected_socket = None
        s = self

        class DummySocket(WebSocket):
            def handleMessage(self):
                print("--message")
                s.wss_recv += unpack(self.data)

            def handleConnected(self):
                print("--connected")
                s.connected = True
                s.connected_socket = self

            def handleClose(self):
                print("--closed")
                s.connected = False

        self.server = SimpleWebSocketServer("0.0.0.0", test_port, DummySocket)
        self.server_thread = threading.Thread(target=self.server.serveforever)
        self.server_thread.start()

    def send(self, msg: list[MessageBase]) -> None:
        if self.connected_socket is not None:
            self.connected_socket.send_message(pack(msg))

    def shutdown(self) -> None:
        self.connected_socket = None
        self.server.close()


@fixture
def dummy_server():
    ds = DummyServer()
    yield ds
    ds.shutdown()

