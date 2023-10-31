from __future__ import annotations
from typing import Callable, Optional
from enum import IntEnum
from copy import deepcopy
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
    hidden: bool
    func_impl: Callable

    def __init__(self, func: Callable) -> None:
        self.func_impl = func
        self.hidden = False
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
        if self.data.is_self(self._member):
            self.data.func_store.set_send(self._field, FuncInfo(func))
        else:
            raise ValueError("Cannot set data to member other than self")

    @property
    def hidden(self) -> bool:
        func_info = self.data.func_store.get_recv(self._member, self._field)
        if func_info is None:
            raise ValueError("Func not set")
        return func_info.hidden

    @hidden.setter
    def hidden(self, h: bool) -> None:
        if self.data.is_self(self._member):
            func_info = self.data.func_store.get_recv(self._member, self._field)
            if func_info is None:
                raise ValueError("Func not set")
            func_info.hidden = h
        else:
            raise ValueError("Cannot set data to member other than self")

    def free(self) -> None:
        self.data.func_store.unset_recv(self._member, self._field)

    def run(self, *args) -> Optional[float | bool | str]:
        pass

    def runAsync(self, *args) -> Optional[float | bool | str]:
        pass

    def __call__(self, *args) -> Optional[float | bool | str]:
        return self.run(*args)

    @property
    def return_type(self) -> int:
        func_info = self.data.func_store.get_recv(self._member, self._field)
        if func_info is None:
            raise ValueError("Func not set")
        return func_info.return_type

    @property
    def args(self) -> list[Arg]:
        func_info = self.data.func_store.get_recv(self._member, self._field)
        if func_info is None:
            raise ValueError("Func not set")
        return deepcopy(func_info.args)


class AnonymousFunc:
    field_id = 0
    @staticmethod
    def field_name_tmp() -> str:
        AnonymousFunc.field_id += 1
        return f".tmp{AnonymousFunc.field_id}"

    base_init: bool
    _func: Callable
    base: Func

    def __init__(self, base: Optional[webcface.field.Field], callback: Callable) -> None:
        if base is not None:
            self.base = Func(base, self.field_name_tmp())
        else:
            
