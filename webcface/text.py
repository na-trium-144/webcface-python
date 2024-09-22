from __future__ import annotations
from typing import Optional, Callable, SupportsFloat, Union
import webcface.field
import webcface.member


class Variant(webcface.field.Field):
    def __init__(self, base: webcface.field.Field, field: str = "") -> None:
        """文字列、数値などの型を送受信するVariantを指すクラス
        (ver2.0〜)
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

    def on_change(self, func: Callable) -> Callable:
        """値が変化したときのイベント
        (ver2.0〜)

        コールバックの引数にはVariantオブジェクトが渡される。

        まだ値をリクエストされてなければ自動でリクエストされる
        """
        self.request()
        data = self._data_check()
        if self._member not in data.on_text_change:
            data.on_text_change[self._member] = {}
        data.on_text_change[self._member][self._field] = func
        return func

    def child(self, field: str) -> Variant:
        """子フィールドを返す

        :return: 「(thisのフィールド名).(子フィールド名)」をフィールド名とするText
        """
        return Variant(self, self._field + "." + field)

    def request(self) -> None:
        """値の受信をリクエストする"""
        req = self._data_check().text_store.add_req(self._member, self._field)
        if req > 0:
            self._data_check().queue_msg_req(
                [webcface.message.TextReq.new(self._member, self._field, req)]
            )

    def try_get(self) -> Optional[Union[float, bool, str]]:
        """データまたはNoneを返す、まだリクエストされてなければ自動でリクエストされる"""
        self.request()
        return self._data_check().text_store.get_recv(self._member, self._field)

    def get(self) -> Union[float, bool, str]:
        """データを返す、まだリクエストされてなければ自動でリクエストされる"""
        v = self.try_get()
        return v if v is not None else ""

    def exists(self) -> bool:
        """このフィールドにデータが存在すればtrue
        (ver2.0〜)

        try_get() などとは違って、実際のデータを受信しない。
        リクエストもしない。
        """
        return self._field in self._data_check().text_store.get_entry(self._member)

    def __str__(self) -> str:
        """printしたときなど

        <member("...").variant("...") = ...> のように表示する
        """
        return (
            f'<member("{self.member.name}").variant("{self.name}") = {self.try_get()}>'
        )

    def set(self, data: Union[SupportsFloat, bool, str]) -> Variant:
        """値をセットする"""
        if isinstance(data, bool):
            data2: Union[float, bool, str] = data
        elif isinstance(data, SupportsFloat):
            data2 = float(data)
        else:
            data2 = str(data)
        self._set_check().text_store.set_send(self._field, data2)
        on_change = (
            self._data_check().on_text_change.get(self._member, {}).get(self._field)
        )
        if on_change is not None:
            on_change(self)
        return self


class Text(Variant):
    def __init__(self, base: webcface.field.Field, field: str = "") -> None:
        """Textを指すクラス

        このコンストラクタを直接使わず、
        Member.text(), Member.texts(), Member.onTextEntry などを使うこと

        詳細は `Textのドキュメント <https://na-trium-144.github.io/webcface/md_11__text.html>`_ を参照
        """
        super().__init__(base, field)

    def on_change(self, func: Callable) -> Callable:
        """値が変化したときのイベント
        (ver2.0〜)

        コールバックの引数にはTextオブジェクトが渡される。

        まだ値をリクエストされてなければ自動でリクエストされる
        """
        super().on_change(lambda var: func(Text(var)))
        return func

    def child(self, field: str) -> Text:
        """子フィールドを返す

        :return: 「(thisのフィールド名).(子フィールド名)」をフィールド名とするText
        """
        return Text(super().child(field))

    def try_get(self) -> Optional[str]:
        """文字列をstrまたはNoneで返す、まだリクエストされてなければ自動でリクエストされる"""
        v = super().try_get()
        return str(v) if v is not None else None

    def get(self) -> str:
        """文字列をstrで返す、まだリクエストされてなければ自動でリクエストされる"""
        return str(super().get())

    def __str__(self) -> str:
        """printしたときなど

        <member("...").text("...") = ...> のように表示する
        """
        return f'<member("{self.member.name}").text("{self.name}") = {self.try_get()}>'


class InputRef:
    _state: Optional[Variant]

    def __init__(self) -> None:
        self._state = None

    def get(self) -> Union[float, bool, str]:
        """値を返す"""
        if self._state is None:
            return ""
        return self._state.get()
