from __future__ import annotations
from typing import Optional
import blinker
import webcface.field
import webcface.member


class Text(webcface.field.Field):
    def __init__(self, base: webcface.field.Field, field: str = "") -> None:
        """Textを指すクラス

        このコンストラクタを直接使わず、
        Member.text(), Member.texts(), Member.onTextEntry などを使うこと

        詳細は `Textのドキュメント <https://na-trium-144.github.io/webcface/md_11__text.html>`_ を参照
        """
        super().__init__(
            base._data, base._member, field if field != "" else base._field
        )

    @property
    def member(self) -> webcface.member.Member:
        """Memberを返す"""
        return webcface.member.Member(self)

    @property
    def name(self) -> str:
        """field名を返す"""
        return self._field

    @property
    def signal(self) -> blinker.NamedSignal:
        """値が変化したときのイベント

        コールバックの引数にはTextオブジェクトが渡される。

        まだ値をリクエストされてなければ自動でリクエストされる
        """
        self.request()
        return self._data_check().signal("text_change", self._member, self._field)

    def child(self, field: str) -> Text:
        """子フィールドを返す

        :return: 「(thisのフィールド名).(子フィールド名)」をフィールド名とするText
        """
        return Text(self, self._field + "." + field)

    def request(self) -> None:
        """値の受信をリクエストする"""
        req = self._data_check().text_store.add_req(self._member, self._field)
        if req > 0:
            self._data_check().queue_msg(
                [webcface.message.TextReq.new(self._member, self._field, req)]
            )

    def try_get(self) -> Optional[str]:
        """文字列をstrまたはNoneで返す、まだリクエストされてなければ自動でリクエストされる"""
        self.request()
        return self._data_check().text_store.get_recv(self._member, self._field)

    def get(self) -> str:
        """文字列をstrで返す、まだリクエストされてなければ自動でリクエストされる"""
        v = self.try_get()
        return v if v is not None else ""

    def __str__(self) -> str:
        """printしたときなど

        <member("...").text("...") = ...> のように表示する
        """
        return f'<member("{self.member.name}").text("{self.name}") = {self.try_get()}>'

    def set(self, data: str) -> Text:
        """値をセットする"""
        if isinstance(data, str):
            self._set_check().text_store.set_send(self._field, data)
            self.signal.send(self)
        return self
