from __future__ import annotations
from typing import Dict, List, Union
import datetime
import msgpack
import webcface.func_info
import webcface.view_base
import webcface.canvas2d_base
import webcface.field
import webcface.log_handler


class MessageBase:
    kind_def = -1
    kind: int
    msg: dict

    def __init__(self, kind: int, msg: dict):
        self.kind = kind
        self.msg = msg


def time_to_int(t: datetime.datetime) -> int:
    return int(t.timestamp() * 1000)


def int_to_time(t: int) -> datetime.datetime:
    return datetime.datetime.fromtimestamp(t / 1000)


class SyncInit(MessageBase):
    kind_def = 80

    def __init__(self, msg: dict) -> None:
        super().__init__(self.kind_def, msg)

    @staticmethod
    def new(M: str, l: str, v: str) -> SyncInit:
        return SyncInit.new_full(M, 0, l, v, "")

    @staticmethod
    def new_full(M: str, m: int, l: str, v: str, a: str) -> SyncInit:
        return SyncInit({"M": M, "m": m, "l": l, "v": v, "a": a})

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


class SyncInitEnd(MessageBase):
    kind_def = 88

    def __init__(self, msg: dict) -> None:
        super().__init__(self.kind_def, msg)

    @staticmethod
    def new(n: str, v: str, m: int, h: str) -> SyncInitEnd:
        return SyncInitEnd({"n": n, "v": v, "m": m, "h": h})

    @property
    def svr_name(self) -> str:
        return self.msg["n"]

    @property
    def ver(self) -> str:
        return self.msg["v"]

    @property
    def member_id(self) -> int:
        return self.msg["m"]

    @property
    def hostname(self) -> str:
        return self.msg["h"]


class Ping(MessageBase):
    kind_def = 89

    def __init__(self, msg: dict) -> None:
        super().__init__(self.kind_def, msg)

    @staticmethod
    def new() -> Ping:
        return Ping({})


class PingStatus(MessageBase):
    kind_def = 90

    def __init__(self, msg: dict) -> None:
        super().__init__(self.kind_def, msg)

    @staticmethod
    def new(s: Dict[int, int]) -> PingStatus:
        return PingStatus({"s": s})

    @property
    def status(self) -> Dict[int, int]:
        return self.msg["s"]


class PingStatusReq(MessageBase):
    kind_def = 91

    def __init__(self, msg: dict) -> None:
        super().__init__(self.kind_def, msg)

    @staticmethod
    def new() -> PingStatusReq:
        return PingStatusReq({})


class Sync(MessageBase):
    kind_def = 87

    def __init__(self, msg: dict) -> None:
        super().__init__(self.kind_def, msg)

    @staticmethod
    def new() -> Sync:
        return Sync({"m": 0, "t": time_to_int(datetime.datetime.now())})

    @staticmethod
    def new_full(m: int, t: int) -> Sync:
        return Sync({"m": m, "t": t})

    @property
    def member_id(self) -> int:
        return self.msg["m"]

    @property
    def time(self) -> datetime.datetime:
        return int_to_time(self.msg["t"])


class Value(MessageBase):
    kind_def = 0

    def __init__(self, msg: dict) -> None:
        super().__init__(self.kind_def, msg)

    @staticmethod
    def new(f: str, d: List[float]) -> Value:
        return Value({"f": f, "d": d})

    @property
    def field(self) -> str:
        return self.msg["f"]

    @property
    def data(self) -> List[float]:
        return self.msg["d"]


class ValueReq(MessageBase):
    kind_def = 40

    def __init__(self, msg: dict) -> None:
        super().__init__(self.kind_def, msg)

    @staticmethod
    def new(m: str, f: str, i: int) -> ValueReq:
        return ValueReq({"M": m, "f": f, "i": i})

    @property
    def member(self) -> str:
        return self.msg["M"]

    @property
    def field(self) -> str:
        return self.msg["f"]

    @property
    def req_id(self) -> int:
        return self.msg["i"]


class ValueRes(MessageBase):
    kind_def = 60

    def __init__(self, msg: dict) -> None:
        super().__init__(self.kind_def, msg)

    @staticmethod
    def new(i: int, f: str, d: List[float]) -> ValueRes:
        return ValueRes({"i": i, "f": f, "d": d})

    @property
    def req_id(self) -> int:
        return self.msg["i"]

    @property
    def sub_field(self) -> str:
        return self.msg["f"]

    @property
    def data(self) -> List[float]:
        return self.msg["d"]


