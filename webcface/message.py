from __future__ import annotations
import msgpack
from typing import Tuple


class MessageBase:
    kind_def = -1
    kind: int
    msg: dict

    def __init__(self, kind: int, msg: dict):
        self.kind = kind
        self.msg = msg


class SyncInit(MessageBase):
    kind_def = 80

    def __init__(self, msg: dict) -> None:
        super().__init__(self.kind_def, msg)

    @staticmethod
    def new(M: str, l: str, v: str) -> SyncInit:
        return SyncInit({"M": M, "m": 0, "l": l, "v": v, "a": ""})

    @property
    def member_name(self) -> str:
        return self.msg["M"]

    @property
    def member_id(self) -> int:
        return self.msg["m"]

    @property
    def lib_name(self) -> str:
        return self.msg["l"]

    @property
    def lib_ver(self) -> str:
        return self.msg["v"]

    @property
    def addr(self) -> str:
        return self.msg["a"]


class SvrVersion(MessageBase):
    kind_def = 88

    def __init__(self, msg: dict) -> None:
        super().__init__(self.kind_def, msg)

    @property
    def svr_name(self) -> str:
        return self.msg["n"]

    @property
    def ver(self) -> str:
        return self.msg["v"]


message_classes = [
    SyncInit,
    SvrVersion,
]


def pack(msgs: list[MessageBase]) -> bytes:
    send_msgs: list[int | dict] = []
    for m in msgs:
        send_msgs.append(m.kind)
        send_msgs.append(m.msg)
    return msgpack.packb(send_msgs)


def unpack(packed: bytes) -> list[MessageBase]:
    unpack_obj = msgpack.unpackb(packed)
    assert len(unpack_obj) % 2 == 0
    msg_ret = []
    for i in range(0, len(unpack_obj), 2):
        kind = unpack_obj[i]
        msg = unpack_obj[i + 1]
        assert isinstance(kind, int)
        assert isinstance(msg, dict)
        for C in message_classes:
            if kind == C.kind_def:
                msg_ret.append(C(msg))
    return msg_ret
