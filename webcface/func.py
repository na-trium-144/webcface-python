from __future__ import annotations
from typing import Callable, Optional
from copy import deepcopy
import threading
import sys
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
    ) -> Func:
        if self.data.is_self(self._member):
            self.data.func_store.set_send(
                self._field, webcface.func_info.FuncInfo(func, args, return_type)
            )
            return self
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

    def free(self) -> Func:
        self.data.func_store.unset_recv(self._member, self._field)
        return self

    def run(self, *args) -> float | bool | str:
        if self.data.is_self(self._member):
            func_info = self.data.func_store.get_recv(self._member, self._field)
            if func_info is None:
                raise webcface.func_info.FuncNotFoundError(self)
            res = func_info.run(args)
            return res
        else:
            return ""

    def run_async(self, *args) -> webcface.func_info.AsyncFuncResult:
        if self.data.is_self(self._member):
            r = self.data.func_result_store.add_result("", self)
            def target():
                with r._cv:
                    func_info = self.data.func_store.get_recv(self._member, self._field)
                    if func_info is None:
                        r._started = False
                        r._started_ready = True
                        r._result_is_error = True
                        r._result_ready = True
                    else:
                        r._started = True
                        r._started_ready = True
                        try:
                            res = func_info.run(args)
                            r._result = res
                            r._result_ready = True
                        except Exception as e:
                            r._result = str(e)
                            r._result_is_error = True
                            r._result_ready = True
                    r._cv.notify_all()
            threading.Thread(target=target).start()
            return r
        else:
            return ""

    def __call__(self, *args) -> float | bool | str:
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