class ValueEntry(MessageBase):
    kind_def = 20

    def __init__(self, msg: dict) -> None:
        super().__init__(self.kind_def, msg)

    @staticmethod
    def new(m: int, f: str) -> ValueEntry:
        return ValueEntry({"m": m, "f": f})

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

    @property
    def field(self) -> str:
        return self.msg["f"]

    @property
    def data(self) -> str:
        return self.msg["d"]


class TextReq(MessageBase):
    kind_def = 41

    def __init__(self, msg: dict) -> None:
        super().__init__(self.kind_def, msg)

    @staticmethod
    def new(m: str, f: str, i: int) -> TextReq:
        return TextReq({"M": m, "f": f, "i": i})

    @property
    def member(self) -> str:
        return self.msg["M"]

    @property
    def field(self) -> str:
        return self.msg["f"]

    @property
    def req_id(self) -> int:
        return self.msg["i"]


class TextRes(MessageBase):
    kind_def = 61

    def __init__(self, msg: dict) -> None:
        super().__init__(self.kind_def, msg)

    @staticmethod
    def new(i: int, f: str, d: str) -> TextRes:
        return TextRes({"i": i, "f": f, "d": d})

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

    @staticmethod
    def new(m: int, f: str) -> TextEntry:
        return TextEntry({"m": m, "f": f})

    @property
    def member_id(self) -> int:
        return self.msg["m"]

    @property
    def field(self) -> str:
        return self.msg["f"]


def vb_to_vd(vb: Dict[str, webcface.view_base.ViewComponentBase]) -> dict:
    """ViewComponentBaseクラスからメッセージに変換"""
    vd = {}
    for i, b in vb.items():
        vd[i] = {
            "t": b._type,
            "x": b._text,
            "L": None if b._on_click_func is None else b._on_click_func._member,
            "l": None if b._on_click_func is None else b._on_click_func._field,
            "R": None if b._text_ref is None else b._text_ref._member,
            "r": None if b._text_ref is None else b._text_ref._field,
            "c": b._text_color,
            "b": b._bg_color,
            "im": b._min,
            "ix": b._max,
            "is": b._step,
            "io": b._option,
        }
    return vd


def vd_to_vb(vd: dict) -> Dict[str, webcface.view_base.ViewComponentBase]:
    """メッセージからViewComponentBaseクラスに変換"""
    vb = {}
    for i, d in vd.items():
        vb[i] = webcface.view_base.ViewComponentBase(
            type=d["t"],
            text=d["x"],
            on_click=(
                None
                if d.get("L") is None or d.get("l") is None
                else webcface.field.FieldBase(d["L"], d["l"])
            ),
            text_ref=(
                None
                if d.get("R") is None or d.get("r") is None
                else webcface.field.FieldBase(d["R"], d["r"])
            ),
            text_color=d["c"],
            bg_color=d["b"],
            min=d.get("im"),
            max=d.get("ix"),
            step=d.get("is"),
            option=d.get("io"),
        )
    return vb


class View(MessageBase):
    kind_def = 3

    def __init__(self, msg: dict) -> None:
        super().__init__(self.kind_def, msg)

    @staticmethod
    def new(f: str, d: Dict[str, webcface.view_base.ViewComponentBase], l: int) -> View:
        return View({"f": f, "d": vb_to_vd(d), "l": l})

    @property
    def field(self) -> str:
        return self.msg["f"]

    @property
    def data(self) -> Dict[str, webcface.view_base.ViewComponentBase]:
        return vd_to_vb(self.msg["d"])

    @property
    def length(self) -> int:
        return self.msg["l"]


class ViewReq(MessageBase):
    kind_def = 43

    def __init__(self, msg: dict) -> None:
        super().__init__(self.kind_def, msg)

    @staticmethod
    def new(m: str, f: str, i: int) -> ViewReq:
        return ViewReq({"M": m, "f": f, "i": i})

    @property
    def member(self) -> str:
        return self.msg["M"]

    @property
    def field(self) -> str:
        return self.msg["f"]

    @property
    def req_id(self) -> int:
        return self.msg["i"]


