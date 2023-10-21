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
