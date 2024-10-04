import datetime
import time
import os
import pytest
import toml
from conftest import self_name, check_sent, clear_sent, send_back
from webcface.message import *
from webcface.field import Field
from webcface.func import Func
from webcface.func_info import Arg, ValType, FuncNotFoundError
from webcface.view import ViewComponent
from webcface.log_handler import LogLine, LogData
import webcface.func_info
import webcface.view_components

conf = toml.load(os.path.join(os.path.dirname(__file__), "../pyproject.toml"))


def test_name(wcli):
    assert wcli.name == self_name


def test_sync(wcli):
    wcli.sync()
    m = check_sent(wcli, SyncInit)
    assert isinstance(m, SyncInit)
    assert m.member_name == self_name
    assert m.lib_name == "python"
    assert m.lib_ver == conf["tool"]["poetry"]["version"]
    m = check_sent(wcli, Sync)
    assert isinstance(m, Sync)
    clear_sent(wcli)
    wcli._data_check()._msg_first = True

    wcli.sync()
    assert check_sent(wcli, SyncInit) is None
    m = check_sent(wcli, Sync)
    assert isinstance(m, Sync)


def test_auto_sync(wcli):
    assert wcli._auto_sync is None
    print(wcli.sync)
    wcli.start()
    time.sleep(0.3)
    assert check_sent(wcli, SyncInit) is None
    assert check_sent(wcli, Sync) is None
    clear_sent(wcli)

    wcli._auto_sync = 0.2
    wcli.start()
    time.sleep(0.3)
    m = check_sent(wcli, SyncInit)
    assert isinstance(m, SyncInit)
    assert m.member_name == self_name
    assert m.lib_name == "python"
    assert m.lib_ver == conf["tool"]["poetry"]["version"]
    m = check_sent(wcli, Sync)
    assert isinstance(m, Sync)
    clear_sent(wcli)
    wcli._data_check()._msg_first = True

    time.sleep(0.3)
    wcli.sync = lambda timeout, auto_start: time.sleep(timeout)
    assert check_sent(wcli, SyncInit) is None
    m = check_sent(wcli, Sync)
    assert isinstance(m, Sync)

    wcli.close()
    time.sleep(0.5)
    assert not wcli._sync_thread.is_alive()


def test_server_version(wcli):
    send_back(wcli, [SyncInitEnd.new("a", "1", 10, "b")])
    assert wcli.server_name == "a"
    assert wcli.server_version == "1"
    assert wcli._data_check().self_member_id == 10
    assert wcli._data_check().sync_init_end is True
    assert wcli.server_hostname == "b"


def test_ping(wcli):
    send_back(wcli, [Ping.new()])
    assert check_sent(wcli, Ping)

    called = 0

    def callback(m):
        nonlocal called
        called += 1

    wcli._data_check()._msg_first = True
    wcli.member("a").on_ping(callback)
    assert check_sent(wcli, PingStatusReq)

    send_back(wcli, [SyncInit.new_full("a", 10, "", "", ""), PingStatus.new({10: 15})])
    assert called == 1
    assert wcli.member("a").ping_status == 15


def test_entry(wcli):
    called = 0

    def callback(m):
        nonlocal called
        called += 1

    wcli.on_member_entry(callback)
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

    assert m.value("b").exists() is False
    m.on_value_entry(callback)
    send_back(wcli, [ValueEntry.new(10, "b")])
    assert called == 1
    called = 0
    assert len(list(m.values())) == 1
    assert list(m.values())[0].name == "b"
    assert m.value("b").exists() is True

    assert m.view("b").exists() is False
    m.on_view_entry(callback)
    send_back(wcli, [ViewEntry.new(10, "b")])
    assert called == 1
    called = 0
    assert len(list(m.views())) == 1
    assert list(m.views())[0].name == "b"
    assert m.view("b").exists() is True

    assert m.text("b").exists() is False
    m.on_text_entry(callback)
    send_back(wcli, [TextEntry.new(10, "b")])
    assert called == 1
    called = 0
    assert len(list(m.texts())) == 1
    assert list(m.texts())[0].name == "b"
    assert m.text("b").exists() is True

    assert m.func("b").exists() is False
    m.on_func_entry(callback)
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
    assert m.func("b").exists() is True

    assert m.log("b").exists() is False
    send_back(wcli, [LogEntry.new(10, "b")])
    assert m.log("b").exists() is True

    m.on_sync(callback)
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

    wcli._data_check()._msg_first = True
    wcli.member("a").value("b").on_change(callback)
    m = check_sent(wcli, ValueReq)
    assert isinstance(m, ValueReq)
    assert m.member == "a"
    assert m.field == "b"
    assert m.req_id == 1

    send_back(wcli, [ValueRes.new(1, "", [1, 2, 3]), ValueRes.new(1, "c", [1, 2, 3])])
    assert called == 1
    assert wcli._data_check().value_store.get_recv("a", "b") == [1, 2, 3]
    assert wcli._data_check().value_store.get_recv("a", "b.c") == [1, 2, 3]


