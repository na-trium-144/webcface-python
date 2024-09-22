from conftest import self_name
import datetime
import pytest
from webcface.log import Log
from webcface.log_handler import LogLine
from webcface.field import Field
from webcface.member import Member


def test_log_member(data):
    assert isinstance(Log(Field(data, "a")).member, Member)
    assert Log(Field(data, "a")).member.name == "a"


def test_log_try_get(data):
    assert Log(Field(data, "a")).try_get() is None
    assert data.log_store.req.get("a", False)

    Log(Field(data, self_name)).try_get()
    assert self_name not in data.log_store.req

    data.log_store.data_recv["a"] = [LogLine(0, datetime.datetime.now(), "")]
    assert len(Log(Field(data, "a")).try_get()) == 1


def test_log_get(data):
    assert Log(Field(data, "a")).get() == []
    assert data.log_store.req.get("a", False)

    Log(Field(data, self_name)).get()
    assert self_name not in data.log_store.req

    data.log_store.data_recv["a"] = [LogLine(0, datetime.datetime.now(), "")]
    assert len(Log(Field(data, "a")).get()) == 1


def test_log_clear(data):
    data.log_store.data_recv["a"] = [LogLine(0, datetime.datetime.now(), "")]
    Log(Field(data, "a")).clear()
    assert len(data.log_store.data_recv["a"]) == 0


def test_log_append(data):
    Log(Field(data, self_name)).append(1, "a")
    assert len(data.log_store.data_recv[self_name]) == 1
    assert data.log_store.data_recv[self_name][0].level == 1
    assert data.log_store.data_recv[self_name][0].message == "a"
