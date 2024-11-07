from typing import Callable, Union
import webcface.temporal_component
import webcface.view_base
import webcface.func

__all__ = ["text", "new_line", "button"]


def text(text: str, **kwargs) -> "webcface.temporal_component.TemporalComponent":
    """text要素"""
    return webcface.temporal_component.TemporalComponent(
        view_type=webcface.view_base.ViewComponentType.TEXT, text=text, **kwargs
    )


def new_line(**kwargs) -> "webcface.temporal_component.TemporalComponent":
    """newLine要素"""
    return webcface.temporal_component.TemporalComponent(
        view_type=webcface.view_base.ViewComponentType.NEW_LINE, **kwargs
    )


def button(
    text: str,
    on_click: "Union[webcface.func.Func, Callable]",
    **kwargs,
) -> "webcface.temporal_component.TemporalComponent":
    """button要素"""
    return webcface.temporal_component.TemporalComponent(
        view_type=webcface.view_base.ViewComponentType.BUTTON,
        text=text,
        on_click=on_click,
        **kwargs,
    )


def text_input(
    text: str = "", **kwargs
) -> "webcface.temporal_component.TemporalComponent":
    """textInput要素 (ver2.0〜)"""
    return webcface.temporal_component.TemporalComponent(
        view_type=webcface.view_base.ViewComponentType.TEXT_INPUT, text=text, **kwargs
    )


def decimal_input(
    text: str = "", **kwargs
) -> "webcface.temporal_component.TemporalComponent":
    """decimalInput要素 (ver2.0〜)"""
    return webcface.temporal_component.TemporalComponent(
        view_type=webcface.view_base.ViewComponentType.DECIMAL_INPUT,
        text=text,
        **kwargs,
    )


def number_input(
    text: str = "", **kwargs
) -> "webcface.temporal_component.TemporalComponent":
    """numberInput要素 (ver2.0〜)"""
    return webcface.temporal_component.TemporalComponent(
        view_type=webcface.view_base.ViewComponentType.NUMBER_INPUT, text=text, **kwargs
    )


def toggle_input(
    text: str = "", **kwargs
) -> "webcface.temporal_component.TemporalComponent":
    """toggleInput要素 (ver2.0〜)"""
    return webcface.temporal_component.TemporalComponent(
        view_type=webcface.view_base.ViewComponentType.TOGGLE_INPUT, text=text, **kwargs
    )


def select_input(
    text: str = "", **kwargs
) -> "webcface.temporal_component.TemporalComponent":
    """selectInput要素 (ver2.0〜)"""
    return webcface.temporal_component.TemporalComponent(
        view_type=webcface.view_base.ViewComponentType.SELECT_INPUT, text=text, **kwargs
    )


def slider_input(
    text: str = "", **kwargs
) -> "webcface.temporal_component.TemporalComponent":
    """sliderInput要素 (ver2.0〜)"""
    return webcface.temporal_component.TemporalComponent(
        view_type=webcface.view_base.ViewComponentType.SLIDER_INPUT, text=text, **kwargs
    )


def check_input(
    text: str = "", **kwargs
) -> "webcface.temporal_component.TemporalComponent":
    """checkInput要素 (ver2.0〜)"""
    return webcface.temporal_component.TemporalComponent(
        view_type=webcface.view_base.ViewComponentType.CHECK_INPUT, text=text, **kwargs
    )
