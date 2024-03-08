import threading
import multiprocessing
import time
from typing import Optional, Iterable
import logging
import io
import os
import atexit
import blinker
import websocket
import webcface.member
import webcface.field
import webcface.client_data
import webcface.message
import webcface.client_impl


class Client(webcface.member.Member):
    """サーバーに接続する

    詳細は `Clientのドキュメント <https://na-trium-144.github.io/webcface/md_01__client.html>`_ を参照

    :arg name: 名前
    :arg host: サーバーのアドレス
    :arg port: サーバーのポート
    """

    connected: bool
    _connection_cv: threading.Condition
    _ws: Optional[websocket.WebSocketApp]
    _closing: bool
    _reconnect_thread: threading.Thread
    _send_thread: threading.Thread

    def __init__(
        self, name: str = "", host: str = "127.0.0.1", port: int = 7530
    ) -> None:
        logger = logging.getLogger(f"webcface_internal({name})")
        handler = logging.StreamHandler()
        fmt = logging.Formatter("%(name)s [%(levelname)s] %(message)s")
        handler.setFormatter(fmt)
        logger.addHandler(handler)
        if "WEBCFACE_TRACE" in os.environ:
            logger.setLevel(logging.DEBUG)
        elif "WEBCFACE_VERBOSE" in os.environ:
            logger.setLevel(logging.INFO)
        else:
            logger.setLevel(logging.CRITICAL + 1)

        super().__init__(
            webcface.field.Field(webcface.client_data.ClientData(name, logger), name),
            name,
        )
        self._ws = None
        self.connected = False
        self._connection_cv = threading.Condition()
        self._closing = False

        data = self._data_check()

        def on_open(ws):
            data.logger_internal.info("WebSocket Open")
            with self._connection_cv:
                self.connected = True
                self._connection_cv.notify_all()

        def on_message(ws, message: bytes):
            data.logger_internal.debug("Received message")
            webcface.client_impl.on_recv(self, data, message)

        def on_error(ws, error):
            data.logger_internal.info(f"WebSocket Error: {error}")

        def on_close(ws, close_status_code, close_msg):
            data.logger_internal.info("WebSocket Closed")
            with self._connection_cv:
                self.connected = False
                self._connection_cv.notify_all()
            data.clear_msg()
            data.queue_msg(webcface.client_impl.sync_data_first(self, data))

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
                    self._ws.run_forever()
                except Exception as e:
                    data.logger_internal.debug(f"WebSocket Error: {e}")
                time.sleep(1)

        self._reconnect_thread = threading.Thread(target=reconnect, daemon=True)

        def msg_send():
            data = self._data_check()
            while not self._closing:
                while (not self.connected or not data.has_msg()) and not self._closing:
                    with self._connection_cv:
                        while not self.connected:
                            self._connection_cv.wait()
                    data.wait_msg()
                msgs = self._data_check().pop_msg()
                if msgs is not None and self._ws is not None and self.connected:
                    try:
                        data.logger_internal.debug("Sending message")
                        self._ws.send(webcface.message.pack(msgs))
                    except Exception as e:
                        data.logger_internal.error(f"Error Sending message {e}")

        self._send_thread = threading.Thread(target=msg_send, daemon=True)

        data.queue_msg(webcface.client_impl.sync_data_first(self, data))

        def close_at_exit():
            data.logger_internal.debug(
                "Client close triggered at interpreter termination"
            )
            self.close()
            if self._reconnect_thread.is_alive():
                self._reconnect_thread.join()
            if self._send_thread.is_alive():
                self._send_thread.join()

        atexit.register(close_at_exit)

    def close(self) -> None:
        """接続を切る

        ver1.1.1〜 キューにたまっているデータがすべて送信されるまで待機
        """
        if not self._closing:
            self._data_check().wait_empty()
            self._closing = True
            if self._ws is not None:
                self._ws.close()

    def start(self) -> None:
        """サーバーに接続を開始する"""
        if not self._reconnect_thread.is_alive():
            self._reconnect_thread.start()
        if not self._send_thread.is_alive():
            self._send_thread.start()

    def wait_connection(self) -> None:
        """サーバーに接続が成功するまで待機する。

        接続していない場合、start()を呼び出す。
        """
        self.start()
        with self._connection_cv:
            while not self.connected:
                self._connection_cv.wait()

    def sync(self) -> None:
        """送信用にセットしたデータとリクエストデータをすべて送信キューに入れる。

        実際に送信をするのは別スレッドであり、この関数はブロックしない。

        サーバーに接続していない場合、start()を呼び出す。
        """
        self.start()
        data = self._data_check()
        data.queue_msg(webcface.client_impl.sync_data(self, data, False))

    def member(self, member_name) -> webcface.member.Member:
        """他のメンバーにアクセスする"""
        return webcface.member.Member(self, member_name)

    def members(self) -> Iterable[webcface.member.Member]:
        """サーバーに接続されている他のmemberをすべて取得する。

        自分自身と、無名のmemberを除く。
        """
        return map(self.member, self._data_check().value_store.get_members())

    @property
    def on_member_entry(self) -> blinker.NamedSignal:
        """Memberが追加されたときのイベント

        コールバックの引数にはMemberオブジェクトが渡される。

        * 呼び出したいコールバック関数をfuncとして
        :code:`client.on_member_entry.connect(func)`
        などとすれば関数を登録できる。
        * または :code:`@client.on_member_entry.connect` をデコレーターとして使う。
        """
        return self._data_check().signal("member_entry")

    @property
    def logging_handler(self) -> logging.Handler:
        """webcfaceに出力するloggingのHandler

        :return: logger.addHandler にセットして使う
        """
        return self._data_check().logging_handler

    @property
    def logging_io(self) -> io.TextIOBase:
        """webcfaceとstderrに出力するio"""
        return self._data_check().logging_io

    @property
    def server_name(self) -> str:
        """サーバーの識別情報

        :return: 通常は"webcface"が返る
        """
        return self._data_check().svr_name

    @property
    def server_version(self) -> str:
        """サーバーのバージョン"""
        return self._data_check().svr_version
