from __future__ import annotations
from typing import Dict
import datetime
import msgpack
import webcface.func_info
import webcface.view_base
import webcface.field


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


class Sync(MessageBase):
    kind_def = 87

    def __init__(self, msg: dict) -> None:
        super().__init__(self.kind_def, msg)

    @staticmethod
    def new() -> Sync:
        return Sync({"m": 0, "t": int(datetime.datetime.now().timestamp() * 1000)})

    @property
    def member_id(self) -> int:
        return self.msg["m"]

    @property
    def time(self) -> datetime.datetime:
        return datetime.datetime.fromtimestamp(self.msg["t"] / 1000)


class Value(MessageBase):
    kind_def = 0

    def __init__(self, msg: dict) -> None:
        super().__init__(self.kind_def, msg)

    @staticmethod
    def new(f: str, d: list[float]) -> Value:
        return Value({"f": f, "d": d})


class ValueReq(MessageBase):
    kind_def = 40

    def __init__(self, msg: dict) -> None:
        super().__init__(self.kind_def, msg)

    @staticmethod
    def new(m: str, f: str, i: int) -> ValueReq:
        return ValueReq({"M": m, "f": f, "i": i})


class ValueRes(MessageBase):
    kind_def = 60

    def __init__(self, msg: dict) -> None:
        super().__init__(self.kind_def, msg)

    @property
    def req_id(self) -> int:
        return self.msg["i"]

    @property
    def sub_field(self) -> str:
        return self.msg["f"]

    @property
    def data(self) -> list[float]:
        return self.msg["d"]


class ValueEntry(MessageBase):
    kind_def = 20

    def __init__(self, msg: dict) -> None:
        super().__init__(self.kind_def, msg)

    @property
    def member_id(self) -> int:
        return self.msg["m"]

    @property
    def field(self) -> str:
        return self.msg["f"]


class Text(MessageBase):
    kind_def = 1

    def __init__(self, msg: dict) -> None:
        super().__init__(self.kind_def, msg)

    @staticmethod
    def new(f: str, d: str) -> Text:
        return Text({"f": f, "d": d})


class TextReq(MessageBase):
    kind_def = 41

    def __init__(self, msg: dict) -> None:
        super().__init__(self.kind_def, msg)

    @staticmethod
    def new(m: str, f: str, i: int) -> TextReq:
        return TextReq({"M": m, "f": f, "i": i})


class TextRes(MessageBase):
    kind_def = 61

    def __init__(self, msg: dict) -> None:
        super().__init__(self.kind_def, msg)

    @property
    def req_id(self) -> int:
        return self.msg["i"]

    @property
    def sub_field(self) -> str:
        return self.msg["f"]

    @property
    def data(self) -> str:
        return self.msg["d"]


class TextEntry(MessageBase):
    kind_def = 21

    def __init__(self, msg: dict) -> None:
        super().__init__(self.kind_def, msg)

    @property
    def member_id(self) -> int:
        return self.msg["m"]

    @property
    def field(self) -> str:
        return self.msg["f"]


class View(MessageBase):
    kind_def = 3

    def __init__(self, msg: dict) -> None:
        super().__init__(self.kind_def, msg)

    @staticmethod
    def new(f: str, d: Dict[str, webcface.view_base.ViewComponentBase], l: int) -> View:
        vd = {}
        for i, c in d.items():
            vd[i] = {
                    "t": c._type,
                    "x": c._text,
                    "L": None if c._on_click_func is None else c._on_click_func._member,
                    "l": None if c._on_click_func is None else c._on_click_func._field,
                    "c": c._text_color,
                    "b": c._bg_color,
                }
        return View({"f": f, "d": vd, "l": l})


class ViewReq(MessageBase):
    kind_def = 43

    def __init__(self, msg: dict) -> None:
        super().__init__(self.kind_def, msg)

    @staticmethod
    def new(m: str, f: str, i: int) -> ViewReq:
        return ViewReq({"M": m, "f": f, "i": i})


