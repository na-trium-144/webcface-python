from __future__ import annotations
from typing import Optional, List
import blinker
import webcface.field
import webcface.member
import webcface.log_handler


class Log(webcface.field.Field):
    def __init__(self, base: webcface.field.Field) -> None:
        """Logを指すクラス

        このコンストラクタを直接使わず、
        Member.log() を使うこと

        詳細は `Logのドキュメント <https://na-trium-144.github.io/webcface/md_40__log.html>`_ を参照
        """
        super().__init__(base._data, base._member)

    @property
    def member(self) -> webcface.member.Member:
        """Memberを返す"""
        return webcface.member.Member(self)

    @property
    def signal(self) -> blinker.NamedSignal:
        """logが追加されたときのイベント

        コールバックの引数にはLogオブジェクトが渡される。

        まだリクエストされてなければ自動でリクエストする。
        """
        self.request()
        return self._data_check().signal("log_append", self._member)

    def request(self) -> None:
        """値の受信をリクエストする"""
        req = self._data_check().log_store.add_req(self._member)
        if req:
            self._data_check().queue_msg(
                [webcface.message.LogReq.new(self._member)]
            )

    def try_get(self) -> Optional[List[webcface.log_handler.LogLine]]:
        """ログをlistまたはNoneで返す、まだリクエストされてなければ自動でリクエストされる"""
        self.request()
        return self._data_check().log_store.get_recv(self._member)

    def get(self) -> List[webcface.log_handler.LogLine]:
        """ログをlistで返す、まだリクエストされてなければ自動でリクエストされる"""
        v = self.try_get()
        return v if v is not None else []

    def clear(self) -> Log:
        """受信したログを空にする

        リクエスト状態はクリアしない"""
        self._data_check().log_store.set_recv(self._member, [])
        return self
