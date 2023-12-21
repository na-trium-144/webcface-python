from conftest import self_name
import datetime
import pytest
from webcface.value import Value
from webcface.text import Text
from webcface.log import Log
from webcface.field import Field
from webcface.member import Member
from webcface.log_handler import LogLine


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
    assert data.value_store.data_send.get("b", []) == [5.0]

    Value(Field(data, self_name, "b")).set(True)
    assert data.value_store.data_send.get("b", []) == [1.0]

    Value(Field(data, self_name, "c")).set([2, 3, 4])
    assert data.value_store.data_send.get("c", []) == [2.0, 3.0, 4.0]

    Value(Field(data, self_name, "b")).set(5.2)
    assert data.value_store.data_send.get("b", []) == [5.2]

    Value(Field(data, self_name, "c")).set([2.5, 3.5, 4])
    assert data.value_store.data_send.get("c", []) == [2.5, 3.5, 4.0]

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


def test_text_member(data):
    assert isinstance(Text(Field(data, "a", "b")).member, Member)
    assert Text(Field(data, "a", "b")).member.name == "a"


def test_text_name(data):
    assert Text(Field(data, "a", "b")).name == "b"


def test_text_child(data):
    c = Text(Field(data, "a", "b")).child("c")
    assert isinstance(c, Text)
    assert c.member.name == "a"
    assert c.name == "b.c"


def text_text_try_get(data):
    assert Text(Field(data, "a", "b")).try_get() is None
    assert data.text_store.req.get("a", {}).get("b", 0) == 1

    Text(Field(data, self_name, "b")).try_get()
    assert self_name not in data.text_store.req

    data.text_store.data_recv["a"] = {"b": "c"}
    assert Text(Field(data, "a", "b")).try_get() == "c"


def test_text_get(data):
    assert Text(Field(data, "a", "b")).get() == ""
    assert data.text_store.req.get("a", {}).get("b", 0) == 1

    Text(Field(data, self_name, "b")).get()
    assert self_name not in data.text_store.req

    data.text_store.data_recv["a"] = {"b": "c"}
    assert Text(Field(data, "a", "b")).get() == "c"


def test_text_set(data):
    Text(Field(data, self_name, "b")).set("c")
    assert data.text_store.data_send.get("b", "") == "c"

    # objectを渡した時

    called = 0

    def callback(v):
        assert v.member.name == self_name
        assert v.name == "b"
        nonlocal called
        called += 1

    Text(Field(data, self_name, "b")).signal.connect(callback)
    Text(Field(data, self_name, "b")).set("c")
    assert called == 1

    with pytest.raises(ValueError) as e:
        Text(Field(data, "a", "b")).set("abc")


def test_log_member(data):
    assert isinstance(Log(Field(data, "a")).member, Member)
    assert Log(Field(data, "a")).member.name == "a"


def text_log_try_get(data):
    assert Log(Field(data, "a")).try_get() is None
    assert data.log_store.req.get("a", False) is True

    Log(Field(data, self_name)).try_get()
    assert self_name not in data.log_store.req

    data.log_store.data_recv["a"] = [LogLine(1, datetime.datetime.now(), "a")]
    assert len(Log(Field(data, "a")).try_get()) == 1
    assert Log(Field(data, "a")).try_get()[0].level == 1
    assert Log(Field(data, "a")).try_get()[0].message == "a"


def test_log_get(data):
    assert Log(Field(data, "a")).get() == []
    assert data.log_store.req.get("a", False) is True

    Log(Field(data, self_name)).get()
    assert self_name not in data.log_store.req

    data.log_store.data_recv["a"] = [LogLine(1, datetime.datetime.now(), "a")]
    assert len(Log(Field(data, "a")).get()) == 1
    assert Log(Field(data, "a")).get()[0].level == 1
    assert Log(Field(data, "a")).get()[0].message == "a"


def test_log_clear(data):
    data.log_store.data_recv["a"] = [LogLine(1, datetime.datetime.now(), "a")]
    Log(Field(data, "a")).clear()
    assert data.log_store.data_recv["a"] == []