class ViewRes(MessageBase):
    kind_def = 63

    def __init__(self, msg: dict) -> None:
        super().__init__(self.kind_def, msg)

    @property
    def req_id(self) -> int:
        return self.msg["i"]

    @property
    def sub_field(self) -> str:
        return self.msg["f"]

    @property
    def data_diff(self) -> Dict[str, webcface.view_base.ViewComponentBase]:
        vc = {}
        for i, d in self.msg["d"].items():
            vc[i] = webcface.view_base.ViewComponentBase(
                    type=d["t"],
                    text=d["x"],
                    on_click=(
                        None
                        if d["L"] is None or d["l"] is None
                        else webcface.field.FieldBase(d["L"], d["l"])
                    ),
                    text_color=d["c"],
                    bg_color=d["b"],
                )
        return vc

    @property
    def length(self) -> int:
        return self.msg["l"]


class ViewEntry(MessageBase):
    kind_def = 23

    def __init__(self, msg: dict) -> None:
        super().__init__(self.kind_def, msg)

    @property
    def member_id(self) -> int:
        return self.msg["m"]

    @property
    def field(self) -> str:
        return self.msg["f"]


class FuncInfo(MessageBase):
    kind_def = 84

    def __init__(self, msg: dict) -> None:
        super().__init__(self.kind_def, msg)

    @staticmethod
    def new(f: str, fi: webcface.func_info.FuncInfo) -> FuncInfo:
        ad = []
        for a in fi.args:
            ad.append(
                {
                    "n": a.name,
                    "t": a.type,
                    "i": a.init,
                    "m": a.min,
                    "x": a.max,
                    "o": a.option,
                }
            )
        return FuncInfo({"m": 0, "f": f, "r": fi.return_type, "a": ad})

    @property
    def member_id(self) -> int:
        return self.msg["m"]

    @property
    def field(self) -> str:
        return self.msg["f"]

    @property
    def func_info(self) -> webcface.func_info.FuncInfo:
        args = []
        for a in self.msg["a"]:
            args.append(
                webcface.func_info.Arg(
                    name=a["n"],
                    type=a["t"],
                    init=a["i"],
                    min=a["m"],
                    max=a["x"],
                    option=a["o"],
                )
            )
        return webcface.func_info.FuncInfo(None, args, self.msg["r"])


class Call(MessageBase):
    kind_def = 81

    def __init__(self, msg: dict) -> None:
        super().__init__(self.kind_def, msg)

    @staticmethod
    def new(i: int, c: int, r: int, f: str, a: list[float | bool | str]) -> Call:
        return Call({"i": i, "c": c, "r": r, "f": f, "a": a})

    @property
    def caller_id(self) -> int:
        return self.msg["i"]

    @property
    def caller_member_id(self) -> int:
        return self.msg["c"]

    @property
    def target_member_id(self) -> int:
        return self.msg["r"]

    @property
    def field(self) -> str:
        return self.msg["f"]

    @property
    def args(self) -> list[float | bool | str]:
        return self.msg["a"]


class CallResponse(MessageBase):
    kind_def = 82

    def __init__(self, msg: dict) -> None:
        super().__init__(self.kind_def, msg)

    @staticmethod
    def new(i: int, c: int, s: bool) -> CallResponse:
        return CallResponse({"i": i, "c": c, "s": s})

    @property
    def caller_id(self) -> int:
        return self.msg["i"]

    @property
    def caller_member_id(self) -> int:
        return self.msg["c"]

    @property
    def started(self) -> bool:
        return self.msg["s"]


class CallResult(MessageBase):
    kind_def = 83

    def __init__(self, msg: dict) -> None:
        super().__init__(self.kind_def, msg)

    @staticmethod
    def new(i: int, c: int, e: bool, r: float | bool | str) -> CallResponse:
        return CallResponse({"i": i, "c": c, "e": e, "r": r})

    @property
    def caller_id(self) -> int:
        return self.msg["i"]

    @property
    def caller_member_id(self) -> int:
        return self.msg["c"]

    @property
    def is_error(self) -> bool:
        return self.msg["e"]

    @property
    def result(self) -> float | bool | str:
        return self.msg["r"]


# 受信する可能性のあるメッセージのリスト
message_classes_recv = [
    SyncInit,
    SvrVersion,
    Sync,
    ValueRes,
    ValueEntry,
    TextRes,
    TextEntry,
    ViewRes,
    ViewEntry,
    FuncInfo,
    Call,
    CallResponse,
    CallResult,
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
        for C in message_classes_recv:
            if kind == C.kind_def:
                msg_ret.append(C(msg))
    return msg_ret