def test_text_send(wcli):
    wcli._data_check().text_store.set_send("a", "b")
    wcli.sync()
    m = check_sent(wcli, Text)
    assert isinstance(m, Text)
    assert m.field == "a"
    assert m.data == "b"


def test_text_req(wcli):
    called = 0

    def callback(v):
        nonlocal called
        called += 1

    wcli._data_check()._msg_first = True
    wcli.member("a").text("b").on_change(callback)
    m = check_sent(wcli, TextReq)
    assert isinstance(m, TextReq)
    assert m.member == "a"
    assert m.field == "b"
    assert m.req_id == 1

    send_back(wcli, [TextRes.new(1, "", "z"), TextRes.new(1, "c", "z")])
    assert called == 1
    assert wcli._data_check().text_store.get_recv("a", "b") == "z"
    assert wcli._data_check().text_store.get_recv("a", "b.c") == "z"


def test_view_send(wcli):
    wcli._data_check().view_store.set_send(
        "a",
        [
            webcface.view_components.text(
                "a",
                text_color=webcface.view_components.ViewColor.YELLOW,
                bg_color=webcface.view_components.ViewColor.GREEN,
            ),
            webcface.view_components.new_line(),
            webcface.view_components.button(
                "a", Func(Field(wcli._data_check(), "x", "y"))
            ),
        ],
    )
    wcli.sync()
    m = check_sent(wcli, View)
    assert isinstance(m, View)
    assert m.field == "a"
    assert m.length == 3
    assert len(m.data) == 3
    m_vc = lambda i: ViewComponent.from_base(m.data[str(i)], wcli._data)
    assert m_vc(0).type == webcface.view_components.ViewComponentType.TEXT
    assert m_vc(0).text == "a"
    assert m_vc(0).text_color == webcface.view_components.ViewColor.YELLOW
    assert m_vc(0).bg_color == webcface.view_components.ViewColor.GREEN
    assert m_vc(1).type == webcface.view_components.ViewComponentType.NEW_LINE
    assert m_vc(2).type == webcface.view_components.ViewComponentType.BUTTON
    assert m_vc(2).on_click.member.name == "x"
    assert m_vc(2).on_click.name == "y"
    clear_sent(wcli)
    wcli._data_check()._msg_first = True

    wcli._data_check().view_store.set_send(
        "a",
        [
            webcface.view_components.text(
                "b",
                text_color=webcface.view_components.ViewColor.RED,
                bg_color=webcface.view_components.ViewColor.GREEN,
            ),
            webcface.view_components.new_line(),
            webcface.view_components.button(
                "a", Func(Field(wcli._data_check(), "x", "y"))
            ),
        ],
    )
    wcli.sync()
    m = check_sent(wcli, View)
    assert isinstance(m, View)
    assert m.field == "a"
    assert m.length == 3
    assert len(m.data) == 1
    m_vc = lambda i: ViewComponent.from_base(m.data[str(i)], wcli._data)
    assert m_vc(0).type == webcface.view_components.ViewComponentType.TEXT
    assert m_vc(0).text == "b"
    assert m_vc(0).text_color == webcface.view_components.ViewColor.RED
    assert m_vc(0).bg_color == webcface.view_components.ViewColor.GREEN


