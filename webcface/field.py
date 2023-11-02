from __future__ import annotations
import webcface.client_data


class FieldBase:
    _member: str
    _field: str

    def __init__(self, member: str, field: str = "") -> None:
        self._member = member
        self._field = field


class Field(FieldBase):
    data: webcface.client_data.ClientData

    def __init__(
        self, data: webcface.client_data.ClientData, member: str, field: str = ""
    ) -> None:
        super().__init__(member, field)
        self.data = data

    def _set_check(self) -> None:
        if not isinstance(self.data, webcface.client_data.ClientData):
            raise RuntimeError("Cannot access internal data")
        if not self.data.is_self(self._member):
            raise ValueError("Cannot set data to member other than self")