class ViewRes(MessageBase):
    kind_def = 63

    def __init__(self, msg: dict) -> None:
        super().__init__(self.kind_def, msg)

    @staticmethod
    def new(
        i: int, f: str, d: Dict[str, webcface.view_base.ViewComponentBase], l: int
    ) -> ViewRes:
        return ViewRes({"i": i, "f": f, "d": vb_to_vd(d), "l": l})

    @property
    def req_id(self) -> int:
        return self.msg["i"]

    @property
    def sub_field(self) -> str:
        return self.msg["f"]

    @property
    def data_diff(self) -> Dict[str, webcface.view_base.ViewComponentBase]:
        return vd_to_vb(self.msg["d"])

    @property
    def length(self) -> int:
        return self.msg["l"]


class ViewEntry(MessageBase):
    kind_def = 23

    def __init__(self, msg: dict) -> None:
        super().__init__(self.kind_def, msg)

    @staticmethod
    def new(m: int, f: str) -> ViewEntry:
        return ViewEntry({"m": m, "f": f})

    @property
    def member_id(self) -> int:
        return self.msg["m"]

    @property
    def field(self) -> str:
        return self.msg["f"]


def c2b_to_c2d(vb: Dict[str, webcface.canvas2d_base.Canvas2DComponentBase]) -> dict:
    """Canvas2dComponentBaseクラスからメッセージに変換"""
    vd = {}
    for i, b in vb.items():
        vd[i] = {
            "t": b._type,
            "op": b._origin_pos,
            "or": b._origin_rot,
            "c": b._color,
            "f": b._fill,
            "s": b._stroke_width,
            "gt": b._geometry_type,
            "gp": b._geometry_properties,
        }
    return vd


def c2d_to_c2b(vd: dict) -> Dict[str, webcface.canvas2d_base.Canvas2DComponentBase]:
    """メッセージからCanvas2DComponentBaseクラスに変換"""
    vb = {}
    for i, d in vd.items():
        vb[i] = webcface.canvas2d_base.Canvas2DComponentBase(
            type=d["t"],
            origin_pos=d["op"],
            origin_rot=d["or"],
            color=d["c"],
            fill=d["f"],
            stroke_width=d["s"],
            geometry_type=d["gt"],
            geometry_properties=d["gp"],
        )
    return vb


class Canvas2D(MessageBase):
    kind_def = 4

    def __init__(self, msg: dict) -> None:
        super().__init__(self.kind_def, msg)

    @staticmethod
    def new(
        f: str,
        w: float,
        h: float,
        d: Dict[str, webcface.canvas2d_base.Canvas2DComponentBase],
        l: int,
    ) -> Canvas2D:
        return Canvas2D({"f": f, "w": w, "h": h, "d": c2b_to_c2d(d), "l": l})

    @property
    def field(self) -> str:
        return self.msg["f"]

    @property
    def width(self) -> float:
        return self.msg["w"]

    @property
    def height(self) -> float:
        return self.msg["h"]

    @property
    def data(self) -> Dict[str, webcface.canvas2d_base.Canvas2DComponentBase]:
        return c2d_to_c2b(self.msg["d"])

    @property
    def length(self) -> int:
        return self.msg["l"]


class Canvas2DReq(MessageBase):
    kind_def = 44

    def __init__(self, msg: dict) -> None:
        super().__init__(self.kind_def, msg)

    @staticmethod
    def new(m: str, f: str, i: int) -> Canvas2DReq:
        return Canvas2DReq({"M": m, "f": f, "i": i})

    @property
    def member(self) -> str:
        return self.msg["M"]

    @property
    def field(self) -> str:
        return self.msg["f"]

    @property
    def req_id(self) -> int:
        return self.msg["i"]


class Canvas2DRes(MessageBase):
    kind_def = 64

    def __init__(self, msg: dict) -> None:
        super().__init__(self.kind_def, msg)

    @staticmethod
    def new(
        i: int,
        f: str,
        w: float,
        h: float,
        d: Dict[str, webcface.canvas2d_base.Canvas2DComponentBase],
        l: int,
    ) -> Canvas2DRes:
        return Canvas2DRes({"i": i, "f": f, "w": w, "h": h, "d": c2b_to_c2d(d), "l": l})

    @property
    def req_id(self) -> int:
        return self.msg["i"]

    @property
    def sub_field(self) -> str:
        return self.msg["f"]

    @property
    def width(self) -> float:
        return self.msg["w"]

    @property
    def height(self) -> float:
        return self.msg["h"]

    @property
    def data_diff(self) -> Dict[str, webcface.canvas2d_base.Canvas2DComponentBase]:
        return c2d_to_c2b(self.msg["d"])

    @property
    def length(self) -> int:
        return self.msg["l"]


