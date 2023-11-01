from __future__ import annotations
from typing import Callable, Optional
from copy import deepcopy
import webcface.member
import webcface.field
import webcface.func_info


class Func(webcface.field.Field):
    def __init__(self, base: webcface.field.Field, field: str = "") -> None:
        super().__init__(base.data, base._member, field if field != "" else base._field)

    @property
    def member(self) -> webcface.member.Member:
        return webcface.member.Member(self)

    @property
    def name(self) -> str:
        return self._field

    def set(
        self,
        func: Callable,
        args: list[webcface.func_info.Arg] = [],
        return_type: Optional[int | type] = None,
    ) -> None:
        if self.data.is_self(self._member):
            self.data.func_store.set_send(
                self._field, webcface.func_info.FuncInfo(func, args, return_type)
            )
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
    def args(self) -> list[webcface.func_info.Arg]:
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

    def __init__(
        self, base: Optional[webcface.field.Field], callback: Callable
    ) -> None:
        if base is not None:
            self.base = Func(base, self.field_name_tmp())
        else:
            pass
