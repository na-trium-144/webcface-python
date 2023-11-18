from __future__ import annotations
from typing import Optional
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
        super().__init__(base.data, base._member)

    @property
    def member(self) -> webcface.member.Member:
        """Memberを返す"""
        return webcface.member.Member(self)

    @property
    def signal(self) -> blinker.NamedSignal:
        """logが追加されたときのイベント

        コールバックの引数にはLogオブジェクトが渡される。
        """
        return self.data.signal("log_append", self._member)

    def try_get(self) -> Optional[list[webcface.log_handler.LogLine]]:
        """ログをlistまたはNoneで返す"""
        return self.data.log_store.get_recv(self._member)

    def get(self) -> list[webcface.log_handler.LogLine]:
        """ログをlistで返す"""
        v = self.try_get()
        return v if v is not None else []

    def clear(self) -> Log:
        """受信したログを空にする

        リクエスト状態はクリアしない"""
        self.data.log_store.set_recv(self._member, [])
        return self