def test_view_req(wcli):
    called = 0

    def callback(v):
        nonlocal called
        called += 1

    wcli._data_check()._msg_first = True
    wcli.member("a").view("b").on_change(callback)
    m = check_sent(wcli, ViewReq)
    assert isinstance(m, ViewReq)
    assert m.member == "a"
    assert m.field == "b"
    assert m.req_id == 1

    v = {
        "0": webcface.view_components.text(
            "b",
            text_color=webcface.view_components.ViewColor.YELLOW,
            bg_color=webcface.view_components.ViewColor.GREEN,
        ),
        "1": webcface.view_components.new_line(),
        "2": webcface.view_components.button(
            "a", Func(Field(wcli._data_check(), "x", "y"))
        ),
    }
    send_back(wcli, [ViewRes.new(1, "", v, 3), ViewRes.new(1, "c", v, 3)])
    assert called == 1
    assert len(wcli._data_check().view_store.get_recv("a", "b")) == 3
    assert (
        wcli._data_check().view_store.get_recv("a", "b")[0]._text_color
        == webcface.view_components.ViewColor.YELLOW
    )
    assert len(wcli._data_check().view_store.get_recv("a", "b.c")) == 3

    v2 = {
        "0": webcface.view_components.text(
            "b",
            text_color=webcface.view_components.ViewColor.RED,
            bg_color=webcface.view_components.ViewColor.GREEN,
        ),
    }
    send_back(wcli, [ViewRes.new(1, "", v2, 3)])
    assert called == 2
    assert len(wcli._data_check().view_store.get_recv("a", "b")) == 3
    assert (
        wcli._data_check().view_store.get_recv("a", "b")[0]._text_color
        == webcface.view_components.ViewColor.RED
    )


def test_log_send(wcli):
    ls = LogData()
    ls.data = [
        LogLine(0, datetime.datetime.now(), "a" * 100000),
        LogLine(1, datetime.datetime.now(), "b"),
    ]
    wcli._data_check().log_store.set_send("hoge", ls)
    wcli.sync()
    m = check_sent(wcli, Log)
    assert isinstance(m, Log)
    assert m.field == "hoge"
    assert len(m.log) == 2
    assert m.log[0].level == 0
    assert m.log[0].message == "a" * 100000
    assert m.log[1].level == 1
    assert m.log[1].message == "b"
    assert ls.sent_lines == 2
    clear_sent(wcli)
    wcli._data_check()._msg_first = True

    ls.data.append(LogLine(2, datetime.datetime.now(), "c"))
    wcli._data_check().log_store.set_send("hoge", ls)
    wcli.sync()
    m = check_sent(wcli, Log)
    assert isinstance(m, Log)
    assert m.field == "hoge"
    assert len(m.log) == 1
    assert m.log[0].level == 2
    assert m.log[0].message == "c"
    assert ls.sent_lines == 3


def test_log_req(wcli):
    called = 0

    def callback(l):
        nonlocal called
        called += 1

    wcli._data_check()._msg_first = True
    wcli.member("a").log("b").on_change(callback)
    m = check_sent(wcli, LogReq)
    assert isinstance(m, LogReq)
    assert m.member == "a"
    assert m.field == "b"
    assert m.req_id == 1

    send_back(
        wcli,
        [
            SyncInit.new_full("a", 10, "", "", ""),
            LogRes.new(
                1,
                "",
                [
                    LogLine(0, datetime.datetime.now(), "a" * 100000),
                    LogLine(1, datetime.datetime.now(), "b"),
                ],
            ),
        ],
    )
    assert called == 1
    assert len(wcli._data_check().log_store.get_recv("a", "b").data) == 2
    assert wcli._data_check().log_store.get_recv("a", "b").data[0].level == 0
    assert (
        wcli._data_check().log_store.get_recv("a", "b").data[0].message == "a" * 100000
    )

    send_back(
        wcli,
        [
            LogRes.new(
                1,
                "",
                [
                    LogLine(2, datetime.datetime.now(), "c"),
                ],
            )
        ],
    )
    assert called == 2
    assert len(wcli._data_check().log_store.get_recv("a", "b").data) == 3

    webcface.Log.keep_lines = 2
    send_back(
        wcli,
        [
            LogRes.new(
                1,
                "",
                [
                    LogLine(3, datetime.datetime.now(), "d"),
                ],
            )
        ],
    )
    assert called == 3
    assert len(wcli._data_check().log_store.get_recv("a", "b").data) == 2
    assert wcli._data_check().log_store.get_recv("a", "b").data[0].level == 2
    assert wcli._data_check().log_store.get_recv("a", "b").data[1].level == 3


