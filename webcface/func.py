from typing import Callable, Optional, List, Union
from copy import deepcopy
import webcface.member
import webcface.field
import webcface.func_info


class Func(webcface.field.Field):
    _return_type: Optional[Union[int, type]]
    _args: "Optional[List[webcface.func_info.Arg]]"
    _handle: bool

    def __init__(
        self,
        base: "Optional[webcface.field.Field]",
        field: str = "",
        return_type: Optional[Union[int, type]] = None,
        args: "Optional[List[webcface.func_info.Arg]]" = None,
        handle: bool = False,
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
        self._handle = handle

    @property
    def member(self) -> "webcface.member.Member":
        """Memberを返す"""
        return webcface.member.Member(self)

    @property
    def name(self) -> str:
        """field名を返す"""
        return self._field

    def _set_info(self, info: "webcface.func_info.FuncInfo") -> None:
        self._set_check().func_store.set_send(self._field, info)

    def _get_info(self) -> "webcface.func_info.FuncInfo":
        func_info = self._data_check().func_store.get_recv(self._member, self._field)
        if func_info is None:
            raise ValueError("Func not set")
        return func_info

    def exists(self) -> bool:
        """このFuncの情報が存在すればtrue
        (ver2.0〜)

        """
        return self._field in self._data_check().func_store.get_entry(self._member)

    def set(
        self,
        func: Callable,
        return_type: Optional[Union[int, type]] = None,
        args: "Optional[List[webcface.func_info.Arg]]" = None,
        handle: bool = False,
    ) -> "Func":
        """関数からFuncInfoを構築しセットする

        * 関数にアノテーションがついている場合はreturn_typeとargs内のtypeは不要
        * (ver2.0〜) set()でセットした関数は Client.sync() のスレッドでそのまま呼び出され、
        この関数が完了するまで他のデータの受信はブロックされる。

        :arg func: 登録したい関数
        :arg return_type: 関数の戻り値 (ValTypeのEnumまたはtypeクラス)
        :arg args: 関数の引数の情報
        :arg handle: (ver2.2〜) これをTrueにするか引数型のアノテーションでCallHandle型が指定されている場合、
        引数に CallHandle が渡されるようになる
        """
        if return_type is not None:
            self._return_type = return_type
        if args is not None:
            self._args = args
        self._set_info(
            webcface.func_info.FuncInfo(
                func, self._return_type, self._args, handle=handle or self._handle
            )
        )
        return self

    def set_async(
        self,
        func: Callable,
        return_type: Optional[Union[int, type]] = None,
        args: "Optional[List[webcface.func_info.Arg]]" = None,
        handle: bool = False,
    ) -> "Func":
        """関数からFuncInfoを構築しセットする
        (ver2.0〜)

        * setAsync()でセットした場合、他クライアントから呼び出されたとき新しいスレッドを建てて実行される。

        :arg func: 登録したい関数
        :arg return_type: 関数の戻り値 (ValTypeのEnumまたはtypeクラス)
        :arg args: 関数の引数の情報
        :arg handle: (ver2.2〜) これをTrueにするか引数型のアノテーションでCallHandle型が指定されている場合、
        引数に CallHandle が渡されるようになる
        """
        if return_type is not None:
            self._return_type = return_type
        if args is not None:
            self._args = args
        self._set_info(
            webcface.func_info.FuncInfo(
                func,
                self._return_type,
                self._args,
                in_thread=True,
                handle=handle or self._handle,
            )
        )
        return self

    def free(self) -> "Func":
        """関数の設定を削除"""
        self._data_check().func_store.unset_recv(self._member, self._field)
        return self

    def run(self, *args) -> Union[float, bool, str]:
        """関数を実行する (同期)

        * selfの関数の場合、このスレッドで直接実行する
        例外が発生した場合そのままraise, 関数が存在しない場合 FuncNotFoundError
        をraiseする
        * リモートの場合、関数呼び出しを送信し結果が返ってくるまで待機
        例外が発生した場合 RuntimeError, 関数が存在しない場合 FuncNotFoundError
        をthrowする
        * (ver2.0〜) Client.sync() を呼ぶのとは別のスレッドで使用することを想定している。
        呼び出しが成功したかどうかの情報の受信は Client.sync() で行われるため、
        この関数を使用して待機している間に Client.sync()
        が呼ばれていないとデッドロックしてしまうので注意。
        """
        ret = self.run_async(*args)
        ret.wait_finish()
        if not ret.found:
            raise webcface.func_info.FuncNotFoundError(self)
        if ret.is_error:
            raise RuntimeError(ret.rejection)
        return ret.response

    def run_async(self, *args) -> "webcface.func_info.Promise":
        """関数を実行する (非同期)

        * 戻り値やエラー、例外はPromiseから取得する
        """
        r = self._data_check().func_result_store.add_result("", self)
        if self._data_check().is_self(self._member):
            with r._data._cv:
                func_info = self._data_check().func_store.get_recv(
                    self._member, self._field
                )
                if func_info is None:
                    r._data._set_reach(False)
                else:
                    r._data._set_reach(True)
                    func_info.run(r._data, args)
        else:
            if not self._data_check().queue_msg_online(
                [
                    webcface.message.Call.new(
                        r._data._caller_id,
                        0,
                        self._data_check().get_member_id_from_name(self._member),
                        self._field,
                        list(args),
                    )
                ]
            ):
                r._data._set_reach(False)
        return r

    def __call__(self, *args) -> Union[float, bool, str, Callable]:
        """引数にCallableを1つだけ渡した場合、set()してそのCallableを返す
        (Funcをデコレータとして使う場合の処理)

        それ以外の場合、run()する
        """
        if len(args) == 1 and callable(args[0]):
            if self._field == "":
                self._field = args[0].__name__
            self.set(args[0])
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
    def args(self) -> "List[webcface.func_info.Arg]":
        """引数の情報を返す"""
        return deepcopy(self._get_info().args)
