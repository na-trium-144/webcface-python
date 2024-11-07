from typing import List, Union, SupportsFloat, Sequence, Tuple
from enum import IntEnum
import webcface.transform

__all__ = [
    "GeometryType",
    "Geometry",
    "Geometry2D",
    "Geometry3D",
    "Line",
    "line",
    "Polygon",
    "polygon",
    "Plane",
    "plane",
    "rect",
    "Box",
    "box",
    "Circle",
    "circle",
    "Cylinder",
    "cylinder",
    "Sphere",
    "sphere",
]


class GeometryType(IntEnum):
    NONE = 0
    LINE = 1
    PLANE = 2
    RECT = 2
    BOX = 3
    CIRCLE = 4
    CYLINDER = 5
    SPHERE = 6
    POLYGON = 7


class Geometry:
    _geometry_type: int
    _properties: List[float]

    def __init__(self, geometry_type: int, properties: Sequence[SupportsFloat]) -> None:
        self._geometry_type = geometry_type
        self._properties = [float(p) for p in properties]

    @property
    def type(self) -> int:
        return self._geometry_type

    @property
    def as_line(self) -> "Line":
        return Line(self._properties)

    @property
    def as_plane(self) -> "Plane":
        return Plane(self._properties)

    @property
    def as_rect(self) -> "Plane":
        return Plane(self._properties)

    @property
    def as_box(self) -> "Box":
        return Box(self._properties)

    @property
    def as_circle(self) -> "Circle":
        return Circle(self._properties)

    @property
    def as_cylinder(self) -> "Cylinder":
        return Cylinder(self._properties)

    @property
    def as_sphere(self) -> "Sphere":
        return Sphere(self._properties)

    @property
    def as_polygon(self) -> "Polygon":
        return Polygon(self._properties)


class Line(Geometry):
    def __init__(self, properties: Sequence[SupportsFloat]) -> None:
        assert len(properties) == 6
        super().__init__(GeometryType.LINE, properties)

    @property
    def begin(self) -> "webcface.transform.Point":
        return webcface.transform.Point(self._properties[0:3])

    @property
    def end(self) -> "webcface.transform.Point":
        return webcface.transform.Point(self._properties[3:6])


def line(
    begin: "Union[webcface.transform.Point, Sequence[SupportsFloat]]",
    end: "Union[webcface.transform.Point, Sequence[SupportsFloat]]",
) -> Line:
    if not isinstance(begin, webcface.transform.Point):
        begin = webcface.transform.Point(begin)
    if not isinstance(end, webcface.transform.Point):
        end = webcface.transform.Point(end)
    return Line(list(begin.pos) + list(end.pos))


class Polygon(Geometry):
    def __init__(self, properties: Sequence[SupportsFloat]) -> None:
        assert len(properties) > 0 and len(properties) % 3 == 0
        super().__init__(GeometryType.POLYGON, properties)

    @property
    def points(self) -> "List[webcface.transform.Point]":
        points: List[webcface.transform.Point] = []
        for i in range(0, len(self._properties), 3):
            points.append(webcface.transform.Point(self._properties[i : i + 3]))
        return points


def polygon(
    points: "Sequence[Union[webcface.transform.Point, Sequence[SupportsFloat]]]",
) -> Polygon:
    props: List[float] = []
    for p in points:
        if not isinstance(p, webcface.transform.Point):
            p = webcface.transform.Point(p)
        props += list(p.pos)
    return Polygon(props)


class Plane(Geometry):
    def __init__(self, properties: Sequence[SupportsFloat]) -> None:
        assert len(properties) == 8
        super().__init__(GeometryType.PLANE, properties)

    @property
    def origin(self) -> "webcface.transform.Transform":
        return webcface.transform.Transform(
            self._properties[0:3],
            webcface.transform.rot_from_euler(self._properties[3:6]),
        )

    @property
    def width(self) -> float:
        return self._properties[6]

    @property
    def height(self) -> float:
        return self._properties[7]

    @property
    def vertex1(self) -> "webcface.transform.Point":
        return webcface.transform.Point(self.origin.pos) - webcface.transform.Point(
            [self.width / 2, self.height / 2, 0]
        )

    @property
    def vertex2(self) -> "webcface.transform.Point":
        return webcface.transform.Point(self.origin.pos) + webcface.transform.Point(
            [self.width / 2, self.height / 2, 0]
        )


def plane(
    origin: Union[
        "webcface.transform.Transform",
        "webcface.transform.Rotation",
        Tuple[
            Union["webcface.transform.Point", Sequence[SupportsFloat]],
            Union["webcface.transform.Rotation", SupportsFloat],
        ],
    ],
    width: SupportsFloat,
    height: SupportsFloat,
) -> Plane:
    origin = webcface.transform.convert_to_transform(origin)
    return Plane(list(origin.pos) + list(origin.rot) + [width, height])


