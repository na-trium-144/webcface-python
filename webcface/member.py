from __future__ import annotations
import webcface.field
import webcface.data


class Member(webcface.field.Field):
    def __init__(self, base: webcface.field.Field, member: str = "") -> None:
        super().__init__(base.data, member if member != "" else base._member)

    @property
    def name(self) -> str:
        return self._member

    def value(self, field: str) -> webcface.data.Value:
        return webcface.data.Value(self, field)

    def text(self, field: str) -> webcface.data.Text:
        return webcface.data.Text(self, field)
