from conftest import self_name
import pytest
from webcface.view import View, ViewComponent, ViewData
from webcface.view_base import ViewComponentType, ViewColor
from webcface.view_base import ViewComponentBase
import webcface.components as view
from webcface.func import Func
from webcface.field import Field
from webcface.member import Member
from webcface.text import InputRef


def test_view_member(data):
    assert isinstance(View(Field(data, "a", "b")).member, Member)
    assert View(Field(data, "a", "b")).member.name == "a"


def test_view_name(data):
    assert View(Field(data, "a", "b")).name == "b"


def test_view_child(data):
    c = View(Field(data, "a", "b")).child("c")
    assert isinstance(c, View)
    assert c.member.name == "a"
    assert c.name == "b.c"


def test_view_try_get(data):
    assert View(Field(data, "a", "b")).try_get() is None
    assert data.view_store.req.get("a", {}).get("b", 0) == 1

    View(Field(data, self_name, "b")).try_get()
    assert self_name not in data.view_store.req

    vdata = ViewData()
    vdata.components = {"0": view.text("a").lock_tmp(data, "", "", "0").to_view()}
    vdata.ids = ["0"]
    data.view_store.data_recv["a"] = {"b": vdata}
    assert len(View(Field(data, "a", "b")).try_get()) == 1
    assert isinstance(View(Field(data, "a", "b")).try_get()[0], ViewComponent)


def test_view_get(data):
    assert View(Field(data, "a", "b")).get() == []
    assert data.view_store.req.get("a", {}).get("b", 0) == 1

    View(Field(data, self_name, "b")).get()
    assert self_name not in data.view_store.req

    vdata = ViewData()
    vdata.components = {"0": view.text("a").lock_tmp(data, "", "", "0").to_view()}
    vdata.ids = ["0"]
    data.view_store.data_recv["a"] = {"b": vdata}
    assert len(View(Field(data, "a", "b")).get()) == 1
    assert isinstance(View(Field(data, "a", "b")).get()[0], ViewComponent)


def test_view_set(data):
    with View(Field(data, self_name, "b")) as v:
        called = 0

        def callback(v):
            assert v.member.name == self_name
            assert v.name == "b"
            nonlocal called
            called += 1

        v.on_change(callback)
        v.add("a\n").add(1)
        v.add(
            view.text("aaa", text_color=ViewColor.YELLOW, bg_color=ViewColor.GREEN),
            view.new_line(),
        )
        v.add(
            view.button("f", Func(Field(data, self_name, "f")), bg_color=ViewColor.RED),
            view.button("a3", lambda: 3),
        )
        ref1 = InputRef()
        ref2 = InputRef()
        v.add(view.decimal_input("i", bind=ref1, init=123, min=1, max=1000))
        v.add(view.select_input("i2", bind=ref2, option=["a", "b", "c"]))
        called_ref3 = 0

        def on_change_ref3(val):
            nonlocal called_ref3
            called_ref3 += 1
            assert val == "aaa"

        v.add(view.text_input("i3", on_change=on_change_ref3))

        # v.sync()

    vdata = data.view_store.data_send.get("b", [])
    vd = [vdata.components[v_id] for v_id in vdata.ids]
    assert vd[0]._type == ViewComponentType.TEXT
    assert vd[0]._text == "a"
    assert vd[1]._type == ViewComponentType.NEW_LINE
    assert vd[2]._type == ViewComponentType.TEXT
    assert vd[2]._text == "1"

    assert vd[3]._type == ViewComponentType.TEXT
    assert vd[3]._text, "aaa"
    assert vd[3]._text_color == ViewColor.YELLOW
    assert vd[3]._bg_color == ViewColor.GREEN
    assert vd[4]._type == ViewComponentType.NEW_LINE

    assert vd[5]._type == ViewComponentType.BUTTON
    assert vd[5]._text == "f"
    assert vd[5]._on_click_func._member == self_name
    assert vd[5]._on_click_func._field == "f"
    assert vd[5]._bg_color == ViewColor.RED
    assert vd[6]._type == ViewComponentType.BUTTON
    assert vd[6]._text == "a3"
    assert vd[6]._on_click_func._member == self_name
    assert vd[6]._on_click_func._field != ""

    assert vd[7]._type == ViewComponentType.DECIMAL_INPUT
    assert vd[7]._text == "i"
    assert vd[7]._on_click_func._member == self_name
    assert vd[7]._on_click_func._field != ""
    assert float(ref1.get()) == 123
    Func(Field(data, self_name, vd[7]._on_click_func._field)).run(10)
    assert float(ref1.get()) == 10
    assert vd[7]._min == 1
    assert vd[7]._max == 1000

    assert vd[8]._type == ViewComponentType.SELECT_INPUT
    assert vd[8]._text == "i2"
    assert vd[8]._on_click_func._member == self_name
    assert vd[8]._on_click_func._field != ""
    assert len(vd[8]._option) == 3
    Func(Field(data, self_name, vd[8]._on_click_func._field)).run("a")
    assert ref2.get() == "a"

    assert vd[9]._type == ViewComponentType.TEXT_INPUT
    assert vd[9]._text == "i3"
    assert vd[9]._on_click_func._member == self_name
    assert vd[9]._on_click_func._field != ""
    Func(Field(data, self_name, vd[9]._on_click_func._field)).run("aaa")
    assert called_ref3 == 1

    assert called == 1

    # v.init()
    # v.sync()
    with View(Field(data, self_name, "b")) as v:
        pass
    vdata = data.view_store.data_send.get("b", [])
    assert len(vdata.components) == 0
    assert called == 2

    with pytest.raises(ValueError) as e:
        View(Field(data, "a", "b")).sync()
