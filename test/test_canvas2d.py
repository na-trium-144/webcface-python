from conftest import self_name
import pytest
from webcface.canvas2d import Canvas2D, Canvas2DComponent, Canvas2DData
from webcface.canvas2d_base import (
    Canvas2DComponentBase,
    Canvas2DComponentType,
)
import webcface.geometries as geometries
from webcface.field import Field
from webcface.member import Member
from webcface.transform import Transform, Point
from webcface.view_base import ViewColor


def test_canvas2d_member(data):
    assert isinstance(Canvas2D(Field(data, "a", "b")).member, Member)
    assert Canvas2D(Field(data, "a", "b")).member.name == "a"


def test_canvas2d_name(data):
    assert Canvas2D(Field(data, "a", "b")).name == "b"


def test_canvas2d_child(data):
    c = Canvas2D(Field(data, "a", "b")).child("c")
    assert isinstance(c, Canvas2D)
    assert c.member.name == "a"
    assert c.name == "b.c"


def test_canvas2d_try_get(data):
    assert Canvas2D(Field(data, "a", "b")).try_get() is None
    assert data.canvas2d_store.req.get("a", {}).get("b", 0) == 1

    Canvas2D(Field(data, self_name, "b")).try_get()
    assert self_name not in data.canvas2d_store.req

    data.canvas2d_store.data_recv["a"] = {"b": Canvas2DData(100, 50)}
    data.canvas2d_store.data_recv["a"]["b"].components = {"0": Canvas2DComponentBase()}
    data.canvas2d_store.data_recv["a"]["b"].ids = ["0"]
    assert len(Canvas2D(Field(data, "a", "b")).try_get()) == 1
    assert isinstance(
        Canvas2D(Field(data, "a", "b")).try_get()[0], Canvas2DComponentBase
    )


def test_canvas2d_get(data):
    assert Canvas2D(Field(data, "a", "b")).get() == []
    assert data.canvas2d_store.req.get("a", {}).get("b", 0) == 1
    assert Canvas2D(Field(data, "a", "b")).width == 0
    assert Canvas2D(Field(data, "a", "b")).height == 0

    Canvas2D(Field(data, self_name, "b")).get()
    assert self_name not in data.view_store.req

    data.canvas2d_store.data_recv["a"] = {"b": Canvas2DData(100, 50)}
    data.canvas2d_store.data_recv["a"]["b"].components = {"0": Canvas2DComponentBase()}
    data.canvas2d_store.data_recv["a"]["b"].ids = ["0"]
    assert Canvas2D(Field(data, "a", "b")).width == 100
    assert Canvas2D(Field(data, "a", "b")).height == 50
    assert len(Canvas2D(Field(data, "a", "b")).get()) == 1
    assert isinstance(Canvas2D(Field(data, "a", "b")).get()[0], Canvas2DComponentBase)


def test_canvas2d_set(data):
    with Canvas2D(Field(data, self_name, "b"), "", 100, 50) as v:
        called = 0

        def callback(v):
            assert v.member.name == self_name
            assert v.name == "b"
            nonlocal called
            called += 1

        v.on_change(callback)

        v.add(
            geometries.line([0, 0], [100, 50]),
            origin=Transform([1, 2], 3),
            color=ViewColor.YELLOW,
            fill=ViewColor.GREEN,
            stroke_width=123,
        )
        v.add(geometries.rect([0, 0], [100, 50]), id="aaa")
        v.add(geometries.circle([[10, 10], 0], 5))
        v.add(geometries.polygon([[1, 1], [2, 2], [3, 3]]))

    vd = data.canvas2d_store.data_send.get("b")
    assert vd.width == 100
    assert vd.height == 50
    vc = [vd.components[i] for i in vd.ids]
    assert vc[0]._type == Canvas2DComponentType.GEOMETRY
    assert vc[0]._origin_pos == [1, 2]
    assert vc[0]._origin_rot == 3
    assert vc[0]._color == ViewColor.YELLOW
    assert vc[0]._fill == ViewColor.GREEN
    assert vc[0]._stroke_width == 123
    assert vc[0]._geometry_type == geometries.GeometryType.LINE
    vcc = [Canvas2DComponent(vd.components[i], data, i) for i in vd.ids]
    assert vcc[0].geometry.as_line.begin == Point([0, 0])
    assert vcc[0].geometry.as_line.end == Point([100, 50])
    assert vcc[0].id == "..0.0"

    assert vcc[1].geometry.as_rect.vertex1 == Point([0, 0])
    assert vcc[1].geometry.as_rect.vertex2 == Point([100, 50])
    assert vcc[1].id == "aaa"

    # assert vcc[2].geometry.as_circle.origin == Transform([10, 10], 0)
    assert vcc[2].geometry.as_circle.radius == 5

    assert vcc[3].geometry.as_polygon.points == [
        Point([1, 1]),
        Point([2, 2]),
        Point([3, 3]),
    ]

    assert called == 1

    # v.init()
    # v.sync()
    with Canvas2D(Field(data, self_name, "b"), "", 1, 1) as v:
        pass
    vd = data.canvas2d_store.data_send.get("b")
    assert len(vd.components) == 0
    assert called == 2

    with pytest.raises(ValueError) as e:
        Canvas2D(Field(data, "a", "b")).sync()
