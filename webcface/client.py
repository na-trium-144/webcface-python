import threading
import time
from typing import Optional, Iterable
import logging
import blinker
import websocket
import webcface.member
import webcface.field
import webcface.client_data
import webcface.message


class Client(webcface.member.Member):
    """サーバーに接続する

    詳細は `Clientのドキュメント <https://na-trium-144.github.io/webcface/md_01__client.html>`_ を参照

    :arg name: 名前
    :arg host: サーバーのアドレス
    :arg port: サーバーのポート
    """

    connected: bool
    _sync_init: bool
    _ws: Optional[websocket.WebSocketApp]
    _closing: bool

    def __init__(
        self, name: str = "", host: str = "127.0.0.1", port: int = 7530
    ) -> None:
        super().__init__(
            webcface.field.Field(webcface.client_data.ClientData(name), name),
            name,
        )
        self._ws = None
        self.connected = False
        self._sync_init = False
        self._closing = False

        def on_open(ws):
            print("open")
            self.connected = True
            self._sync_init = False

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
                        self.data.signal("member_entry").send(
                            self.member(m.member_name)
                        )
                    if isinstance(m, webcface.message.ValueRes):
                        member, field = self.data.value_store.get_req(
                            m.req_id, m.sub_field
                        )
                        self.data.value_store.set_recv(member, field, m.data)
                        self.data.signal("value_change", member, field).send(
                            self.member(member).value(field)
                        )
                    if isinstance(m, webcface.message.ValueEntry):
                        member = self.data.get_member_name_from_id(m.member_id)
                        self.data.value_store.set_entry(member, m.field)
                        self.data.signal("value_entry", member).send(
                            self.member(member).value(m.field)
                        )
                    if isinstance(m, webcface.message.TextRes):
                        member, field = self.data.text_store.get_req(
                            m.req_id, m.sub_field
                        )
                        self.data.text_store.set_recv(member, field, m.data)
                        self.data.signal("text_change", member, field).send(
                            self.member(member).text(field)
                        )
                    if isinstance(m, webcface.message.TextEntry):
                        member = self.data.get_member_name_from_id(m.member_id)
                        self.data.text_store.set_entry(member, m.field)
                        self.data.signal("text_entry", member).send(
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
                        self.data.signal("view_change", member, field).send(
                            self.member(member).view(field)
                        )
                    if isinstance(m, webcface.message.ViewEntry):
                        member = self.data.get_member_name_from_id(m.member_id)
                        self.data.view_store.set_entry(member, m.field)
                        self.data.signal("view_entry", member).send(
                            self.member(member).view(m.field)
                        )
                    if isinstance(m, webcface.message.FuncInfo):
                        member = self.data.get_member_name_from_id(m.member_id)
                        self.data.func_store.set_entry(member, m.field)
                        self.data.func_store.set_recv(member, m.field, m.func_info)
                        self.data.signal("func_entry", member).send(
                            self.member(member).func(m.field)
                        )
                    if isinstance(m, webcface.message.Call):
                        func_info = self.data.func_store.get_recv(
                            self.data.self_member_name, m.field
                        )
                        if func_info is not None:

                            def do_call():
                                self.data.queue_msg(
                                    [
                                        webcface.message.CallResponse.new(
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
                                self.data.queue_msg(
                                    [
                                        webcface.message.CallResult.new(
                                            m.caller_id,
                                            m.caller_member_id,
                                            is_error,
                                            result,
                                        )
                                    ]
                                )

                            threading.Thread(target=do_call).start()
                        else:
                            self.data.queue_msg(
                                [
                                    webcface.message.CallResponse.new(
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
                    if isinstance(m, webcface.message.Log):
                        member = self.data.get_member_name_from_id(m.member_id)
                        log_s = self.data.log_store.get_recv(member)
                        if log_s is None:
                            log_s = []
                            self.data.log_store.set_recv(member, log_s)
                        log_s.extend(m.log)
                        self.data.signal("log_append", member).send(
                            self.member(member).log()
                        )

        def on_error(ws, error):
            print(error)

        def on_close(ws, close_status_code, close_msg):
            print("closed")
            self.connected = False

        def reconnect():
            while not self._closing:
                self._ws = websocket.WebSocketApp(
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

        threading.Thread(target=reconnect, daemon=True).start()

        def msg_send():
            while not self._closing:
                msgs = self.data.pop_msg()
                if self.connected and self._ws is not None:
                    self._ws.send(webcface.message.pack(msgs))

        threading.Thread(target=msg_send, daemon=True).start()

    def __del__(self) -> None:
        self.close()

    def close(self) -> None:
        """接続を切る"""
        self._closing = True
        if self._ws is not None:
            self._ws.close()

    def sync(self) -> None:
        """送信用にセットしたデータとリクエストデータをすべて送信キューに入れる。

        実際に送信をするのは別スレッドであり、この関数はブロックしない。

        * 他memberの情報を取得できるのは初回のsync()の後のみ。
        * 他memberの関数の呼び出しと結果の受信はsync()とは非同期に行われる。
        * clientを使用する時は必ずsendを適当なタイミングで繰り返し呼ぶこと。
        """
        if self.connected and self._ws is not None:
            msgs: list[webcface.message.MessageBase] = []
            is_first = False
            if not self._sync_init:
                msgs.append(webcface.message.SyncInit.new(self.name, "python", "1.0.0"))
                self._sync_init = True
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
                if not v3.hidden:
                    msgs.append(webcface.message.FuncInfo.new(k, v3))

            log_send = []
            if is_first:
                log_all = self.data.log_store.get_recv(self.data.self_member_name)
                if log_all is not None:
                    log_send.extend(log_all)
            else:
                new_logs = self.data.log_handler._send_queue
                log_send.extend(new_logs)
            self.data.log_handler._send_queue = []

            if len(log_send) > 0:
                msgs.append(webcface.message.Log.new(log_send))
            for m, r2 in self.data.log_store.transfer_req(is_first).items():
                msgs.append(webcface.message.LogReq.new(m))

            self.data.queue_msg(msgs)

    def member(self, member_name) -> webcface.member.Member:
        """他のメンバーにアクセスする"""
        return webcface.member.Member(self, member_name)

    def members(self) -> Iterable[webcface.member.Member]:
        """サーバーに接続されている他のmemberをすべて取得する。

        自分自身と、無名のmemberを除く。
        """
        return map(self.member, self.data.value_store.get_members())

    @property
    def on_member_entry(self) -> blinker.NamedSignal:
        """Memberが追加されたときのイベント

        コールバックの引数にはMemberオブジェクトが渡される。

        * 呼び出したいコールバック関数をfuncとして
        :code:`client.on_member_entry.connect(func)`
        などとすれば関数を登録できる。
        * または :code:`@client.on_member_entry.connect` をデコレーターとして使う。
        """
        return self.data.signal("member_entry")

    @property
    def logging_handler(self) -> logging.Handler:
        """webcfaceに出力するloggingのHandler

        :return: logger.addHandler にセットして使う
        """
        return self.data.log_handler

    @property
    def server_name(self) -> str:
        """サーバーの識別情報

        :return: 通常は"webcface"が返る
        """
        return self.data.svr_name

    @property
    def server_version(self) -> str:
        """サーバーのバージョン"""
        return self.data.svr_version
