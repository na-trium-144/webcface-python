from __future__ import annotations
from typing import Optional, List, Union
import webcface.field
import webcface.client_data


class ViewComponentBase:
    _type: int
    _text: str
    _on_click_func: Optional[webcface.field.FieldBase]
    _text_ref: Optional[webcface.field.FieldBase]
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
        on_click: Optional[webcface.field.FieldBase] = None,
        text_ref: Optional[webcface.field.FieldBase] = None,
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
