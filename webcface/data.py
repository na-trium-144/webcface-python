from __future__ import annotations
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

    def child(self, field: str) -> Value:
        return Value(self, self._field + "." + field)

    def try_get_vec(self) -> list[float] | None:
        return self.data.value_store.get_recv(self._member, self._field)

    def try_get(self) -> float | None:
        v = self.try_get_vec()
        return v[0] if v is not None else None

    def get_vec(self) -> list[float]:
        v = self.try_get_vec()
        return v if v is not None else []

    def get(self) -> float:
        v = self.try_get()
        return v if v is not None else 0

    def set(self, data: list[float] | float) -> None:
        if self.data.is_self(self._member):
            if isinstance(data, int):
                self.data.value_store.set_send(self._field, [data])
                # self.triggerEvent()
            elif isinstance(data, list):
                self.data.value_store.set_send(self._field, data)
                # self.triggerEvent()
        else:
            raise ValueError("Cannot set data to member other than self")