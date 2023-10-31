from conftest import self_name
from webcface.data import Value, Text
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
