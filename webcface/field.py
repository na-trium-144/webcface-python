from typing import Optional
import webcface.client_data


class FieldBase:
    _member: str
    _field: str

    def __init__(self, member: str, field: str = "") -> None:
        self._member = member
        self._field = field


class Field(FieldBase):
    _data: "Optional[webcface.client_data.ClientData]"

    def __init__(
        self,
        data: "Optional[webcface.client_data.ClientData]",
        member: str,
        field: str = "",
    ) -> None:
        super().__init__(member, field)
        self._data = data

    def _data_check(self) -> "webcface.client_data.ClientData":
        if isinstance(self._data, webcface.client_data.ClientData):
            return self._data
        raise RuntimeError("Cannot access internal data")

    def _set_check(self) -> "webcface.client_data.ClientData":
        data = self._data_check()
        if data.is_self(self._member):
            return data
        raise ValueError("Cannot set data to member other than self")
