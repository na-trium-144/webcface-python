from __future__ import annotations
from typing import Callable, Optional
import webcface.field
import webcface.data
import webcface.view
import webcface.func


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

    def view(self, field: str) -> webcface.view.View:
        return webcface.view.View(self, field)

    def func(
        self, arg: Optional[str | Callable] = None, **kwargs
    ) -> webcface.func.Func | webcface.func.AnonymousFunc:
        if isinstance(arg, str):
            return webcface.func.Func(self, arg, **kwargs)
        else:
            return webcface.func.AnonymousFunc(self, arg, **kwargs)
