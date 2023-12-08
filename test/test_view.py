from conftest import self_name
import pytest
from webcface.view import View, ViewComponent
from webcface.view_components import ViewComponentType, ViewColor
from webcface.view_base import ViewComponentBase
import webcface.view_components as view
from webcface.func import Func, AnonymousFunc
from webcface.field import Field
from webcface.member import Member


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

    data.view_store.data_recv["a"] = {"b": [view.text("a").lock_tmp(data, "")]}
    assert len(View(Field(data, "a", "b")).try_get()) == 1
    assert isinstance(View(Field(data, "a", "b")).try_get()[0], ViewComponent)

    data.view_store.data_recv["a"] = {
        "b": [ViewComponentBase(type=ViewComponentType.TEXT, text="a")]
    }
    assert len(View(Field(data, "a", "b")).try_get()) == 1
    assert isinstance(View(Field(data, "a", "b")).try_get()[0], ViewComponent)


def test_view_get(data):
    assert View(Field(data, "a", "b")).get() == []
    assert data.view_store.req.get("a", {}).get("b", 0) == 1

    View(Field(data, self_name, "b")).get()
    assert self_name not in data.view_store.req

    data.view_store.data_recv["a"] = {"b": [view.text("a").lock_tmp(data, "")]}
    assert len(View(Field(data, "a", "b")).get()) == 1
    assert isinstance(View(Field(data, "a", "b")).get()[0], ViewComponent)

    data.view_store.data_recv["a"] = {
        "b": [ViewComponentBase(type=ViewComponentType.TEXT, text="a")]
    }
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

        v.signal.connect(callback)
        v.add("a\n").add(1)
        v.add(
            view.text("aaa", text_color=ViewColor.YELLOW, bg_color=ViewColor.GREEN),
            view.new_line(),
        )
        v.add(
            view.button("f", Func(Field(data, self_name, "f"))),
            view.button("a", AnonymousFunc(Field(data, self_name, "a"), lambda: 1)),
            view.button("a2", AnonymousFunc(None, lambda: 2)),
            view.button("a3", lambda: 3),
        )
        # v.sync()

    vd = data.view_store.data_send.get("b", [])
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
    assert vd[6]._type == ViewComponentType.BUTTON
    assert vd[6]._text == "a"
    assert vd[6]._on_click_func._member == self_name
    assert vd[6]._on_click_func._field != "a"
    assert vd[7]._type == ViewComponentType.BUTTON
    assert vd[7]._text == "a2"
    assert vd[7]._on_click_func._member == self_name
    assert vd[7]._on_click_func._field != ""
    assert vd[8]._type == ViewComponentType.BUTTON
    assert vd[8]._text == "a3"
    assert vd[8]._on_click_func._member == self_name
    assert vd[8]._on_click_func._field != ""
    assert called == 1

    # v.init()
    # v.sync()
    with View(Field(data, self_name, "b")) as v:
        pass
    vd = data.view_store.data_send.get("b", [])
    assert len(vd) == 0
    assert called == 2

    with pytest.raises(ValueError) as e:
        View(Field(data, "a", "b")).sync()