class Canvas2DEntry(MessageBase):
    kind_def = 24

    def __init__(self, msg: dict) -> None:
        super().__init__(self.kind_def, msg)

    @staticmethod
    def new(m: int, f: str) -> Canvas2DEntry:
        return Canvas2DEntry({"m": m, "f": f})

    @property
    def member_id(self) -> int:
        return self.msg["m"]

    @property
    def field(self) -> str:
        return self.msg["f"]


def c3b_to_c3d(vb: Dict[str, webcface.canvas3d_base.Canvas3DComponentBase]) -> dict:
    """Canvas3dComponentBaseクラスからメッセージに変換"""
    vd = {}
    for i, b in vb.items():
        vd[i] = {
            "t": b._type,
            "op": b._origin_pos,
            "or": b._origin_rot,
            "c": b._color,
            "gt": b._geometry_type,
            "gp": b._geometry_properties,
            "fm": b._field_member,
            "ff": b._field_field,
            "a": b._angles,
        }
    return vd


def c3d_to_c3b(vd: dict) -> Dict[str, webcface.canvas3d_base.Canvas3DComponentBase]:
    """メッセージからCanvas2DComponentBaseクラスに変換"""
    vb = {}
    for i, d in vd.items():
        vb[i] = webcface.canvas3d_base.Canvas3DComponentBase(
            type=d["t"],
            origin_pos=d["op"],
            origin_rot=d["or"],
            color=d["c"],
            geometry_type=d["gt"],
            geometry_properties=d["gp"],
            field_member=d["fm"],
            field_field=d["ff"],
            angles=d["a"],
        )
    return vb


class Canvas3D(MessageBase):
    kind_def = 7

    def __init__(self, msg: dict) -> None:
        super().__init__(self.kind_def, msg)

    @staticmethod
    def new(
        f: str,
        d: Dict[str, webcface.canvas3d_base.Canvas3DComponentBase],
        l: int,
    ) -> Canvas3D:
        return Canvas3D({"f": f, "d": c3b_to_c3d(d), "l": l})

    @property
    def field(self) -> str:
        return self.msg["f"]

    @property
    def data(self) -> Dict[str, webcface.canvas3d_base.Canvas3DComponentBase]:
        return c3d_to_c3b(self.msg["d"])

    @property
    def length(self) -> int:
        return self.msg["l"]


class Canvas3DReq(MessageBase):
    kind_def = 47

    def __init__(self, msg: dict) -> None:
        super().__init__(self.kind_def, msg)

    @staticmethod
    def new(m: str, f: str, i: int) -> Canvas3DReq:
        return Canvas3DReq({"M": m, "f": f, "i": i})

    @property
    def member(self) -> str:
        return self.msg["M"]

    @property
    def field(self) -> str:
        return self.msg["f"]

    @property
    def req_id(self) -> int:
        return self.msg["i"]


class Canvas3DRes(MessageBase):
    kind_def = 67

    def __init__(self, msg: dict) -> None:
        super().__init__(self.kind_def, msg)

    @staticmethod
    def new(
        i: int,
        f: str,
        d: Dict[str, webcface.canvas3d_base.Canvas3DComponentBase],
        l: int,
    ) -> Canvas3DRes:
        return Canvas3DRes({"i": i, "f": f, "d": c3b_to_c3d(d), "l": l})

    @property
    def req_id(self) -> int:
        return self.msg["i"]

    @property
    def sub_field(self) -> str:
        return self.msg["f"]

    @property
    def data_diff(self) -> Dict[str, webcface.canvas3d_base.Canvas3DComponentBase]:
        return c3d_to_c3b(self.msg["d"])

    @property
    def length(self) -> int:
        return self.msg["l"]


