from __future__ import annotations
from enum import IntEnum
from typing import Optional, Callable
from copy import deepcopy
import json
from blinker import signal
import webcface.field
import webcface.view_base
import webcface.client_data
import webcface.func


class ViewComponentType(IntEnum):
    TEXT = 0
    NEW_LINE = 1
    BUTTON = 2


class ViewColor(IntEnum):
    INHERIT = 0
    BLACK = 1
    WHITE = 2
    GRAY = 4
    RED = 8
    ORANGE = 9
    YELLOW = 11
    GREEN = 13
    TEAL = 15
    CYAN = 16
    BLUE = 18
    INDIGO = 19
    PURPLE = 21
    PINK = 23


class ViewComponent(webcface.view_base.ViewComponentBase):
    _data: Optional[webcface.client_data.ClientData]
    _on_click_func_tmp: Optional[webcface.func.AnonymousFunc]

    @staticmethod
    def from_base(
        base: webcface.view_base.ViewComponentBase,
    ) -> ViewComponent:
        vc = ViewComponent(
            base._type,
            base._text,
            base._on_click_func,
            base._text_color,
            base._bg_color,
        )
        vc._data = base._data
        return vc

    def __init__(
        self,
        type: int = 0,
        text: str = "",
        on_click: Optional[webcface.field.FieldBase | Callable] = None,
        text_color: int = 0,
        bg_color: int = 0,
    ) -> None:
        super().__init__(type, text, None, text_color, bg_color)
        self._data = None
        self._on_click_func = None
        self._on_click_func_tmp = None
        if isinstance(on_click, webcface.func.AnonymousFunc):
            self._on_click_func_tmp = on_click
        elif isinstance(on_click, webcface.field.FieldBase):
            self._on_click_func = on_click
        elif callable(on_click):
            self._on_click_func_tmp = webcface.func.AnonymousFunc(None, on_click)
        if isinstance(on_click, webcface.field.Field) and on_click.data is not None:
            self._data = on_click.data

    def lock_tmp(
        self, data: webcface.client_data.ClientData, field_id: str
    ) -> ViewComponent:
        if self._on_click_func_tmp is not None:
            on_click = webcface.func.Func(
                webcface.field.Field(data, data.self_member_name), field_id
            )
            self._on_click_func_tmp.lock_to(on_click)
            on_click.hidden = True
            self._on_click_func = on_click
        self._data = data
        return self

    def __eq__(self, other) -> bool:
        return (
            isinstance(other, ViewComponent)
            and self._type == other._type
            and self._text == other._text
            and (
                (self._on_click_func is None and other._on_click_func is None)
                or (
                    self._on_click_func is not None
                    and other._on_click_func is not None
                    and self._on_click_func._member == other._on_click_func._member
                    and self._on_click_func._field == other._on_click_func._field
                )
            )
            and self._text_color == other._text_color
            and self._bg_color == other._bg_color
        )

    def __ne__(self, other) -> bool:
        return not self == other

    @property
    def type(self) -> int:
        return self._type

    @property
    def text(self) -> str:
        return self._text

    @property
    def on_click(self) -> Optional[webcface.func.Func]:
        if self._on_click_func is not None:
            if self._data is None:
                raise RuntimeError("internal data not set")
            return webcface.func.Func(
                webcface.field.Field(
                    self._data, self._on_click_func._member, self._on_click_func._field
                )
            )
        return None

    @property
    def text_color(self) -> int:
        return self._text_color

    @property
    def bg_color(self) -> int:
        return self._bg_color


def text(text: str, **kwargs) -> ViewComponent:
    return ViewComponent(type=ViewComponentType.TEXT, text=text, **kwargs)


def new_line() -> ViewComponent:
    return ViewComponent(type=ViewComponentType.NEW_LINE)


def button(
    text: str, on_click: webcface.func.Func | webcface.func.AnonymousFunc | Callable
) -> ViewComponent:
    return ViewComponent(type=ViewComponentType.BUTTON, text=text, on_click=on_click)


class View(webcface.field.Field):
    _components: list[ViewComponent | str | bool | float | int]

    def __init__(self, base: webcface.field.Field, field: str = "") -> None:
        super().__init__(base.data, base._member, field if field != "" else base._field)
        self._components = []
        if self.data.is_self(self._field):
            self.init()

    def __del__(self) -> None:
        if self.data.is_self(self._field):
            self.sync()

    @property
    def member(self) -> webcface.member.Member:
        return webcface.member.Member(self)

    @property
    def name(self) -> str:
        return self._field

    @property
    def signal(self) -> signal:
        return signal(json.dumps(["viewChange", self._member, self._field]))

    def child(self, field: str) -> View:
        return View(self, self._field + "." + field)

    def try_get(self) -> Optional[list[ViewComponent]]:
        v = self.data.view_store.get_recv(self._member, self._field)
        v2: Optional[list[ViewComponent]] = None
        if v is not None:
            v2 = list(map(ViewComponent.from_base, v))
        return v2

    def get(self) -> list[ViewComponent]:
        v = self.try_get()
        return v if v is not None else []

    def set(self, components: list[ViewComponent | str | bool | float | int]) -> View:
        self._set_check()
        data2 = []
        for c in components:
            if isinstance(c, ViewComponent):
                data2.append(c)
            elif isinstance(c, str):
                while "\n" in c:
                    s = c[: c.find("\n")]
                    data2.append(text(s))
                    data2.append(new_line())
                    c = c[c.find("\n") + 1 :]
                if c != "":
                    data2.append(text(c))
            else:
                data2.append(text(str(c)))
        for i, c in enumerate(data2):
            data2[i] = c.lock_tmp(self.data, f"{self._field}_f{i}")
        self.data.view_store.set_send(self._field, list(data2))
        self.signal.send(self)
        return self

    def init(self) -> View:
        self._components = []
        return self

    def sync(self) -> View:
        self.set(self._components)
        return self

    def add(self, *args: ViewComponent | str | bool | float | int) -> View:
        for c in args:
            self._components.append(c)
        return self