def rect(
    begin: "Union[webcface.transform.Point, Sequence[SupportsFloat]]",
    end: "Union[webcface.transform.Point, Sequence[SupportsFloat]]",
) -> Plane:
    if not isinstance(begin, webcface.transform.Point):
        begin = webcface.transform.Point(begin)
    if not isinstance(end, webcface.transform.Point):
        end = webcface.transform.Point(end)
    origin = webcface.transform.translation(
        [(b + e) / 2 for b, e in zip(begin.pos, end.pos)],
    )
    width = abs(begin.pos[0] - end.pos[0])
    height = abs(begin.pos[1] - end.pos[1])
    return plane(origin, width, height)


class Box(Geometry):
    def __init__(self, properties: Sequence[SupportsFloat]) -> None:
        assert len(properties) == 6
        super().__init__(GeometryType.BOX, properties)

    @property
    def vertex1(self) -> "webcface.transform.Point":
        return webcface.transform.Point(self._properties[0:3])

    @property
    def vertex2(self) -> "webcface.transform.Point":
        return webcface.transform.Point(self._properties[3:6])


def box(
    vertex1: "Union[webcface.transform.Point, Sequence[SupportsFloat]]",
    vertex2: "Union[webcface.transform.Point, Sequence[SupportsFloat]]",
) -> Box:
    if not isinstance(vertex1, webcface.transform.Point):
        vertex1 = webcface.transform.Point(vertex1)
    if not isinstance(vertex2, webcface.transform.Point):
        vertex2 = webcface.transform.Point(vertex2)
    return Box(list(vertex1.pos) + list(vertex2.pos))


class Circle(Geometry):
    def __init__(self, properties: Sequence[SupportsFloat]) -> None:
        assert len(properties) == 7
        super().__init__(GeometryType.CIRCLE, properties)

    @property
    def origin(self) -> "webcface.transform.Transform":
        return webcface.transform.Transform(
            self._properties[0:3],
            webcface.transform.rot_from_euler(self._properties[3:6]),
        )

    @property
    def radius(self) -> float:
        return self._properties[6]


def circle(
    origin: Union[
        "webcface.transform.Point",
        Sequence[SupportsFloat],
        "webcface.transform.Transform",
        "webcface.transform.Rotation",
        Tuple[
            Union["webcface.transform.Point", Sequence[SupportsFloat]],
            Union["webcface.transform.Rotation", SupportsFloat],
        ],
    ],
    radius: SupportsFloat,
) -> Circle:
    origin = webcface.transform.convert_to_transform(origin)
    return Circle(list(origin.pos) + list(origin.rot) + [radius])


class Cylinder(Geometry):
    def __init__(self, properties: Sequence[SupportsFloat]) -> None:
        assert len(properties) == 8
        super().__init__(GeometryType.CYLINDER, properties)

    @property
    def origin(self) -> "webcface.transform.Transform":
        return webcface.transform.Transform(
            self._properties[0:3],
            webcface.transform.rot_from_euler(self._properties[3:6]),
        )

    @property
    def radius(self) -> float:
        return self._properties[6]

    @property
    def length(self) -> float:
        return self._properties[7]


def cylinder(
    origin: Union[
        "webcface.transform.Point",
        Sequence[SupportsFloat],
        "webcface.transform.Transform",
        "webcface.transform.Rotation",
        Tuple[
            Union["webcface.transform.Point", Sequence[SupportsFloat]],
            Union["webcface.transform.Rotation", SupportsFloat],
        ],
    ],
    radius: SupportsFloat,
    length: SupportsFloat,
) -> Cylinder:
    origin = webcface.transform.convert_to_transform(origin)
    return Cylinder(list(origin.pos) + list(origin.rot) + [radius, length])


class Sphere(Geometry):
    def __init__(self, properties: Sequence[SupportsFloat]) -> None:
        assert len(properties) == 4
        super().__init__(GeometryType.SPHERE, properties)

    @property
    def origin(self) -> "webcface.transform.Point":
        return webcface.transform.Point(self._properties[0:3])

    @property
    def radius(self) -> float:
        return self._properties[3]


def sphere(
    origin: "Union[webcface.transform.Point, Sequence[SupportsFloat]]",
    radius: SupportsFloat,
) -> Sphere:
    if not isinstance(origin, webcface.transform.Point):
        origin = webcface.transform.Point(origin)
    return Sphere(list(origin.pos) + [radius])


Geometry2D = Union[Line, Plane, Circle, Polygon]

Geometry3D = Union[Line, Plane, Box, Circle, Cylinder, Sphere, Polygon]
