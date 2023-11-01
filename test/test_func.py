from conftest import self_name
import pytest
from webcface.func import Func
from webcface.func_info import (
    Arg,
    FuncInfo,
    ValType,
    FuncNotFoundError,
    AsyncFuncResult,
)
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

    with pytest.raises(ValueError) as e:
        Func(Field(data, "a", "b")).set(lambda: 1)


def test_func_run(data):
    called = 0

    def f1(a: int, b: float, c: str, d: bool) -> float:
        assert a == 123
        assert b == 123.45
        assert c == "a"
        assert d == True
        nonlocal called
        called += 1
        return 123.45

    ret = Func(Field(data, self_name, "a")).set(f1).run(123, 123.45, "a", True)
    assert called == 1
    assert ret == 123.45

    called = 0
    ret = Func(Field(data, self_name, "a")).run_async(123, 123.45, "a", True)
    assert ret.started
    assert ret.result == 123.45
    assert ret.member.name == self_name
    assert ret.name == "a"
    assert called == 1

    with pytest.raises(TypeError) as e:
        Func(Field(data, self_name, "a")).run()
    ret = Func(Field(data, self_name, "a")).run_async()
    assert ret.started
    with pytest.raises(RuntimeError) as e:
        ret.result

    with pytest.raises(FuncNotFoundError) as e:
        Func(Field(data, self_name, "b")).run()
    ret = Func(Field(data, self_name, "b")).run_async()
    assert not ret.started
    with pytest.raises(FuncNotFoundError) as e:
        ret.result
