from __future__ import annotations
from typing import Optional, List
import webcface.field
import webcface.client_data


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
