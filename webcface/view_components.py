from __future__ import annotations
from typing import Callable
from enum import IntEnum
import webcface.view
import webcface.func

__all__ = ["ViewComponentType", "ViewColor", "text", "new_line", "button"]


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


def text(text: str, **kwargs) -> webcface.view.ViewComponent:
    """textコンポーネント

    kwargsに指定したプロパティはViewComponentのコンストラクタに渡される
    """
    return webcface.view.ViewComponent(type=ViewComponentType.TEXT, text=text, **kwargs)


def new_line() -> webcface.view.ViewComponent:
    """newLineコンポーネント

    kwargsに指定したプロパティはViewComponentのコンストラクタに渡される
    """
    return webcface.view.ViewComponent(type=ViewComponentType.NEW_LINE)


def button(
    text: str,
    on_click: webcface.func.Func | webcface.func.AnonymousFunc | Callable,
    **kwargs,
) -> webcface.view.ViewComponent:
    """buttonコンポーネント

    kwargsに指定したプロパティはViewComponentのコンストラクタに渡される
    """
    return webcface.view.ViewComponent(
        type=ViewComponentType.BUTTON, text=text, on_click=on_click, **kwargs
    )
