from __future__ import annotations
from typing import Optional, List, Dict
from enum import IntEnum
import webcface.field


class Canvas3DComponentType(IntEnum):
    GEOMETRY = 0
    ROBOT_MODEL = 1


class Canvas3DComponentBase:
    _type: int
    _origin_pos: List[float]
    _origin_rot: List[float]
    _color: int
    _geometry_type: Optional[int]
    _geometry_properties: List[float]
    _field_member: Optional[str]
    _field_field: Optional[str]
    _angles: Dict[str, float]

    def __init__(
        self,
        type: int = 0,
        origin_pos: Optional[List[float]] = None,
        origin_rot: Optional[List[float]] = None,
        color: int = 0,
        geometry_type: int = 0,
        geometry_properties: Optional[List[float]] = None,
        field_member: Optional[str] = None,
        field_field: Optional[str] = None,
        angles: Optional[Dict[str, float]] = None,
    ) -> None:
        self._type = type
        self._origin_pos = origin_pos or []
        self._origin_rot = origin_rot or []
        self._color = color
        self._geometry_type = geometry_type
        self._geometry_properties = geometry_properties or []
        self._field_member = field_member
        self._field_field = field_field
        self._angles = angles or {}

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, Canvas3DComponentBase)
            and self._type == other._type
            and self._origin_pos == other._origin_pos
            and self._origin_rot == other._origin_rot
            and self._color == other._color
            and self._geometry_type == other._geometry_type
            and self._geometry_properties == other._geometry_properties
            and self._field_member == other._field_member
            and self._field_field == other._field_field
            and self._angles == other._angles
        )
