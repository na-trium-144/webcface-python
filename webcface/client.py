import threading
import time
import websocket
import webcface.member
import webcface.field
import webcface.client_data
import webcface.message


class Client(webcface.member.Member):
    connected: bool
    sync_init: bool
    ws: websocket.WebSocketApp | None
    closing: bool
    ws_thread: threading.Thread

    def __init__(
        self, name: str = "", host: str = "127.0.0.1", port: int = 7530
    ) -> None:
        super().__init__(
            webcface.field.Field(webcface.client_data.ClientData(name), name), name
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
                    if isinstance(m, webcface.message.ValueRes):
                        member, field = self.data.value_store.get_req(
                            m.req_id, m.sub_field
                        )
                        self.data.value_store.set_recv(member, field, m.data)
                    if isinstance(m, webcface.message.ValueEntry):
                        member = self.data.get_member_name_from_id(m.member_id)
                        self.data.value_store.set_entry(member, m.field)

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
                    print(e)
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

            self.ws.send(webcface.message.pack(msgs))

    def member(self, member_name) -> webcface.member.Member:
        return webcface.member.Member(self, member_name)

    @property
    def server_name(self) -> str:
        return self.data.svr_name

    @property
    def server_version(self) -> str:
        return self.data.svr_version
