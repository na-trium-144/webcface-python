from conftest import self_name, check_sent, clear_sent, send_back
from webcface.message import *
import webcface.func_info


def test_name(wcli):
    assert wcli.name == self_name


def test_sync(wcli):
    wcli.sync()
    m = check_sent(wcli, SyncInit)
    assert isinstance(m, SyncInit)
    assert m.member_name == self_name
    assert m.lib_name == "python"
    assert m.lib_ver == "1.0.0"
    m = check_sent(wcli, Sync)
    assert isinstance(m, Sync)
    clear_sent(wcli)

    wcli.sync()
    assert check_sent(wcli, SyncInit) is None
    m = check_sent(wcli, Sync)
    assert isinstance(m, Sync)


def test_server_version(wcli):
    send_back(wcli, [SvrVersion.new("a", "1")])
    assert wcli.server_name == "a"
    assert wcli.server_version == "1"


def test_ping(wcli):
    send_back(wcli, [Ping.new()])
    assert check_sent(wcli, Ping)

    called = 0

    def callback(m):
        nonlocal called
        called += 1

    wcli.member("a").on_ping.connect(callback)
    assert check_sent(wcli, PingStatusReq)

    send_back(wcli, [SyncInit.new_full("a", 10, "", "", ""), PingStatus.new({10: 15})])
    assert called == 1
    assert wcli.member("a").ping_status == 15


def test_entry(wcli):
    called = 0

    def callback(m):
        nonlocal called
        called += 1

    wcli.on_member_entry.connect(callback)
    send_back(wcli, [SyncInit.new_full("a", 10, "b", "1", "12345")])
    assert called == 1
    called = 0
    assert len(list(wcli.members())) == 1
    assert list(wcli.members())[0].name == "a"
    assert wcli._data_check().member_ids["a"] == 10

    m = wcli.member("a")
    assert m.lib_name == "b"
    assert m.lib_version == "1"
    assert m.remote_addr == "12345"

    m.on_value_entry.connect(callback)
    send_back(wcli, [ValueEntry.new(10, "b")])
    assert called == 1
    called = 0
    assert len(list(m.values())) == 1
    assert list(m.values())[0].name == "b"

    m.on_view_entry.connect(callback)
    send_back(wcli, [ViewEntry.new(10, "b")])
    assert called == 1
    called = 0
    assert len(list(m.views())) == 1
    assert list(m.views())[0].name == "b"

    m.on_text_entry.connect(callback)
    send_back(wcli, [TextEntry.new(10, "b")])
    assert called == 1
    called = 0
    assert len(list(m.texts())) == 1
    assert list(m.texts())[0].name == "b"

    m.on_func_entry.connect(callback)
    send_back(
        wcli,
        [
            FuncInfo.new_full(
                10,
                "b",
                webcface.func_info.FuncInfo(
                    None,
                    webcface.func_info.ValType.INT,
                    [webcface.func_info.Arg()],
                    False,
                ),
            )
        ],
    )
    assert called == 1
    called = 0
    assert len(list(m.funcs())) == 1
    assert list(m.funcs())[0].name == "b"
    assert m.func("b").return_type == webcface.func_info.ValType.INT
    assert len(m.func("b").args) == 1

    m.on_sync.connect(callback)
    send_back(wcli, [Sync.new_full(10, 0)])
    assert called == 1
    called = 0


def test_value_send(wcli):
    wcli._data_check().value_store.set_send("a", [5])
    wcli.sync()
    m = check_sent(wcli, Value)
    assert isinstance(m, Value)
    assert m.field == "a"
    assert m.data == [5]


def test_value_req(wcli):
    called = 0

    def callback(v):
        nonlocal called
        called += 1

    wcli.member("a").value("b").signal.connect(callback)
    m = check_sent(wcli, ValueReq)
    assert isinstance(m, ValueReq)
    assert m.member == "a"
    assert m.field == "b"
    assert m.req_id == 1

    send_back(wcli, [ValueRes.new(1, "", [1, 2, 3]), ValueRes.new(1, "c", [1, 2, 3])])
    assert called == 1
    assert wcli._data_check().value_store.get_recv("a", "b") == [1, 2, 3]
    assert wcli._data_check().value_store.get_recv("a", "b.c") == [1, 2, 3]
