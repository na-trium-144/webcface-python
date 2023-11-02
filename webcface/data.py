from __future__ import annotations
from typing import Optional
import json
from blinker import signal
import webcface.field
import webcface.member


class Value(webcface.field.Field):
    def __init__(self, base: webcface.field.Field, field: str = "") -> None:
        super().__init__(base.data, base._member, field if field != "" else base._field)

    @property
    def member(self) -> webcface.member.Member:
        return webcface.member.Member(self)

    @property
    def name(self) -> str:
        return self._field

    @property
    def signal(self) -> signal:
        return signal(json.dumps(["valueChange", self._member, self._field]))

    def child(self, field: str) -> Value:
        return Value(self, self._field + "." + field)

    def try_get_vec(self) -> Optional[list[float]]:
        return self.data.value_store.get_recv(self._member, self._field)

    def try_get(self) -> Optional[float]:
        v = self.try_get_vec()
        return v[0] if v is not None else None

    def get_vec(self) -> list[float]:
        v = self.try_get_vec()
        return v if v is not None else []

    def get(self) -> float:
        v = self.try_get()
        return v if v is not None else 0

    def set(self, data: list[float] | float) -> Value:
        self._set_check()
        if isinstance(data, int):
            self.data.value_store.set_send(self._field, [data])
            self.signal.send(self)
        elif isinstance(data, list):
            self.data.value_store.set_send(self._field, data)
            self.signal.send(self)
        return self


class Text(webcface.field.Field):
    def __init__(self, base: webcface.field.Field, field: str = "") -> None:
        super().__init__(base.data, base._member, field if field != "" else base._field)

    @property
    def member(self) -> webcface.member.Member:
        return webcface.member.Member(self)

    @property
    def name(self) -> str:
        return self._field

    @property
    def signal(self) -> signal:
        return signal(json.dumps(["textChange", self._member, self._field]))

    def child(self, field: str) -> Text:
        return Text(self, self._field + "." + field)

    def try_get(self) -> Optional[str]:
        return self.data.text_store.get_recv(self._member, self._field)

    def get(self) -> str:
        v = self.try_get()
        return v if v is not None else ""

    def set(self, data: str) -> Text:
        self._set_check()
        if isinstance(data, str):
            self.data.text_store.set_send(self._field, data)
            self.signal.send(self)
        return self
