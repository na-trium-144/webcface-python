from conftest import self_name
import datetime
import pytest
from webcface.value import Value
from webcface.text import Text
from webcface.func import Func, AnonymousFunc
from webcface.func_info import ValType, Arg
from webcface.field import Field
from webcface.view import View
from webcface.log import Log
from webcface.member import Member


def test_name(data):
    assert Member(Field(data, "a"), "").name == "a"


def test_value(data):
    v = Member(Field(data, "a"), "").value("b")
    assert isinstance(v, Value)
    assert v.member.name == "a"
    assert v.name == "b"


def test_text(data):
    v = Member(Field(data, "a"), "").text("b")
    assert isinstance(v, Text)
    assert v.member.name == "a"
    assert v.name == "b"


def test_func(data):
    m = Member(Field(data, self_name), "")
    f1 = m.func("b")
    assert isinstance(f1, Func)
    assert f1.member.name == self_name
    assert f1.name == "b"

    f2 = m.func()
    assert isinstance(f2, AnonymousFunc)
    assert f2.member.name == self_name
    assert f2.name.startswith(".")

    @m.func()
    def f3(a: int, b: float) -> int:
        return 123

    @m.func(args=[Arg(name="a", type=int), Arg(name="b", type=float)], return_type=int)
    def f4(a, b):
        return 123

    @m.func("f5")
    def f5_impl(a: int, b: float) -> int:
        return 123

    @m.func(
        "f6", args=[Arg(name="a", type=int), Arg(name="b", type=float)], return_type=int
    )
    def f6_impl(a, b):
        return 123

    assert f3(0, 0) == 123  # 関数自体は変わっていないか
    assert m.func("f3")(0, 0) == 123
    assert len(m.func("f3").args) == 2
    assert m.func("f3").return_type == ValType.INT

    assert f4(0, 0) == 123
    assert m.func("f4")(0, 0) == 123
    assert len(m.func("f4").args) == 2
    assert m.func("f4").return_type == ValType.INT

    assert f5_impl(0, 0) == 123
    assert m.func("f5")(0, 0) == 123
    assert len(m.func("f5").args) == 2
    assert m.func("f5").return_type == ValType.INT

    assert f6_impl(0, 0) == 123
    assert m.func("f6")(0, 0) == 123
    assert len(m.func("f6").args) == 2
    assert m.func("f6").return_type == ValType.INT


def test_view(data):
    v = Member(Field(data, "a"), "").view("b")
    assert isinstance(v, View)
    assert v.member.name == "a"
    assert v.name == "b"


def test_log(data):
    v = Member(Field(data, "a"), "").log()
    assert isinstance(v, Log)
    assert v.member.name == "a"


def test_values(data):
    data.value_store.entry = {"a": ["b", "c", "d"]}
    assert len(list(Member(Field(data, "a")).values())) == 3
    assert list(Member(Field(data, "b")).values()) == []


def test_texts(data):
    data.text_store.entry = {"a": ["b", "c", "d"]}
    assert len(list(Member(Field(data, "a")).texts())) == 3
    assert list(Member(Field(data, "b")).texts()) == []


def test_funcs(data):
    data.func_store.entry = {"a": ["b", "c", "d"]}
    assert len(list(Member(Field(data, "a")).funcs())) == 3
    assert list(Member(Field(data, "b")).funcs()) == []


def test_views(data):
    data.view_store.entry = {"a": ["b", "c", "d"]}
    assert len(list(Member(Field(data, "a")).views())) == 3
    assert list(Member(Field(data, "b")).views()) == []


def test_on_value_entry(data):
    called = 0

    @Member(Field(data, "a")).on_value_entry.connect
    def a(a):
        nonlocal called
        called += 1

    data.signal("value_entry", "a").send()
    assert called == 1


def test_on_text_entry(data):
    called = 0

    @Member(Field(data, "a")).on_text_entry.connect
    def a(a):
        nonlocal called
        called += 1

    data.signal("text_entry", "a").send()
    assert called == 1


def test_on_func_entry(data):
    called = 0

    @Member(Field(data, "a")).on_func_entry.connect
    def a(a):
        nonlocal called
        called += 1

    data.signal("func_entry", "a").send()
    assert called == 1


def test_on_view_entry(data):
    called = 0

    @Member(Field(data, "a")).on_view_entry.connect
    def a(a):
        nonlocal called
        called += 1

    data.signal("view_entry", "a").send()
    assert called == 1


def test_on_sync(data):
    called = 0

    @Member(Field(data, "a")).on_sync.connect
    def a(a):
        nonlocal called
        called += 1

    data.signal("sync", "a").send()
    assert called == 1


def test_sync_time(data):
    t = datetime.datetime.now()
    data.sync_time_store.set_recv(self_name, t)
    assert Member(Field(data, self_name)).sync_time == t


def test_lib_version(data):
    data.member_ids["a"] = 1
    data.member_lib_name[1] = "aaa"
    data.member_lib_ver[1] = "bbb"
    data.member_remote_addr[1] = "ccc"
    a = Member(Field(data, "a"))
    assert a.lib_name == "aaa"
    assert a.lib_version == "bbb"
    assert a.remote_addr == "ccc"


def test_ping_status(data):
    data.member_ids["a"] = 1
    data.ping_status[1] = 10
    a = Member(Field(data, "a"))
    assert a.ping_status == 10
    assert data.ping_status_req is True


def test_on_ping(data):
    called = 0

    @Member(Field(data, "a")).on_ping.connect
    def a(a):
        nonlocal called
        called += 1

    assert data.ping_status_req is True

    data.signal("ping", "a").send()
    assert called == 1
