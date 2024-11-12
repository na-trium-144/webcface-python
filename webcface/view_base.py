from typing import Optional, List, Union, Dict
from enum import IntEnum
import webcface.field


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


class ViewComponentBase:
    _type: int
    _text: str
    _on_click_func: "Optional[webcface.field.FieldBase]"
    _text_ref: "Optional[webcface.field.FieldBase]"
    _text_color: int
    _bg_color: int
    _min: Optional[float]
    _max: Optional[float]
    _step: Optional[float]
    _option: List[Union[float, bool, str]]

    def __init__(
        self,
        type: int = 0,
        text: str = "",
        on_click: "Optional[webcface.field.FieldBase]" = None,
        text_ref: "Optional[webcface.field.FieldBase]" = None,
        text_color: int = 0,
        bg_color: int = 0,
        min: Optional[float] = None,
        max: Optional[float] = None,
        step: Optional[float] = None,
        option: Optional[List[Union[float, bool, str]]] = None,
    ) -> None:
        self._type = type
        self._text = text
        self._on_click_func = on_click
        self._text_ref = text_ref
        self._text_color = text_color
        self._bg_color = bg_color
        self._min = min
        self._max = max
        self._step = step
        self._option = option or []
