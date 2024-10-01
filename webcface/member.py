from __future__ import annotations
from typing import Callable, Optional, Iterable, SupportsFloat
import datetime
import webcface.field
import webcface.value
import webcface.text
import webcface.view
import webcface.func
import webcface.log
import webcface.message
import webcface.canvas2d
import webcface.canvas3d


class Member(webcface.field.Field):
    def __init__(self, base: webcface.field.Field, member: str = "") -> None:
        """Memberを指すクラス

        このコンストラクタを直接使わず、
        Client.member(), Client.members(), Client.onMemberEntry などを使うこと

        詳細は `Memberのドキュメント <https://na-trium-144.github.io/webcface/md_02__member.html>`_ を参照
        """
        super().__init__(base._data, member if member != "" else base._member)

    @property
    def name(self) -> str:
        """Member名"""
        return self._member

    def value(self, field: str) -> webcface.value.Value:
        """Valueオブジェクトを生成"""
        return webcface.value.Value(self, field)

    def text(self, field: str) -> webcface.text.Text:
        """Textオブジェクトを生成"""
        return webcface.text.Text(self, field)

    def variant(self, field: str) -> webcface.text.Variant:
        """Variantオブジェクトを生成 (ver2.0〜)"""
        return webcface.text.Variant(self, field)

    def view(self, field: str) -> webcface.view.View:
        """Viewオブジェクトを生成"""
        return webcface.view.View(self, field)

    def canvas2d(
        self,
        field: str,
        width: Optional[SupportsFloat] = None,
        height: Optional[SupportsFloat] = None,
    ) -> webcface.canvas2d.Canvas2D:
        """Canvas2Dオブジェクトを生成

        :arg width, height: Canvas2Dのサイズを指定して初期化する
        """
        return webcface.canvas2d.Canvas2D(self, field, width, height)

    def canvas3d(self, field: str) -> webcface.canvas3d.Canvas3D:
        """Canvas3Dオブジェクトを生成"""
        return webcface.canvas3d.Canvas3D(self, field)

    def log(self, field: str = "default") -> webcface.log.Log:
        """Logオブジェクトを生成

        :arg field: (ver2.1〜) Logの名前を指定可能(省略すると"default")
        """
        return webcface.log.Log(self, field)

    def func(self, arg: str = "", **kwargs) -> webcface.func.Func:
        """Funcオブジェクトを生成

        #. member.func(arg: str)
            * 指定した名前のFuncオブジェクトを生成・参照する。
        #. @member.func(arg: str, [**kwargs])
            * デコレータとして使い、デコレートした関数を指定した名前でセットする。
            * デコレート後、関数は元のまま返す。
        #. @member.func([**kwargs])
            * 3と同じだが、名前はデコレートした関数から自動で取得される。
        #. member.func(arg: Callable, [**kwargs])
            * これはver2.0で削除。

        2, 3 の場合のkwargsは Func.set() を参照。
        """
        return webcface.func.Func(self, arg, **kwargs)

    def values(self) -> Iterable[webcface.value.Value]:
        """このメンバーのValueをすべて取得する。

        .. deprecated:: 1.1
        """
        return self.value_entries()

    def value_entries(self) -> Iterable[webcface.value.Value]:
        """このメンバーのValueをすべて取得する。"""
        return map(self.value, self._data_check().value_store.get_entry(self._member))

    def texts(self) -> Iterable[webcface.text.Text]:
        """このメンバーのTextをすべて取得する。

        .. deprecated:: 1.1
        """
        return self.text_entries()

    def text_entries(self) -> Iterable[webcface.text.Text]:
        """このメンバーのTextをすべて取得する。"""
        return map(self.text, self._data_check().text_store.get_entry(self._member))

    def views(self) -> Iterable[webcface.view.View]:
        """このメンバーのViewをすべて取得する。

        .. deprecated:: 1.1
        """
        return self.view_entries()

    def view_entries(self) -> Iterable[webcface.view.View]:
        """このメンバーのViewをすべて取得する。"""
        return map(self.view, self._data_check().view_store.get_entry(self._member))

    def funcs(self) -> Iterable[webcface.func.Func]:
        """このメンバーのFuncをすべて取得する。

        .. deprecated:: 1.1
        """
        return self.func_entries()

    def func_entries(self) -> Iterable[webcface.func.Func]:
        """このメンバーのFuncをすべて取得する。"""
        return map(self.func, self._data_check().func_store.get_entry(self._member))

    def canvas2d_entries(self) -> Iterable[webcface.canvas2d.Canvas2D]:
        """このメンバーのCanvas2Dをすべて取得する。"""
        return map(
            self.canvas2d, self._data_check().canvas2d_store.get_entry(self._member)
        )

    def canvas3d_entries(self) -> Iterable[webcface.canvas3d.Canvas3D]:
        """このメンバーのCanvas3Dをすべて取得する。"""
        return map(
            self.canvas3d, self._data_check().canvas3d_store.get_entry(self._member)
        )

    def log_entries(self) -> Iterable[webcface.log.Log]:
        """このメンバーのLogをすべて取得する。(ver2.1〜)"""
        return map(self.log, self._data_check().log_store.get_entry(self._member))

    def on_value_entry(self, func: Callable) -> Callable:
        """Valueが追加されたときのイベント

        コールバックの引数にはValueオブジェクトが渡される。
        """
        self._data_check().on_value_entry[self._member] = func
        return func

    def on_text_entry(self, func: Callable) -> Callable:
        """Textが追加されたときのイベント

        コールバックの引数にはTextオブジェクトが渡される。
        """
        self._data_check().on_text_entry[self._member] = func
        return func

    def on_view_entry(self, func: Callable) -> Callable:
        """Viewが追加されたときのイベント

        コールバックの引数にはViewオブジェクトが渡される。
        """
        self._data_check().on_view_entry[self._member] = func
        return func

    def on_func_entry(self, func: Callable) -> Callable:
        """Funcが追加されたときのイベント

        コールバックの引数にはFuncオブジェクトが渡される。
        """
        self._data_check().on_func_entry[self._member] = func
        return func

    def on_canvas2d_entry(self, func: Callable) -> Callable:
        """Canvas2Dが追加されたときのイベント

        コールバックの引数にはCanvas2Dオブジェクトが渡される。
        """
        self._data_check().on_canvas2d_entry[self._member] = func
        return func

    def on_canvas3d_entry(self, func: Callable) -> Callable:
        """Canvas3Dが追加されたときのイベント

        コールバックの引数にはCanvas3Dオブジェクトが渡される。
        """
        self._data_check().on_canvas3d_entry[self._member] = func
        return func

    def on_log_entry(self, func: Callable) -> Callable:
        """Logが追加されたときのイベント(ver2.1〜)

        コールバックの引数にはLogオブジェクトが渡される。
        """
        self._data_check().on_log_entry[self._member] = func
        return func

    def on_sync(self, func: Callable) -> Callable:
        """Memberがsyncしたときのイベント

        コールバックの引数にはMemberオブジェクトが渡される。
        """
        self._data_check().on_sync[self._member] = func
        return func

    @property
    def sync_time(self) -> datetime.datetime:
        """memberが最後にsyncした時刻を返す"""
        t = self._data_check().sync_time_store.get_recv(self._member)
        if t is not None:
            return t
        else:
            return datetime.datetime.fromtimestamp(0)

    @property
    def lib_name(self) -> str:
        """このMemberが使っているWebCFaceライブラリの識別情報

        c++クライアントライブラリは"cpp", javascriptクライアントは"js",
        pythonクライアントは"python"を返す。
        """
        return self._data_check().member_lib_name.get(
            self._data_check().get_member_id_from_name(self._member), ""
        )

    @property
    def lib_version(self) -> str:
        """このMemberが使っているWebCFaceのバージョン"""
        return self._data_check().member_lib_ver.get(
            self._data_check().get_member_id_from_name(self._member), ""
        )

    @property
    def remote_addr(self) -> str:
        """このMemberのIPアドレス"""
        return self._data_check().member_remote_addr.get(
            self._data_check().get_member_id_from_name(self._member), ""
        )

    @property
    def ping_status(self) -> Optional[int]:
        """通信速度を調べる

        通信速度データをリクエストしていなければリクエストし、
        sync()後通信速度が得られるようになる
        :return: データがなければ None, 受信していれば pingの往復時間 (ms)
        """
        self.request_ping_status()
        return self._data_check().ping_status.get(
            self._data_check().get_member_id_from_name(self._member), None
        )

    def request_ping_status(self) -> None:
        """通信速度データをリクエストする
        (ver2.0〜)
        """
        if not self._data_check().ping_status_req:
            self._data_check().ping_status_req = True
            self._data_check().queue_msg_req([webcface.message.PingStatusReq.new()])

    def on_ping(self, func: Callable) -> Callable:
        """通信速度データが更新されたときのイベント

        通信速度データをリクエストしていなければリクエストする

        コールバックの引数にはMemberオブジェクトが渡される。
        """
        self.request_ping_status()
        self._data_check().on_ping[self._member] = func
        return func
