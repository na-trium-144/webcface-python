from __future__ import annotations
from typing import Callable, Optional
from enum import IntEnum
import inspect
import webcface.member
import webcface.field


class ValType(IntEnum):
    NONE = 0
    STRING = 1
    STR = 1
    BOOL = 2
    INT = 3
    FLOAT = 4


def get_type_enum(t: type) -> int:
    if t == int:
        return ValType.INT
    if t == float:
        return ValType.FLOAT
    if t == bool:
        return ValType.BOOL
    if t == str:
        return ValType.STRING
    if (
        t == inspect.Parameter.empty
        or t == inspect.Signature.empty
        or isinstance(None, t)
    ):
        return ValType.NONE
    print("unknown argument type")
    return ValType.STRING


class Arg:
    _name: str
    _type: int
    _min: Optional[float]
    _max: Optional[float]
    _init: Optional[float | bool | str]
    _option: list[float | str]

    def __init__(self, name: str = "") -> None:
        self._name = name
        self._type = 0
        self._min = None
        self._max = None
        self._init = None
        self._option = []

    @property
    def name(self) -> str:
        return self._name

    @property
    def type(self) -> int:
        return self._type

    @type.setter
    def type(self, t: int | type) -> None:
        if isinstance(t, int):
            self._type = t
        else:
            self._type = get_type_enum(t)

    @property
    def init(self) -> Optional[float | bool | str]:
        return self._init

    @init.setter
    def init(self, i: Optional[float | bool | str]) -> None:
        self._init = i


class FuncInfo:
    return_type: int
    args: list[Arg]
    func_impl: Callable

    def __init__(self, func: Callable) -> None:
        self.func_impl = func
        sig = inspect.signature(func)
        self.args = []
        for pname in sig.parameters:
            p = sig.parameters[pname]
            a = Arg(pname)
            a.type = p.annotation
            if p.default != inspect.Parameter.empty:
                a.init = p.default
            self.args.append(a)
        self.return_type = get_type_enum(sig.return_annotation)


class Func(webcface.field.Field):
    def __init__(self, base: webcface.field.Field, field: str = "") -> None:
        super().__init__(base.data, base._member, field if field != "" else base._field)

    @property
    def member(self) -> webcface.member.Member:
        return webcface.member.Member(self)

    @property
    def name(self) -> str:
        return self._field

    def set(self, func: Callable) -> None:
        self.data.func_store.setSend(FuncInfo(func))
