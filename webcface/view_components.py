from __future__ import annotations
from typing import Callable
import webcface.view
import webcface.func

__all__ = ["text", "new_line", "button"]


def text(text: str, **kwargs) -> webcface.view.ViewComponent:
    """textコンポーネント

    kwargsに指定したプロパティはViewComponentのコンストラクタに渡される
    """
    return webcface.view.ViewComponent(
        type=webcface.view.ViewComponentType.TEXT, text=text, **kwargs
    )


def new_line() -> webcface.view.ViewComponent:
    """newLineコンポーネント

    kwargsに指定したプロパティはViewComponentのコンストラクタに渡される
    """
    return webcface.view.ViewComponent(type=webcface.view.ViewComponentType.NEW_LINE)


def button(
    text: str, on_click: webcface.func.Func | webcface.func.AnonymousFunc | Callable
) -> webcface.view.ViewComponent:
    """buttonコンポーネント

    kwargsに指定したプロパティはViewComponentのコンストラクタに渡される
    """
    return webcface.view.ViewComponent(
        type=webcface.view.ViewComponentType.BUTTON, text=text, on_click=on_click
    )
