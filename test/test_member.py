from conftest import self_name
from webcface.data import Value
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
