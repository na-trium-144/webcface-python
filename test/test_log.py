from conftest import self_name
import datetime
import pytest
from webcface.log import Log
from webcface.log_handler import LogLine, LogData
from webcface.field import Field
from webcface.member import Member


def test_log_member(data):
    assert isinstance(Log(Field(data, "a"), "b").member, Member)
    assert Log(Field(data, "a"), "b").member.name == "a"


def test_log_try_get(data):
    assert Log(Field(data, "a"), "b").try_get() is None
    assert data.log_store.req.get("a", {}).get("b")

    Log(Field(data, self_name), "b").try_get()
    assert self_name not in data.log_store.req

    log_data = LogData()
    log_data.data = [LogLine(1, datetime.datetime.now(), "a")]
    data.log_store.data_recv["a"] = {"b": log_data}
    assert len(Log(Field(data, "a"), "b").try_get()) == 1


def test_log_get(data):
    assert Log(Field(data, "a"), "b").get() == []
    assert data.log_store.req.get("a", {}).get("b")

    Log(Field(data, self_name), "b").get()
    assert self_name not in data.log_store.req

    log_data = LogData()
    log_data.data = [LogLine(1, datetime.datetime.now(), "a")]
    data.log_store.data_recv["a"] = {"b": log_data}
    assert len(Log(Field(data, "a"), "b").get()) == 1


def test_log_clear(data):
    log_data = LogData()
    log_data.data = [LogLine(1, datetime.datetime.now(), "a")]
    data.log_store.data_recv["a"] = {"b": log_data}
    Log(Field(data, "a"), "b").clear()
    assert len(data.log_store.data_recv["a"]["b"].data) == 0


def test_log_append(data):
    Log(Field(data, self_name), "b").append(1, "a")
    assert len(data.log_store.data_recv[self_name]["b"].data) == 1
    assert data.log_store.data_recv[self_name]["b"].data[0].level == 1
    assert data.log_store.data_recv[self_name]["b"].data[0].message == "a"
