from __future__ import annotations
from typing import Optional
import blinker
import webcface.field
import webcface.member


class Value(webcface.field.Field):
    def __init__(self, base: webcface.field.Field, field: str = "") -> None:
        """Valueを指すクラス

        このコンストラクタを直接使わず、
        Member.value(), Member.values(), Member.onValueEntry などを使うこと

        詳細は `Valueのドキュメント <https://na-trium-144.github.io/webcface/md_10__value.html>`_ を参照
        """
        super().__init__(base.data, base._member, field if field != "" else base._field)

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

        コールバックの引数にはValueオブジェクトが渡される。
        """
        return self.data.signal("value_change", self._member, self._field)

    def child(self, field: str) -> Value:
        """子フィールドを返す

        :return: 「(thisのフィールド名).(子フィールド名)」をフィールド名とするValue
        """
        return Value(self, self._field + "." + field)

    def try_get_vec(self) -> Optional[list[float]]:
        """値をlistまたはNoneで返す"""
        return self.data.value_store.get_recv(self._member, self._field)

    def try_get(self) -> Optional[float]:
        """値をfloatまたはNoneで返す"""
        v = self.try_get_vec()
        return v[0] if v is not None else None

    def get_vec(self) -> list[float]:
        """値をlistで返す"""
        v = self.try_get_vec()
        return v if v is not None else []

    def get(self) -> float:
        """値をfloatで返す"""
        v = self.try_get()
        return v if v is not None else 0

    def set(self, data: list[float] | float) -> Value:
        """値をセットする"""
        self._set_check()
        if isinstance(data, int):
            self.data.value_store.set_send(self._field, [data])
            self.signal.send(self)
        elif isinstance(data, list):
            self.data.value_store.set_send(self._field, data)
            self.signal.send(self)
        return self
