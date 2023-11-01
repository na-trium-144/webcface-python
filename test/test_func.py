from conftest import self_name
import pytest
from webcface.func import Func
from webcface.func_info import Arg, FuncInfo, ValType
from webcface.field import Field
from webcface.member import Member


def test_func_member(data):
    assert isinstance(Func(Field(data, "a", "b")).member, Member)
    assert Func(Field(data, "a", "b")).member.name == "a"


def test_func_name(data):
    assert Func(Field(data, "a", "b")).name == "b"


def test_func_set(data):
    def f1() -> None:  # Noneでもアノテーション必要
        pass

    def f2(a: int, b: float, c: bool, d: str = "d") -> int:
        return 0

    f = Func(Field(data, self_name, "a"))
    f.set(f1)
    assert data.func_store.get_recv(self_name, "a").return_type == ValType.NONE
    assert f.return_type == ValType.NONE
    assert Func(Field(data, self_name, "a")).return_type == ValType.NONE
    assert len(data.func_store.get_recv(self_name, "a").args) == 0
    assert len(f.args) == 0
    assert len(Func(Field(data, self_name, "a")).args) == 0

    f = Func(Field(data, self_name, "b"))
    f.set(f2)
    assert f.return_type == ValType.INT
    assert len(f.args) == 4
    assert f.args[0].type == ValType.INT
    assert f.args[1].type == ValType.FLOAT
    assert f.args[2].type == ValType.BOOL
    assert f.args[2].init is None
    assert f.args[3].type == ValType.STR
    assert f.args[3].init == "d"

    f = Func(Field(data, self_name, "c"))
    f.set(
        lambda x: x + 0.5,
        args=[Arg(name="aaaa", type=int), Arg("b")],
        return_type=float,
    )
    assert len(f.args) == 2
    assert f.args[0].name == "aaaa"
    assert f.args[0].type == ValType.INT
    assert f.args[1].name == "b"
    assert f.args[1].type == ValType.NONE
    assert f.return_type == ValType.FLOAT
