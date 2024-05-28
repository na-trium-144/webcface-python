from __future__ import annotations
from typing import Optional, List
import blinker
import webcface.field
import webcface.member
import webcface.message
import webcface.cffi
import ctypes

class Value(webcface.field.Field):
    def __init__(self, base: webcface.field.Field, field: str = "") -> None:
        """Valueを指すクラス

        このコンストラクタを直接使わず、
        Member.value(), Member.values(), Member.onValueEntry などを使うこと

        詳細は `Valueのドキュメント <https://na-trium-144.github.io/webcface/md_10__value.html>`_ を参照
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

        コールバックの引数にはValueオブジェクトが渡される。

        まだ値をリクエストされてなければ自動でリクエストされる
        """
        raise NotImplementedError()
        # self.request()
        # return self._data_check().signal("value_change", self._member, self._field)

    def child(self, field: str) -> Value:
        """「(thisのフィールド名).(子フィールド名)」をフィールド名とするValue"""
        return Value(self, self._field + "." + field)

    def request(self) -> None:
        """値の受信をリクエストする"""
        self.try_get()

    def try_get_vec(self) -> Optional[List[float]]:
        """値をlistまたはNoneで返す、まだリクエストされてなければ自動でリクエストされる"""
        buf = (ctypes.c_double * 1)()
        recv_size = ctypes.POINTER(ctypes.c_int)()
        ret = webcface.cffi.wcfValueGetVecDW(
            self._data_check().wcli, self._member, self._field, buf, 1, recv_size
        )
        if ret == webcface.cffi.WCF_NOT_FOUND:
            return None
        if ret != webcface.cffi.WCF_OK:
            raise RuntimeError("wcfValueGetVecDW failed: " + ret)
        if recv_size.contents > 1:
            buf = (ctypes.c_double * recv_size.contents)()
            webcface.cffi.wcfValueGetVecDW(
                self._data_check().wcli,
                self._member,
                self._field,
                buf,
                recv_size.contents,
                recv_size,
            )
        return [v for v in buf]

    def try_get(self) -> Optional[float]:
        """値をfloatまたはNoneで返す、まだリクエストされてなければ自動でリクエストされる"""
        v = self.try_get_vec()
        return v[0] if v is not None else None

    def get_vec(self) -> List[float]:
        """値をlistで返す、まだリクエストされてなければ自動でリクエストされる"""
        v = self.try_get_vec()
        return v if v is not None else []

    def get(self) -> float:
        """値をfloatで返す、まだリクエストされてなければ自動でリクエストされる"""
        v = self.try_get()
        return v if v is not None else 0

    def __str__(self) -> str:
        """printしたときなど

        <member("...").value("...") = ...> のように表示する
        """
        return f'<member("{self.member.name}").value("{self.name}") = {self.try_get_vec()}>'

    def set(self, data: List[float] | int | float) -> Value:
        """値をセットする"""
        self._set_check()
        if not isinstance(data, list):
            data = [data]
        buf = (ctypes.c_double * len(data))(*data)
        ret = webcface.cffi.wcfValueSetVecDW(self._data_check().wcli, self._field, buf, len(data))
        if ret != webcface.cffi.WCF_OK:
            raise RuntimeError("wcfValueSetVecDW failed: " + ret)
        return self
