from __future__ import annotations
from typing import Callable, Optional
from copy import deepcopy
import threading
import sys
import webcface.member
import webcface.field
import webcface.func_info


class Func(webcface.field.Field):
    _args: Optional[list[webcface.func_info.Arg]]
    _return_type: Optional[int | type]

    def __init__(
        self,
        base: Optional[webcface.field.Field],
        field: str = "",
        args: Optional[list[webcface.func_info.Arg]] = None,
        return_type: Optional[int | type] = None,
    ) -> None:
        if base is None:
            self.data = None
            self._member = ""
            self._field = ""
        else:
            super().__init__(
                base.data, base._member, field if field != "" else base._field
            )
        self._args = args
        self._return_type = return_type

    @property
    def member(self) -> webcface.member.Member:
        return webcface.member.Member(self)

    @property
    def name(self) -> str:
        return self._field

    def _set_info(self, info: webcface.func_info.FuncInfo) -> None:
        if self.data.is_self(self._member):
            self.data.func_store.set_send(self._field, info)
        else:
            raise ValueError("Cannot set data to member other than self")

    def _get_info(self) -> webcface.func_info.FuncInfo:
        func_info = self.data.func_store.get_recv(self._member, self._field)
        if func_info is None:
            raise ValueError("Func not set")
        return func_info

    def set(
        self,
        func: Callable,
        args: Optional[list[webcface.func_info.Arg]] = None,
        return_type: Optional[int | type] = None,
    ) -> Func:
        if args is not None:
            self._args = args
        if return_type is not None:
            self._return_type = return_type
        self._set_check()
        self._set_info(webcface.func_info.FuncInfo(func, self._args, self._return_type))
        return self

    @property
    def hidden(self) -> bool:
        return self._get_info().hidden

    @hidden.setter
    def hidden(self, h: bool) -> None:
        self._set_check()
        self._get_info().hidden = h

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
            return self.run_async(*args).result

    def run_async(self, *args) -> webcface.func_info.AsyncFuncResult:
        r = self.data.func_result_store.add_result("", self)
        if self.data.is_self(self._member):

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
        else:
            self.data.queue_msg(
                [
                    webcface.message.Call.new(
                        r._caller_id,
                        0,
                        self.data.get_member_id_from_name(self._member),
                        self._field,
                        list(args),
                    )
                ]
            )
        return r

    def __call__(self, *args) -> float | bool | str | Callable:
        if len(args) == 1 and callable(args[0]):
            if isinstance(self, AnonymousFunc):
                target = Func(self, args[0].__name__, self._args, self._return_type)
            else:
                target = self
            target.set(args[0])
            return args[0]
        else:
            return self.run(*args)

    @property
    def return_type(self) -> int:
        return self._get_info().return_type

    @property
    def args(self) -> list[webcface.func_info.Arg]:
        return deepcopy(self._get_info().args)


class AnonymousFunc(Func):
    field_id = 0

    @staticmethod
    def field_name_tmp() -> str:
        AnonymousFunc.field_id += 1
        return f".tmp{AnonymousFunc.field_id}"

    _base_init: bool
    _func: Optional[Callable]

    def __init__(
        self,
        base: Optional[webcface.field.Field],
        callback: Optional[Callable],
        **kwargs,
    ) -> None:
        if base is not None:
            super().__init__(base, AnonymousFunc.field_name_tmp(), **kwargs)
            if callback is not None:
                self.set(callback)
                self.hidden = True
            self._base_init = True
        else:
            super().__init__(None, "", **kwargs)
            self._base_init = False
            self._func = callback

    def lock_to(self, target: Func) -> None:
        if not self._base_init:
            if self._func is None:
                raise ValueError("func not set")
            self.data = target.data
            self._member = target._member
            self._field = AnonymousFunc.field_name_tmp()
            self.set(self._func)
            self.hidden = True
        target._set_info(self._get_info())
        self.free()
