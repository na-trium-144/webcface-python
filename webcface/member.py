from __future__ import annotations
from typing import Callable, Optional, Iterable
import blinker
import webcface.field
import webcface.value
import webcface.text
import webcface.view
import webcface.func


class Member(webcface.field.Field):
    def __init__(self, base: webcface.field.Field, member: str = "") -> None:
        """Memberを指すクラス

        このコンストラクタを直接使わず、
        Client.member(), Client.members(), Client.onMemberEntry などを使うこと

        詳細は `Memberのドキュメント <https://na-trium-144.github.io/webcface/md_02__member.html>`_ を参照
        """
        super().__init__(base.data, member if member != "" else base._member)

    @property
    def name(self) -> str:
        """Member名"""
        return self._member

    def value(self, field: str) -> webcface.value.Value:
        """Valueを参照する"""
        return webcface.value.Value(self, field)

    def text(self, field: str) -> webcface.text.Text:
        """Textを参照する"""
        return webcface.text.Text(self, field)

    def view(self, field: str) -> webcface.view.View:
        """Viewを参照する"""
        return webcface.view.View(self, field)

    def func(
        self, arg: Optional[str | Callable] = None, **kwargs
    ) -> webcface.func.Func | webcface.func.AnonymousFunc:
        """FuncオブジェクトまたはAnonymousオブジェクトを生成

        #. member.func(arg: str)
            * 指定した名前のFuncオブジェクトを生成・参照する。
        #. member.func(arg: Callable, [**kwargs])
            * Funcの名前を決めずに一時的なFuncオブジェクト(AnonymoudFuncオブジェクト)を作成し、関数をセットする。
        #. @member.func(arg: str, [**kwargs])
            * デコレータとして使い、デコレートした関数を指定した名前でセットする。
            * デコレート後、関数は元のまま返す。
        #. @member.func([**kwargs])
            * 3と同じだが、名前はデコレートした関数から自動で取得される。

        2,3,4について、関数のセットに関しては Func.set() を参照。

        :return: 1→ Func, 2→ AnonymousFunc
        """
        if isinstance(arg, str):
            return webcface.func.Func(self, arg, **kwargs)
        else:
            return webcface.func.AnonymousFunc(self, arg, **kwargs)

    # def log()

    def values(self) -> Iterable[webcface.value.Value]:
        """このメンバーのValueをすべて取得する。"""
        return map(self.value, self.data.value_store.get_entry(self._member))

    def texts(self) -> Iterable[webcface.text.Text]:
        """このメンバーのTextをすべて取得する。"""
        return map(self.text, self.data.text_store.get_entry(self._member))

    def views(self) -> Iterable[webcface.view.View]:
        """このメンバーのViewをすべて取得する。"""
        return map(self.view, self.data.view_store.get_entry(self._member))

    def funcs(self) -> Iterable[webcface.func.Func]:
        """このメンバーのFuncをすべて取得する。"""
        return map(self.func, self.data.func_store.get_entry(self._member))

    @property
    def on_value_entry(self) -> blinker.NamedSignal:
        """Valueが追加されたときのイベント

        コールバックの引数にはValueオブジェクトが渡される。
        """
        return self.data.signal("value_entry", self._member)

    @property
    def on_text_entry(self) -> blinker.NamedSignal:
        """Textが追加されたときのイベント

        コールバックの引数にはTextオブジェクトが渡される。
        """
        return self.data.signal("text_entry", self._member)

    @property
    def on_view_entry(self) -> blinker.NamedSignal:
        """Viewが追加されたときのイベント

        コールバックの引数にはViewオブジェクトが渡される。
        """
        return self.data.signal("view_entry", self._member)

    @property
    def on_func_entry(self) -> blinker.NamedSignal:
        """Funcが追加されたときのイベント

        コールバックの引数にはFuncオブジェクトが渡される。
        """
        return self.data.signal("func_entry", self._member)

    @property
    def on_sync(self) -> blinker.NamedSignal:
        """Memberがsyncしたときのイベント

        コールバックの引数にはMemberオブジェクトが渡される。
        """
        return self.data.signal("sync", self._member)

    @property
    def lib_name(self) -> str:
        """このMemberが使っているWebCFaceライブラリの識別情報

        c++クライアントライブラリは"cpp", javascriptクライアントは"js",
        pythonクライアントは"python"を返す。
        """
        return self.data.member_lib_name.get(
            self.data.get_member_id_from_name(self._member), ""
        )

    @property
    def lib_version(self) -> str:
        """このMemberが使っているWebCFaceのバージョン"""
        return self.data.member_lib_ver.get(
            self.data.get_member_id_from_name(self._member), ""
        )

    @property
    def remote_addr(self) -> str:
        """このMemberのIPアドレス"""
        return self.data.member_remote_addr.get(
            self.data.get_member_id_from_name(self._member), ""
        )

    @property
    def ping_status(self) -> Optional[int]:
        """通信速度を調べる

        初回の呼び出しで通信速度データをリクエストし、
        sync()後通信速度が得られるようになる
        :return: 初回→ None, 2回目以降(取得できれば)→ pingの往復時間 (ms)
        """
        if not self.data.ping_status_req:
            self.data.ping_status_req_send = True
            self.data.ping_status_req = True
        return self.data.ping_status.get(
            self.data.get_member_id_from_name(self._member), None
        )

    @property
    def on_ping(self) -> blinker.NamedSignal:
        """通信速度データが更新されたときのイベント

        コールバックの引数にはMemberオブジェクトが渡される。
        """
        self.ping_status
        return self.data.signal("ping")
