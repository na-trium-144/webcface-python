import threading
import time
from typing import Optional
import json
import websocket
from blinker import signal
import webcface.member
import webcface.field
import webcface.client_data
import webcface.message


class Client(webcface.member.Member):
    connected: bool
    sync_init: bool
    ws: Optional[websocket.WebSocketApp]
    closing: bool
    ws_thread: threading.Thread

    def __init__(
        self, name: str = "", host: str = "127.0.0.1", port: int = 7530
    ) -> None:
        def call_func(
            r: webcface.func_info.AsyncFuncResult,
            target: webcface.field.FieldBase,
            args: list[float | bool | str],
        ) -> None:
            self._send(
                [
                    webcface.message.Call.new(
                        r._caller_id,
                        0,
                        self.data.get_member_id_from_name(target._member),
                        target._field,
                        args,
                    )
                ]
            )

        super().__init__(
            webcface.field.Field(
                webcface.client_data.ClientData(name, call_func), name
            ),
            name,
        )
        self.ws = None
        self.connected = False
        self.sync_init = False
        self.closing = False

        def on_open(ws):
            print("open")
            self.connected = True
            self.sync_init = False

        def on_message(ws, message):
            if len(message) > 0:
                for m in webcface.message.unpack(message):
                    if isinstance(m, webcface.message.SvrVersion):
                        self.data.svr_name = m.svr_name
                        self.data.svr_version = m.ver
                    if isinstance(m, webcface.message.SyncInit):
                        self.data.value_store.add_member(m.member_name)
                        self.data.text_store.add_member(m.member_name)
                        self.data.func_store.add_member(m.member_name)
                        self.data.member_ids[m.member_name] = m.member_id
                        self.data.member_lib_name[m.member_id] = m.lib_name
                        self.data.member_lib_ver[m.member_id] = m.lib_ver
                        self.data.member_remote_addr[m.member_id] = m.addr
                        signal(json.dumps(["memberEntry"])).send(
                            self.member(m.member_name)
                        )
                    if isinstance(m, webcface.message.ValueRes):
                        member, field = self.data.value_store.get_req(
                            m.req_id, m.sub_field
                        )
                        self.data.value_store.set_recv(member, field, m.data)
                        signal(json.dumps(["valueChange", member, field])).send(
                            self.member(member).value(field)
                        )
                    if isinstance(m, webcface.message.ValueEntry):
                        member = self.data.get_member_name_from_id(m.member_id)
                        self.data.value_store.set_entry(member, m.field)
                        signal(json.dumps(["valueEntry", member])).send(
                            self.member(member).value(m.field)
                        )
                    if isinstance(m, webcface.message.TextRes):
                        member, field = self.data.text_store.get_req(
                            m.req_id, m.sub_field
                        )
                        self.data.text_store.set_recv(member, field, m.data)
                        signal(json.dumps(["textChange", member, field])).send(
                            self.member(member).text(field)
                        )
                    if isinstance(m, webcface.message.TextEntry):
                        member = self.data.get_member_name_from_id(m.member_id)
                        self.data.text_store.set_entry(member, m.field)
                        signal(json.dumps(["textEntry", member])).send(
                            self.member(member).text(m.field)
                        )
                    if isinstance(m, webcface.message.ViewRes):
                        member, field = self.data.view_store.get_req(
                            m.req_id, m.sub_field
                        )
                        v_prev = self.data.view_store.get_recv(member, field)
                        if v_prev is None:
                            v_prev = []
                            self.data.view_store.set_recv(member, field, v_prev)
                        for i, c in m.data_diff.items():
                            if i >= len(v_prev):
                                v_prev.append(c)
                            else:
                                v_prev[i] = c
                        if len(v_prev) >= m.length:
                            del v_prev[m.length :]
                        signal(json.dumps(["viewChange", member, field])).send(
                            self.member(member).view(field)
                        )
                    if isinstance(m, webcface.message.ViewEntry):
                        member = self.data.get_member_name_from_id(m.member_id)
                        self.data.view_store.set_entry(member, m.field)
                        signal(json.dumps(["viewEntry", member])).send(
                            self.member(member).view(m.field)
                        )
                    if isinstance(m, webcface.message.FuncInfo):
                        member = self.data.get_member_name_from_id(m.member_id)
                        self.data.func_store.set_entry(member, m.field)
                        self.data.func_store.set_recv(member, m.field, m.func_info)
                        signal(json.dumps(["funcEntry", member])).send(
                            self.member(member).func(m.field)
                        )
                    if isinstance(m, webcface.message.Call):
                        func_info = self.data.func_store.get_recv(
                            self.data.self_member_name, m.field
                        )
                        if func_info is not None:

                            def do_call():
                                self._send(
                                    [
                                        webcface.message.CallResponse(
                                            m.caller_id, m.caller_member_id, True
                                        )
                                    ]
                                )
                                try:
                                    result = func_info.run(m.args)
                                    is_error = False
                                except Exception as e:
                                    is_error = True
                                    result = str(e)
                                self._send(
                                    [
                                        webcface.message.CallResult(
                                            m.caller_id,
                                            m.caller_member_id,
                                            is_error,
                                            result,
                                        )
                                    ]
                                )

                            threading.Thread(target=do_call).start()
                        else:
                            self._send(
                                [
                                    webcface.message.CallResponse(
                                        m.caller_id, m.caller_member_id, True
                                    )
                                ]
                            )
                    if isinstance(m, webcface.message.CallResponse):
                        try:
                            r = self.data.func_result_store.get_result(m.caller_id)
                            with r._cv:
                                r._started = m.started
                                r._started_ready = True
                                if not m.started:
                                    r._result_is_error = True
                                    r._result_ready = True
                                r._cv.notify_all()
                        except IndexError:
                            print(f"error receiving call response id={m.caller_id}")
                    if isinstance(m, webcface.message.CallResult):
                        try:
                            r = self.data.func_result_store.get_result(m.caller_id)
                            with r._cv:
                                r._result_is_error = m.is_error
                                r._result = m.result
                                r._result_ready = True
                                r._cv.notify_all()
                        except IndexError:
                            print(f"error receiving call result id={m.caller_id}")

        def on_error(ws, error):
            print(error)

        def on_close(ws, close_status_code, close_msg):
            print("closed")
            self.connected = False

        def reconnect():
            while not self.closing:
                self.ws = websocket.WebSocketApp(
                    f"ws://{host}:{port}/",
                    on_open=on_open,
                    on_message=on_message,
                    on_error=on_error,
                    on_close=on_close,
                )
                try:
                    self.ws.run_forever()
                except Exception as e:
                    print(f"ws error: {e}")
                    time.sleep(1)

        self.ws_thread = threading.Thread(target=reconnect)
        self.ws_thread.start()

    def __del__(self) -> None:
        self.close()

    def close(self) -> None:
        self.closing = True
        if self.ws is not None:
            self.ws.close()
        self.ws_thread.join()

    def _send(self, msgs: list[webcface.message.MessageBase]) -> None:
        if self.connected and self.ws is not None:
            self.ws.send(webcface.message.pack(msgs))

    def sync(self) -> None:
        if self.connected and self.ws is not None:
            msgs: list[webcface.message.MessageBase] = []
            is_first = False
            if not self.sync_init:
                msgs.append(webcface.message.SyncInit.new(self.name, "python", "1.0.0"))
                self.sync_init = True
                is_first = True

            msgs.append(webcface.message.Sync.new())

            for k, v in self.data.value_store.transfer_send(is_first).items():
                msgs.append(webcface.message.Value.new(k, v))
            for m, r in self.data.value_store.transfer_req(is_first).items():
                for k, i in r.items():
                    msgs.append(webcface.message.ValueReq.new(m, k, i))
            for k, v2 in self.data.text_store.transfer_send(is_first).items():
                msgs.append(webcface.message.Text.new(k, v2))
            for m, r in self.data.text_store.transfer_req(is_first).items():
                for k, i in r.items():
                    msgs.append(webcface.message.TextReq.new(m, k, i))

            view_send_prev = self.data.view_store.get_send_prev(is_first)
            view_send = self.data.view_store.transfer_send(is_first)
            for k, v4 in view_send.items():
                v_prev = view_send_prev.get(k, [])
                v_diff = {}
                for i, c in enumerate(v4):
                    if i >= len(v_prev) or v_prev[i] != c:
                        v_diff[str(i)] = c
                msgs.append(webcface.message.View.new(k, v_diff, len(v4)))
            for m, r in self.data.view_store.transfer_req(is_first).items():
                for k, i in r.items():
                    msgs.append(webcface.message.ViewReq.new(m, k, i))

            for k, v3 in self.data.func_store.transfer_send(is_first).items():
                msgs.append(webcface.message.FuncInfo.new(k, v3))

            self._send(msgs)

    def member(self, member_name) -> webcface.member.Member:
        return webcface.member.Member(self, member_name)

    @property
    def server_name(self) -> str:
        return self.data.svr_name

    @property
    def server_version(self) -> str:
        return self.data.svr_version
