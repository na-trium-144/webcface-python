from conftest import self_name


def test_s2_self(s2):
    assert s2.is_self(self_name)
    assert not s2.is_self("a")
    assert not s2.is_self("")


def test_s2_set_send(s2):
    s2.set_send("a", "b")
    assert s2.data_send["a"] == "b"
    assert s2.data_recv[self_name]["a"] == "b"


def test_s2_set_recv(s2):
    s2.set_recv("a", "b", "c")
    assert s2.data_recv["a"]["b"] == "c"


def test_s2_get_recv(s2):
    s2.data_recv["a"] = {"b": "c"}
    assert s2.get_recv("a", "b") == "c"
    assert s2.req["a"]["b"] == 1
    assert s2.req_send["a"]["b"] == 1

    s2.get_recv(self_name, "b")
    assert self_name not in s2.req
    assert self_name not in s2.req_send


def test_s2_unset_recv(s2):
    s2.data_recv["a"] = {"b": "c"}
    s2.req["a"] = {"b": 1}
    s2.req_send["a"] = {"b": 1}
    s2.unset_recv("a", "b")
    assert "b" not in s2.data_recv["a"]
    assert s2.req["a"]["b"] == 0
    assert s2.req_send["a"]["b"] == 0


def test_s2_add_member(s2):
    s2.add_member("a")
    assert s2.entry["a"] == []


def test_s2_set_entry(s2):
    s2.set_entry("a", "b")
    assert s2.entry["a"] == ["b"]


def test_s2_get_members(s2):
    s2.entry = {"a": [], "b": []}
    assert s2.get_members() == ["a", "b"]


def test_s2_get_entry(s2):
    s2.entry["a"] = ["a", "b", "c"]
    assert s2.get_entry("a") == ["a", "b", "c"]


def test_s2_transfer_send(s2):
    s2.data_send["a"] = "a"
    s2.data_recv[self_name] = {"a": "a", "b": "b"}

    s = s2.transfer_send(False)
    assert s["a"] == "a"
    assert "b" not in s

    s = s2.transfer_send(False)
    assert len(s) == 0

    s = s2.transfer_send(True)
    assert s["a"] == "a"
    assert s["b"] == "b"


def test_s2_get_send_prev(s2):
    s2.data_send["a"] = "a"
    s2.data_recv[self_name] = {"a": "a", "b": "b"}

    s2.transfer_send(False)
    s = s2.get_send_prev(False)
    assert s["a"] == "a"
    assert "b" not in s

    s = s2.get_send_prev(True)
    assert len(s) == 0


def test_s2_transfer_req(s2):
    s2.req_send["a"] = {"b": 1}
    s2.req["a"] = {"b": 1, "c": 2}

    s = s2.transfer_req(False)
    assert s["a"]["b"] == 1
    assert "c" not in s["a"]

    s = s2.transfer_req(False)
    assert len(s) == 0

    s = s2.transfer_req(True)
    assert s["a"]["b"] == 1
    assert s["a"]["c"] == 2


def test_s2_get_req(s2):
    s2.req["a"] = {"b": 1, "c": 2}
    assert s2.get_req(1, "") == ("a", "b")
    assert s2.get_req(1, "c") == ("a", "b.c")
    assert s2.get_req(999, "") == ("", "")


def test_s1_self(s1):
    assert s1.is_self(self_name)
    assert not s1.is_self("a")
    assert not s1.is_self("")


def test_s1_set_recv(s1):
    s1.set_recv("a", "b")
    assert s1.data_recv["a"] == "b"


def test_s1_get_recv(s1):
    s1.data_recv["a"] = "b"
    assert s1.get_recv("a") == "b"
    assert s1.req["a"] == True
    assert s1.req_send["a"] == True

    s1.get_recv(self_name)
    assert self_name not in s1.req
    assert self_name not in s1.req_send


def test_s1_transfre_req(s1):
    s1.req_send = {"a": True}
    s1.req = {"a": True, "b": True}

    s = s1.transfer_req(False)
    assert s["a"] == True
    assert "b" not in s

    s = s1.transfer_req(False)
    assert len(s) == 0

    s = s1.transfer_req(True)
    assert s["a"] == True
    assert s["b"] == True


def test_is_self(data):
    assert data.is_self(self_name)
    assert not data.is_self("a")
    assert not data.is_self("")


def test_get_member(data):
    data.member_ids["a"] = 10
    assert data.get_member_name_from_id(10) == "a"
    assert data.get_member_name_from_id(999) == ""
    assert data.get_member_id_from_name("a") == 10
    assert data.get_member_id_from_name("b") == 0
    assert data.get_member_id_from_name("") == 0