def test_func_info(wcli):
    f = wcli.func("a").set(
        lambda: 1,
        return_type=ValType.INT,
        args=[Arg("a", type=ValType.INT, init=3)],
    )
    wcli._data_check()._msg_first = True
    wcli.sync()
    m = check_sent(wcli, FuncInfo)
    assert isinstance(m, FuncInfo)
    assert m.field == "a"
    assert m.func_info.return_type == ValType.INT
    assert len(m.func_info.args) == 1
    assert m.func_info.args[0].name == "a"


def test_func_call(wcli):
    send_back(wcli, [SyncInit.new_full("a", 10, "", "", "")])
    r = wcli.member("a").func("b").run_async(1, True, "a")
    m = check_sent(wcli, Call)
    assert isinstance(m, Call)
    assert m.caller_id == 0
    assert m.target_member_id == 10
    assert m.field == "b"
    assert len(m.args) == 3
    assert m.args[0] == 1
    assert m.args[1] is True
    assert m.args[2] == "a"

    send_back(wcli, [CallResponse.new(0, 0, False)])
    assert r.started is False
    with pytest.raises(FuncNotFoundError) as e:
        res = r.result
    clear_sent(wcli)

    # 2nd call
    r = wcli.member("a").func("b").run_async(1, True, "a")
    m = check_sent(wcli, Call)
    assert isinstance(m, Call)
    assert m.caller_id == 1
    assert m.target_member_id == 10
    assert m.field == "b"

    send_back(wcli, [CallResponse.new(1, 0, True)])
    assert r.started is True

    send_back(wcli, [CallResult.new(1, 0, True, "a")])
    with pytest.raises(RuntimeError) as e:
        res = r.result
    try:
        res = r.result
    except RuntimeError as e:
        assert str(e) == "a"
    clear_sent(wcli)

    # 3rd call
    r = wcli.member("a").func("b").run_async(1, True, "a")
    m = check_sent(wcli, Call)
    assert isinstance(m, Call)
    assert m.caller_id == 2
    assert m.target_member_id == 10
    assert m.field == "b"

    send_back(wcli, [CallResponse.new(2, 0, True)])
    assert r.started is True

    send_back(wcli, [CallResult.new(2, 0, False, "b")])
    assert r.result == "b"


def test_func_response(wcli):
    @wcli.func("a")
    def hoge(a):
        if a == 0:
            raise ValueError("a==0")
        else:
            return a

    send_back(wcli, [Call.new(7, 100, 0, "n", [])])
    time.sleep(0.01)
    m = check_sent(wcli, CallResponse)
    assert isinstance(m, CallResponse)
    assert m.caller_id == 7
    assert m.caller_member_id == 100
    assert m.started is False
    clear_sent(wcli)

    send_back(wcli, [Call.new(8, 100, 0, "a", [1, "zzz"])])
    time.sleep(0.01)
    m = check_sent(wcli, CallResponse)
    assert isinstance(m, CallResponse)
    assert m.caller_id == 8
    assert m.caller_member_id == 100
    assert m.started is True
    m = check_sent(wcli, CallResult)
    assert isinstance(m, CallResult)
    assert m.caller_id == 8
    assert m.caller_member_id == 100
    assert m.is_error is True
    assert m.result == "requires 1 arguments but got 2"
    clear_sent(wcli)

    send_back(wcli, [Call.new(9, 100, 0, "a", [0])])
    time.sleep(0.01)
    m = check_sent(wcli, CallResponse)
    assert isinstance(m, CallResponse)
    assert m.caller_id == 9
    assert m.caller_member_id == 100
    assert m.started is True
    m = check_sent(wcli, CallResult)
    assert isinstance(m, CallResult)
    assert m.caller_id == 9
    assert m.caller_member_id == 100
    assert m.is_error is True
    assert m.result == "a==0"
    clear_sent(wcli)

    send_back(wcli, [Call.new(10, 100, 0, "a", [123])])
    time.sleep(0.01)
    m = check_sent(wcli, CallResponse)
    assert isinstance(m, CallResponse)
    assert m.caller_id == 10
    assert m.caller_member_id == 100
    assert m.started is True
    m = check_sent(wcli, CallResult)
    assert isinstance(m, CallResult)
    assert m.caller_id == 10
    assert m.caller_member_id == 100
    assert m.is_error is False
    assert m.result == 123
    clear_sent(wcli)
