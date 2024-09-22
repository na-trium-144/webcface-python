import threading
import time
import logging
import os
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
    logger = logging.getLogger(f"webcface_internal")
    handler = logging.StreamHandler()
    fmt = logging.Formatter("[%(levelname)s] %(message)s")
    handler.setFormatter(fmt)
    logger.addHandler(handler)
    if "WEBCFACE_TRACE" in os.environ:
        logger.setLevel(logging.DEBUG)
    elif "WEBCFACE_VERBOSE" in os.environ:
        logger.setLevel(logging.INFO)
    else:
        logger.setLevel(logging.CRITICAL + 1)
    return ClientData(self_name, logger, True)


@fixture
def wcli():
    c = Client(self_name)

    def loop():
        while not c._closing:
            time.sleep(0.1)

    def close():
        c._closing = True

    c._reconnect_thread = threading.Thread(target=lambda: loop(), daemon=True)
    c._send_thread = threading.Thread(target=lambda: loop(), daemon=True)
    c.close = close
    # c.connected = True
    c._data_check().connected = True
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
