import threading
import multiprocessing
import time
from typing import Optional, Iterable, Callable
import logging
import io
import os
import atexit
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
    :arg auto_reconnect: (ver2.0〜) 通信が切断された時に自動で再接続する。(デフォルト: True)
    :arg auto_sync: (ver2.1〜) 指定した間隔(秒)ごとに別スレッドで自動的に sync() をする (デフォルト: None (syncしない))
    """

    _ws: Optional[websocket.WebSocketApp]
    _closing: bool
    _reconnect_thread: threading.Thread
    _send_thread: threading.Thread
    _auto_sync: Optional[float]
    _sync_thread: Optional[threading.Thread]

    def __init__(
        self,
        name: str = "",
        host: str = "127.0.0.1",
        port: int = 7530,
        auto_reconnect: bool = True,
        auto_sync: Optional[float] = None,
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
            webcface.field.Field(
                webcface.client_data.ClientData(name, logger, auto_reconnect), name
            ),
            name,
        )
        self._ws = None
        self._closing = False

        data = self._data_check()

        def on_open(ws):
            data.logger_internal.info("WebSocket Open")
            # syncInitメッセージを準備してなければqueueの先頭に入れる
            if not data._msg_first:
                data.queue_first()
            # 接続完了 send_threadが動き始める
            with data._connection_cv:
                data.connected = True
                data._connection_cv.notify_all()

        def on_message(ws, message: bytes):
            data.logger_internal.debug("Received message")
            # webcface.client_impl.on_recv(self, data, message)
            with data.recv_cv:
                data.recv_queue.append(message)
                data.recv_cv.notify_all()

        def on_error(ws, error):
            data.logger_internal.info(f"WebSocket Error: {error}")

        def on_close(ws, close_status_code, close_msg):
            data.logger_internal.info("WebSocket Closed")
            with data._connection_cv:
                data.connected = False
                data._connection_cv.notify_all()
            data.clear_msg()
            data.self_member_id = None
            data.sync_init_end = False
            # data.queue_msg(webcface.client_impl.sync_data_first(self, data))

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
                if not data.auto_reconnect:
                    break
                if not self._closing:
                    time.sleep(0.1)
            data.logger_internal.debug(f"reconnect_thread end")

        self._reconnect_thread = threading.Thread(target=reconnect, daemon=True)

        def msg_send():
            data = self._data_check()
            while self._reconnect_thread.is_alive():
                while (
                    not data.connected or not data.has_msg()
                ) and self._reconnect_thread.is_alive():
                    if not data.connected:
                        with data._connection_cv:
                            data._connection_cv.wait(timeout=0.1)
                    data.wait_msg(timeout=0.1)
                msgs = self._data_check().pop_msg()
                if msgs is not None and self._ws is not None and self.connected:
                    try:
                        data.logger_internal.debug("Sending message")
                        self._ws.send(webcface.message.pack(msgs))
                    except Exception as e:
                        data.logger_internal.error(f"Error Sending message {e}")

        self._send_thread = threading.Thread(target=msg_send, daemon=True)

        self._auto_sync = auto_sync
        self._sync_thread = None

        # data.queue_msg(webcface.client_impl.sync_data_first(self, data))

        def close_at_exit():
            data.logger_internal.debug(
                "Client close triggered at interpreter termination"
            )
            self.close()
            if self._reconnect_thread.is_alive():
                self._reconnect_thread.join()
            if self._send_thread.is_alive():
                self._send_thread.join()
            if self._sync_thread is not None and self._sync_thread.is_alive():
                self._sync_thread.join()

        atexit.register(close_at_exit)

    def close(self) -> None:
        """接続を切る

        * ver1.1.1〜 キューにたまっているデータがすべて送信されるまで待機
        * ver1.1.2〜 サーバーへの接続に失敗した場合は待機しない
        """
        if not self._closing:
            self._closing = True
            while self._data_check().has_msg() and self._reconnect_thread.is_alive():
                self._data_check().wait_empty(timeout=1)
            if self._ws is not None:
                self._ws.close()

    def start(self) -> None:
        """サーバーに接続を開始する"""
        if not self._reconnect_thread.is_alive():
            self._reconnect_thread.start()
        if not self._send_thread.is_alive():
            self._send_thread.start()
        if self._auto_sync is not None:
            if self._sync_thread is None:

                def loop_sync():
                    while self._reconnect_thread.is_alive():
                        self.sync(timeout=self._auto_sync, auto_start=False)

                self._sync_thread = threading.Thread(target=loop_sync, daemon=True)
            if not self._sync_thread.is_alive():
                self._sync_thread.start()

    def wait_connection(self) -> None:
        """サーバーに接続が成功するまで待機する。

        接続していない場合、start()を呼び出す。
        """
        self.start()
        data = self._data_check()
        while not data.connected or not data.sync_init_end:
            if not data.connected:
                with data._connection_cv:
                    self._data_check()._connection_cv.wait()
            else:
                if len(data.recv_queue) == 0:
                    with data.recv_cv:
                        data.recv_cv.wait(timeout=None)
                self.sync(timeout=0)

    @property
    def connected(self) -> bool:
        """サーバーに接続できていればtrue

        ver2.0からプロパティ
        """
        return self._data_check().connected

    def sync(self, timeout: Optional[float] = 0, auto_start: bool = True) -> None:
        """送信用にセットしたデータをすべて送信キューに入れ、受信したデータを処理する

        * 実際に送信をするのは別スレッドであり、この関数はブロックしない。
        * サーバーに接続していない場合、start()を呼び出す。
        * ver2.0〜: 受信したデータがあれば各種コールバックをこのスレッドで呼び出し、
        それがすべて完了するまでこの関数はブロックされる。
        * ver2.0〜: timeoutが正の場合、データを受信してもしなくても
        timeout 経過するまでは繰り返しsync()を再試行する。
        timeout=0 または負の値なら再試行せず即座にreturnする。
        (デフォルト、ver1.1までのsync()と同じ)
        * timeout がNoneの場合、close()するまで無制限に待機する。
        * autoReconnectがfalseでサーバーに接続できてない場合はreturnする。
        (deadlock回避)

        :param timeout: (ver2.0〜) sync()を再試行するタイムアウト (秒単位の実数、またはNone)
        :param auto_start: (ver2.1〜)
        """
        if auto_start:
            self.start()
        data = self._data_check()
        if data._msg_first:
            data.queue_msg_always(webcface.client_impl.sync_data(data, False))
        else:
            data.queue_first()
        start_ns = time.time_ns()
        timeout_ns = round(timeout * 1e9) if timeout is not None else None
        while not self._closing and (data.connected or data.auto_reconnect):
            with data.recv_cv:
                if len(data.recv_queue) == 0:
                    timeout_now = None
                    if timeout_ns is not None:
                        timeout_now = (
                            timeout_ns - (time.time_ns() - start_ns)
                        ) / 1e9
                    data.recv_cv.wait(timeout=timeout_now)
                for msg in data.recv_queue:
                    webcface.client_impl.on_recv(self, data, msg)
                data.recv_queue = []
            if (
                timeout_ns is not None
                and time.time_ns() - start_ns >= timeout_ns
            ):
                break

    def member(self, member_name: str) -> webcface.member.Member:
        """他のメンバーにアクセスする"""
        return webcface.member.Member(self, member_name)

    def members(self) -> Iterable[webcface.member.Member]:
        """サーバーに接続されている他のmemberをすべて取得する。

        自分自身と、無名のmemberを除く。
        """
        return map(self.member, self._data_check().value_store.get_members())

    def on_member_entry(self, func: Callable) -> Callable:
        """Memberが追加されたときのイベント

        コールバックの引数にはMemberオブジェクトが渡される。

        ver2.0〜:
        * 呼び出したいコールバック関数をfuncとして
        :code:`client.on_member_entry(func)`
        などとすれば関数を登録できる。
        * または :code:`@client.on_member_entry` をデコレーターとして使う。
        """
        self._data_check().on_member_entry = func
        return func

    @property
    def logging_handler(self) -> logging.Handler:
        """webcfaceに出力するloggingのHandler

        (ver2.1〜: Log名は "default", log().handler と同じ)

        :return: logger.addHandler にセットして使う
        """
        return webcface.log_handler.Handler(self._data_check(), "default")

    @property
    def logging_io(self) -> io.TextIOBase:
        """webcfaceとstderrに出力するio

        (ver2.1〜: Log名は "default", log().io と同じ)
        """
        return webcface.log_handler.LogWriteIO(self._data_check(), "default")

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

    @property
    def server_hostname(self) -> str:
        """サーバーのホスト名
        (ver2.0〜)
        """
        return self._data_check().svr_hostname
