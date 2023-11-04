from __future__ import annotations
from enum import IntEnum
from typing import Optional, Callable
from copy import deepcopy
import json
from blinker import signal
import webcface.client_data
import webcface.field
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


class ViewComponent:
    _type: int
    _text: str
    _on_click_func: Optional[webcface.func.Func]
    _on_click_func_tmp: Optional[webcface.func.AnonymousFunc]
    _text_color: int
    _bg_color: int

    def __init__(
        self,
        type: int = 0,
        text: str = "",
        on_click: Optional[
            webcface.func.Func | webcface.func.AnonymousFunc | Callable
        ] = None,
        text_color: int = 0,
        bg_color: int = 0,
    ) -> None:
        self._type = type
        self._text = text
        self._on_click_func = None
        self._on_click_func_tmp = None
        if isinstance(on_click, webcface.func.AnonymousFunc):
            self._on_click_func_tmp = on_click
        elif isinstance(on_click, webcface.func.Func):
            self._on_click_func = on_click
        elif callable(on_click):
            self._on_click_func_tmp = webcface.func.AnonymousFunc(None, on_click)
        self._text_color = text_color
        self._bg_color = bg_color

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
        return self

    @property
    def type(self) -> int:
        return self._type

    @property
    def text(self) -> str:
        return self._text

    @property
    def on_click(self) -> Optional[webcface.func.Func]:
        return self._on_click_func

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
        return deepcopy(self.data.view_store.get_recv(self._member, self._field))

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
        self.data.view_store.set_send(self._field, data2)
        return self

    def init(self) -> View:
        self._components = []
        return self

    def sync(self) -> View:
        self.set(self._components)
        return self

    def add(self, c: ViewComponent | str | bool | float | int) -> View:
        self._components.append(c)
        return self