class Canvas3DEntry(MessageBase):
    kind_def = 27

    def __init__(self, msg: dict) -> None:
        super().__init__(self.kind_def, msg)

    @staticmethod
    def new(m: int, f: str) -> Canvas3DEntry:
        return Canvas3DEntry({"m": m, "f": f})

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
        return FuncInfo.new_full(0, f, fi)

    @staticmethod
    def new_full(m: int, f: str, fi: webcface.func_info.FuncInfo) -> FuncInfo:
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
        return FuncInfo({"m": m, "f": f, "r": fi.return_type, "a": ad})

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
        return webcface.func_info.FuncInfo(None, self.msg["r"], args)


class Call(MessageBase):
    kind_def = 81

    def __init__(self, msg: dict) -> None:
        super().__init__(self.kind_def, msg)

    @staticmethod
    def new(i: int, c: int, r: int, f: str, a: List[Union[float, bool, str]]) -> Call:
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
    def args(self) -> List[Union[float, bool, str]]:
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
    def new(i: int, c: int, e: bool, r: Union[float, bool, str]) -> CallResult:
        return CallResult({"i": i, "c": c, "e": e, "r": r})

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
    def result(self) -> Union[float, bool, str]:
        return self.msg["r"]


def msg2logline(lm: List[Dict]) -> List[webcface.log_handler.LogLine]:
    return [
        webcface.log_handler.LogLine(l["v"], int_to_time(l["t"]), l["m"]) for l in lm
    ]


def logline2msg(lls: List[webcface.log_handler.LogLine]) -> List[Dict]:
    return [{"v": ll.level, "t": time_to_int(ll.time), "m": ll.message} for ll in lls]


class Log(MessageBase):
    kind_def = 8

    def __init__(self, msg: dict) -> None:
        super().__init__(self.kind_def, msg)

    @staticmethod
    def new(f: str, lls: List[webcface.log_handler.LogLine]) -> Log:
        return Log(
            {
                "f": f,
                "l": logline2msg(lls),
            }
        )

    @property
    def field(self) -> str:
        return self.msg["f"]

    @property
    def log(self) -> List[webcface.log_handler.LogLine]:
        return msg2logline(self.msg["l"])


class LogRes(MessageBase):
    kind_def = 68

    def __init__(self, msg: dict) -> None:
        super().__init__(self.kind_def, msg)

    @staticmethod
    def new(i: int, f: str, lls: List[webcface.log_handler.LogLine]) -> LogRes:
        return LogRes(
            {
                "i": i,
                "f": f,
                "l": logline2msg(lls),
            }
        )

    @property
    def req_id(self) -> int:
        return self.msg["i"]

    @property
    def sub_field(self) -> str:
        return self.msg["f"]

    @property
    def log(self) -> List[webcface.log_handler.LogLine]:
        return msg2logline(self.msg["l"])


class LogReq(MessageBase):
    kind_def = 48

    def __init__(self, msg: dict) -> None:
        super().__init__(self.kind_def, msg)

    @staticmethod
    def new(m: str, f: str, i: int) -> LogReq:
        return LogReq({"M": m, "f": f, "i": i})

    @property
    def member(self) -> str:
        return self.msg["M"]

    @property
    def field(self) -> str:
        return self.msg["f"]

    @property
    def req_id(self) -> int:
        return self.msg["i"]


class LogEntry(MessageBase):
    kind_def = 28

    def __init__(self, msg: dict) -> None:
        super().__init__(self.kind_def, msg)

    @staticmethod
    def new(m: int, f: str) -> LogEntry:
        return LogEntry({"m": m, "f": f})

    @property
    def member_id(self) -> int:
        return self.msg["m"]

    @property
    def field(self) -> str:
        return self.msg["f"]


# 受信する可能性のあるメッセージのリスト
message_classes_recv = [
    SyncInit,
    SyncInitEnd,
    Ping,
    PingStatus,
    Sync,
    ValueRes,
    ValueEntry,
    TextRes,
    TextEntry,
    ViewRes,
    ViewEntry,
    Canvas2DRes,
    Canvas2DEntry,
    Canvas3DRes,
    Canvas3DEntry,
    FuncInfo,
    Call,
    CallResponse,
    CallResult,
    LogEntry,
    LogRes,
]


def pack(msgs: List[MessageBase]) -> bytes:
    send_msgs: List[Union[int, dict]] = []
    for m in msgs:
        send_msgs.append(m.kind)
        send_msgs.append(m.msg)
    return msgpack.packb(send_msgs)


def unpack(packed: bytes) -> List[MessageBase]:
    unpack_obj = msgpack.unpackb(packed, strict_map_key=False)
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
