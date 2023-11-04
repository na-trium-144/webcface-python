from conftest import self_name
from webcface.data import Value, Text
from webcface.func import Func, AnonymousFunc
from webcface.func_info import ValType, Arg
from webcface.field import Field
from webcface.member import Member
import pytest


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
