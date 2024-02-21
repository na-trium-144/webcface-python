from __future__ import annotations
from typing import Optional, List
from enum import IntEnum


class Canvas2DComponentType(IntEnum):
    GEOMETRY = 0


class Canvas2DComponentBase:
    _type: int
    _origin_pos: List[float]
    _origin_rot: float
    _color: int
    _fill: int
    _stroke_width: float
    _geometry_type: int
    _geometry_properties: List[float]

    def __init__(
        self,
        type: int = 0,
        origin_pos: Optional[List[float]] = None,
        origin_rot: float = 0,
        color: int = 0,
        fill: int = 0,
        stroke_width: float = 0,
        geometry_type: int = 0,
        geometry_properties: Optional[List[float]] = None,
    ) -> None:
        self._type = type
        self._origin_pos = origin_pos or []
        self._origin_rot = origin_rot
        self._color = color
        self._fill = fill
        self._stroke_width = stroke_width
        self._geometry_type = geometry_type
        self._geometry_properties = geometry_properties or []

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, Canvas2DComponentBase)
            and self._type == other._type
            and self._origin_pos == other._origin_pos
            and self._origin_rot == other._origin_rot
            and self._color == other._color
            and self._fill == other._fill
            and self._stroke_width == other._stroke_width
            and self._geometry_type == other._geometry_type
            and self._geometry_properties == other._geometry_properties
        )


class Canvas2DData:
    components: List[Canvas2DComponentBase]
    width: float
    height: float

    def __init__(self, width: float, height: float) -> None:
        if width <= 0 or height <= 0:
            raise ValueError(f"Invalid Canvas2D size ({width} x {height})")
        self.components = []
        self.width = width
        self.height = height
