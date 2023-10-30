from conftest import self_name
from webcface.data import Value
from webcface.field import Field
from webcface.member import Member
import pytest


def test_value_member(data):
    assert isinstance(Value(Field(data, "a", "b")).member, Member)
    assert Value(Field(data, "a", "b")).member.name == "a"


def test_value_name(data):
    assert Value(Field(data, "a", "b")).name == "b"


def test_value_child(data):
    c = Value(Field(data, "a", "b")).child("c")
    assert isinstance(c, Value)
    assert c.member.name == "a"
    assert c.name == "b.c"


def test_value_try_get(data):
    assert Value(Field(data, "a", "b")).try_get() is None
    assert data.value_store.req.get("a", {}).get("b", 0) == 1

    Value(Field(data, self_name, "b")).try_get()
    assert self_name not in data.value_store.req

    data.value_store.data_recv["a"] = {"b": [2, 3, 4]}
    assert Value(Field(data, "a", "b")).try_get() == 2


def test_value_get(data):
    assert Value(Field(data, "a", "b")).get() == 0
    assert data.value_store.req.get("a", {}).get("b", 0) == 1

    Value(Field(data, self_name, "b")).get()
    assert self_name not in data.value_store.req

    data.value_store.data_recv["a"] = {"b": [2, 3, 4]}
    assert Value(Field(data, "a", "b")).get() == 2


def test_value_try_get_vec(data):
    assert Value(Field(data, "a", "b")).try_get_vec() is None
    assert data.value_store.req.get("a", {}).get("b", 0) == 1

    Value(Field(data, self_name, "b")).try_get_vec()
    assert self_name not in data.value_store.req

    data.value_store.data_recv["a"] = {"b": [2, 3, 4]}
    assert Value(Field(data, "a", "b")).try_get_vec() == [2, 3, 4]


def test_value_get_vec(data):
    assert Value(Field(data, "a", "b")).get_vec() == []
    assert data.value_store.req.get("a", {}).get("b", 0) == 1

    Value(Field(data, self_name, "b")).get_vec()
    assert self_name not in data.value_store.req

    data.value_store.data_recv["a"] = {"b": [2, 3, 4]}
    assert Value(Field(data, "a", "b")).get_vec() == [2, 3, 4]


def test_value_set(data):
    Value(Field(data, self_name, "b")).set(5)
    assert data.value_store.data_send.get("b", []) == [5]

    Value(Field(data, self_name, "c")).set([2, 3, 4])
    assert data.value_store.data_send.get("c", []) == [2, 3, 4]

    # objectを渡した時

    called = 0

    def callback(v):
        assert v.member.name == self_name
        assert v.name == "b"
        nonlocal called
        called += 1

    Value(Field(data, self_name, "b")).signal.connect(callback)
    Value(Field(data, self_name, "b")).set(1)
    assert called == 1

    with pytest.raises(ValueError) as e:
        Value(Field(data, "a", "b")).set(123456)
