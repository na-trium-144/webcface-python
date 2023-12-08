from __future__ import annotations
from typing import Callable, Optional, List
from copy import deepcopy
import threading
import sys
import webcface.member
import webcface.field
import webcface.func_info


class Func(webcface.field.Field):
    _return_type: Optional[int | type]
    _args: Optional[List[webcface.func_info.Arg]]
    _hidden: Optional[bool]

    def __init__(
        self,
        base: Optional[webcface.field.Field],
        field: str = "",
        return_type: Optional[int | type] = None,
        args: Optional[List[webcface.func_info.Arg]] = None,
        hidden: Optional[bool] = None,
    ) -> None:
        """Funcを指すクラス

        このコンストラクタを直接使わず、
        Member.func(), Member.funcs(), Member.onFuncEntry などを使うこと

        詳細は `Funcのドキュメント <https://na-trium-144.github.io/webcface/md_30__func.html>`_ を参照
        """
        if base is None:
            super().__init__(None, "", "")
        else:
            super().__init__(
                base._data, base._member, field if field != "" else base._field
            )
        self._return_type = return_type
        self._args = args
        self._hidden = hidden

    @property
    def member(self) -> webcface.member.Member:
        """Memberを返す"""
        return webcface.member.Member(self)

    @property
    def name(self) -> str:
        """field名を返す"""
        return self._field

    def _set_info(self, info: webcface.func_info.FuncInfo) -> None:
        self._set_check().func_store.set_send(self._field, info)

    def _get_info(self) -> webcface.func_info.FuncInfo:
        func_info = self._data_check().func_store.get_recv(self._member, self._field)
        if func_info is None:
            raise ValueError("Func not set")
        return func_info

    def set(
        self,
        func: Callable,
        return_type: Optional[int | type] = None,
        args: Optional[List[webcface.func_info.Arg]] = None,
        hidden: Optional[bool] = None,
    ) -> Func:
        """関数からFuncInfoを構築しセットする

        関数にアノテーションがついている場合はreturn_typeとargs内のtypeは不要

        :arg func: 登録したい関数
        :arg return_type: 関数の戻り値 (ValTypeのEnumまたはtypeクラス)
        :arg args: 関数の引数の情報
        :arg hidden: Trueにすると関数を他のMemberから隠す
        """
        if return_type is not None:
            self._return_type = return_type
        if args is not None:
            self._args = args
        if hidden is not None:
            self._hidden = hidden
        self._set_info(
            webcface.func_info.FuncInfo(
                func, self._return_type, self._args, self._hidden
            )
        )
        return self

    @property
    def hidden(self) -> bool:
        return self._get_info().hidden

    @hidden.setter
    def hidden(self, h: bool) -> None:
        """関数の登録後にhidden属性を変更する"""
        info = self._get_info()
        info.hidden = h
        self._set_info(info)

    def free(self) -> Func:
        """関数の設定を削除"""
        self._data_check().func_store.unset_recv(self._member, self._field)
        return self

    def run(self, *args) -> float | bool | str:
        """関数を実行する (同期)

        selfの関数の場合、このスレッドで直接実行する
        例外が発生した場合そのままraise, 関数が存在しない場合 FuncNotFoundError
        をraiseする

        リモートの場合、関数呼び出しを送信し結果が返ってくるまで待機
        例外が発生した場合 RuntimeError, 関数が存在しない場合 FuncNotFoundError
        をthrowする
        """
        if self._data_check().is_self(self._member):
            func_info = self._data_check().func_store.get_recv(
                self._member, self._field
            )
            if func_info is None:
                raise webcface.func_info.FuncNotFoundError(self)
            res = func_info.run(args)
            return res
        else:
            return self.run_async(*args).result

    def run_async(self, *args) -> webcface.func_info.AsyncFuncResult:
        """関数を実行する (非同期)

        戻り値やエラー、例外はAsyncFuncResultから取得する
        """
        r = self._data_check().func_result_store.add_result("", self)
        if self._data_check().is_self(self._member):

            def target():
                with r._cv:
                    func_info = self._data_check().func_store.get_recv(
                        self._member, self._field
                    )
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
            self._data_check().queue_msg(
                [
                    webcface.message.Call.new(
                        r._caller_id,
                        0,
                        self._data.get_member_id_from_name(self._member),
                        self._field,
                        list(args),
                    )
                ]
            )
        return r

    def __call__(self, *args) -> float | bool | str | Callable:
        """引数にCallableを1つだけ渡した場合、set()してそのCallableを返す
        (Funcをデコレータとして使う場合の処理)

        それ以外の場合、run()する
        """
        if len(args) == 1 and callable(args[0]):
            if isinstance(self, AnonymousFunc):
                target = Func(self, args[0].__name__, self._return_type, self._args)
            else:
                target = self
            target.set(args[0])
            return args[0]
        else:
            return self.run(*args)

    @property
    def return_type(self) -> int:
        """戻り値の型を返す

        ValTypeのEnumを使う
        """
        return self._get_info().return_type

    @property
    def args(self) -> List[webcface.func_info.Arg]:
        """引数の情報を返す"""
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
        """名前を指定せず先に関数を登録するFuncクラス

        詳細は `Funcのドキュメント <https://na-trium-144.github.io/webcface/md_30__func.html>`_ を参照
        """
        if base is not None:
            super().__init__(base, AnonymousFunc.field_name_tmp(), **kwargs)
            if callback is not None:
                self.set(callback, hidden=True)
            self._base_init = True
        else:
            super().__init__(None, "", **kwargs)
            self._base_init = False
            self._func = callback

    def lock_to(self, target: Func) -> None:
        """target に関数を移動"""
        if not self._base_init:
            if self._func is None:
                raise ValueError("func not set")
            self._data = target._data
            self._member = target._member
            self._field = AnonymousFunc.field_name_tmp()
            self.set(self._func, hidden=True)
        target._set_info(self._get_info())
        target.hidden = False
        self.free()
