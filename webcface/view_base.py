from __future__ import annotations
from typing import Optional
import webcface.field
import webcface.client_data

class ViewComponentBase:
    _type: int
    _text: str
    _on_click_func: Optional[webcface.field.FieldBase]
    _text_color: int
    _bg_color: int

    def __init__(
        self,
        type: int = 0,
        text: str = "",
        on_click: Optional[webcface.field.FieldBase] = None,
        text_color: int = 0,
        bg_color: int = 0,
    ) -> None:
        self._type = type
        self._text = text
        self._on_click_func = on_click
        self._text_color = text_color
        self._bg_color = bg_color

