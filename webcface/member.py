from typing import Callable, Optional, Iterable
import datetime
import webcface.field
import webcface.value
import webcface.text
import webcface.view
import webcface.func
import webcface.func_listener
import webcface.log
import webcface.image
import webcface.message
import webcface.canvas2d
import webcface.canvas3d


class Member(webcface.field.Field):
    def __init__(self, base: "webcface.field.Field", member: str = "") -> None:
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

    def values(self) -> "Iterable[webcface.value.Value]":
        """このメンバーのValueをすべて取得する。

        .. deprecated:: 1.1
        """
        return self.value_entries()

    def texts(self) -> "Iterable[webcface.text.Text]":
        """このメンバーのTextをすべて取得する。

        .. deprecated:: 1.1
        """
        return self.text_entries()

    def views(self) -> "Iterable[webcface.view.View]":
        """このメンバーのViewをすべて取得する。

        .. deprecated:: 1.1
        """
        return self.view_entries()

    def funcs(self) -> "Iterable[webcface.func.Func]":
        """このメンバーのFuncをすべて取得する。

        .. deprecated:: 1.1
        """
        return self.func_entries()

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

    def on_image_entry(self, func: Callable) -> Callable:
        """Textが追加されたときのイベント

        コールバックの引数にはTextオブジェクトが渡される。
        """
        self._data_check().on_image_entry[self._member] = func
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
