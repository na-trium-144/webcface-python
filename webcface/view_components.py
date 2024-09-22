from __future__ import annotations
from typing import Callable, Union
from enum import IntEnum
import webcface.view
import webcface.func

__all__ = ["ViewComponentType", "ViewColor", "text", "new_line", "button"]


class ViewComponentType(IntEnum):
    TEXT = 0
    NEW_LINE = 1
    BUTTON = 2
    TEXT_INPUT = 3
    DECIMAL_INPUT = 4
    NUMBER_INPUT = 5
    TOGGLE_INPUT = 6
    SELECT_INPUT = 7
    SLIDER_INPUT = 8
    CHECK_INPUT = 9


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
    """newLineコンポーネント"""
    return webcface.view.ViewComponent(type=ViewComponentType.NEW_LINE)


def button(
    text: str,
    on_click: Union[webcface.func.Func, Callable],
    **kwargs,
) -> webcface.view.ViewComponent:
    """buttonコンポーネント

    kwargsに指定したプロパティはViewComponentのコンストラクタに渡される
    """
    return webcface.view.ViewComponent(
        type=ViewComponentType.BUTTON, text=text, on_click=on_click, **kwargs
    )


def text_input(text: str = "", **kwargs) -> webcface.view.ViewComponent:
    """textInputコンポーネント
    (ver2.0〜)
    """
    return webcface.view.ViewComponent(
        type=ViewComponentType.TEXT_INPUT, text=text, **kwargs
    )


def decimal_input(text: str = "", **kwargs) -> webcface.view.ViewComponent:
    """decimalInputコンポーネント
    (ver2.0〜)
    """
    return webcface.view.ViewComponent(
        type=ViewComponentType.DECIMAL_INPUT, text=text, **kwargs
    )


def number_input(text: str = "", **kwargs) -> webcface.view.ViewComponent:
    """numberInputコンポーネント
    (ver2.0〜)
    """
    return webcface.view.ViewComponent(
        type=ViewComponentType.NUMBER_INPUT, text=text, **kwargs
    )


def toggle_input(text: str = "", **kwargs) -> webcface.view.ViewComponent:
    """toggleInputコンポーネント
    (ver2.0〜)
    """
    return webcface.view.ViewComponent(
        type=ViewComponentType.TOGGLE_INPUT, text=text, **kwargs
    )


def select_input(text: str = "", **kwargs) -> webcface.view.ViewComponent:
    """selectInputコンポーネント
    (ver2.0〜)
    """
    return webcface.view.ViewComponent(
        type=ViewComponentType.SELECT_INPUT, text=text, **kwargs
    )


def slider_input(text: str = "", **kwargs) -> webcface.view.ViewComponent:
    """sliderInputコンポーネント
    (ver2.0〜)
    """
    return webcface.view.ViewComponent(
        type=ViewComponentType.SLIDER_INPUT, text=text, **kwargs
    )


def check_input(text: str = "", **kwargs) -> webcface.view.ViewComponent:
    """checkInputコンポーネント
    (ver2.0〜)
    """
    return webcface.view.ViewComponent(
        type=ViewComponentType.CHECK_INPUT, text=text, **kwargs
    )
