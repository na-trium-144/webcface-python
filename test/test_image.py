from conftest import self_name
import datetime
import pytest
import numpy as np
from webcface.image import Image
from webcface.image_frame import ImageFrame, ImageColorMode, ImageCompressMode
from webcface.field import Field
from webcface.member import Member


def test_image_member(data):
    assert isinstance(Image(Field(data, "a", "b")).member, Member)
    assert Image(Field(data, "a", "b")).member.name == "a"


def test_image_name(data):
    assert Image(Field(data, "a", "b")).name == "b"


def test_image_child(data):
    c = Image(Field(data, "a", "b")).child("c")
    assert isinstance(c, Image)
    assert c.member.name == "a"
    assert c.name == "b.c"


def test_image_try_get(data):
    assert Image(Field(data, "a", "b")).try_get() is None
    assert data.image_store.req.get("a", {}).get("b", 0) == 1

    Image(Field(data, self_name, "b")).try_get()
    assert self_name not in data.image_store.req

    data.image_store.data_recv["a"] = {
        "b": ImageFrame(5, 5, b"\0" * 75, ImageColorMode.RGB, ImageCompressMode.RAW)
    }
    assert Image(Field(data, "a", "b")).try_get().data == b"\0" * 75


def test_image_get(data):
    assert Image(Field(data, "a", "b")).get().data == b""
    assert data.image_store.req.get("a", {}).get("b", 0) == 1

    Image(Field(data, self_name, "b")).get()
    assert self_name not in data.image_store.req

    data.image_store.data_recv["a"] = {
        "b": ImageFrame(5, 5, b"\0" * 75, ImageColorMode.RGB, ImageCompressMode.RAW)
    }
    assert Image(Field(data, "a", "b")).get().data == b"\0" * 75
    assert Image(Field(data, "a", "b")).get().numpy().shape == (5, 5, 3)


def test_image_set(data):
    Image(Field(data, self_name, "b")).set(
        ImageFrame(5, 5, b"\0" * 75, ImageColorMode.RGB, ImageCompressMode.RAW)
    )
    assert data.image_store.data_send.get("b", "").data == b"\0" * 75

    data.image_store.data_send = {}
    # Image(Field(data, self_name, "b")).set(ImageFrame(5, 5, b"\0"*75, ImageColorMode.RGB, ImageCompressMode.RAW))
    # assert "b" not in data.image_store.data_send  # 同じデータを2度送らない

    Image(Field(data, self_name, "b")).set(
        ImageFrame.from_numpy(np.ones((5, 5, 3), dtype=np.uint8), ImageColorMode.RGB)
    )
    assert data.image_store.data_send.get("b", "").data == b"\1" * 75

    called = 0

    def callback(v):
        assert v.member.name == self_name
        assert v.name == "b"
        nonlocal called
        called += 1

    Image(Field(data, self_name, "b")).on_change(callback)
    Image(Field(data, self_name, "b")).set(
        ImageFrame(5, 5, b"\0" * 75, ImageColorMode.RGB, ImageCompressMode.RAW)
    )
    assert called == 1

    with pytest.raises(ValueError) as e:
        Image(Field(data, "a", "b")).set(
            ImageFrame(5, 5, b"\0" * 75, ImageColorMode.RGB, ImageCompressMode.RAW)
        )
