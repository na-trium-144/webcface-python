import threading
import time
from typing import Optional, List
from pytest import fixture
from webcface.client_data import SyncDataStore2, SyncDataStore1, ClientData
from webcface.client import Client
import webcface.client_impl
import webcface.message

self_name = "test"


@fixture
def s2():
    return SyncDataStore2[str](self_name)


@fixture
def s1():
    return SyncDataStore1[str](self_name)


@fixture
def data():
    return ClientData(self_name)


@fixture
def wcli():
    c = Client(self_name)

    def loop():
        while not c._closing:
            time.sleep(0.1)

    c._reconnect_thread = threading.Thread(target=lambda: loop(), daemon=True)
    c._send_thread = threading.Thread(target=lambda: loop(), daemon=True)
    c.connected = True
    return c


def check_sent(wcli: Client, MsgClass: type) -> Optional[webcface.message.MessageBase]:
    for mg in wcli._data_check()._msg_queue:
        for m in mg:
            if isinstance(m, MsgClass) and isinstance(m, webcface.message.MessageBase):
                return m
    return None


def clear_sent(wcli: Client) -> None:
    wcli._data_check().clear_msg()


def send_back(wcli: Client, msgs: List[webcface.message.MessageBase]) -> None:
    webcface.client_impl.on_recv(wcli, wcli._data_check(), webcface.message.pack(msgs))
