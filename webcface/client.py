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
import webcface.cffi

class Client(webcface.member.Member):
    """サーバーに接続する

    詳細は `Clientのドキュメント <https://na-trium-144.github.io/webcface/md_01__client.html>`_ を参照

    :arg name: 名前
    :arg host: サーバーのアドレス
    :arg port: サーバーのポート
    """

    _closing: bool
    _wcli: ctypes.c_void_p

    def __init__(
        self, name: str = "", host: str = "127.0.0.1", port: int = 7530
    ) -> None:
        # logger = logging.getLogger(f"webcface_internal({name})")
        # handler = logging.StreamHandler()
        # fmt = logging.Formatter("%(name)s [%(levelname)s] %(message)s")
        # handler.setFormatter(fmt)
        # logger.addHandler(handler)
        # if "WEBCFACE_TRACE" in os.environ:
        #     logger.setLevel(logging.DEBUG)
        # elif "WEBCFACE_VERBOSE" in os.environ:
        #     logger.setLevel(logging.INFO)
        # else:
        #     logger.setLevel(logging.CRITICAL + 1)
        wcli = webcface.cffi.wcfInitW(name, host, port)
        data = webcface.client_data.ClientData(name, wcli)
        super().__init__(
            webcface.field.Field(data, name),
            name,
        )
        self._closing = False
        self._wcli = wcli

        def close_at_exit():
            data.logger_internal.debug(
                "Client close triggered at interpreter termination"
            )
            self.close()

        atexit.register(close_at_exit)

    def close(self) -> None:
        """接続を切る

        * ver1.1.1〜 キューにたまっているデータがすべて送信されるまで待機
        * ver1.1.2〜 サーバーへの接続に失敗した場合は待機しない
        """
        if not self._closing:
            self._closing = True
            webcface.cffi.wcfClose(self._wcli)

    def start(self) -> None:
        """サーバーに接続を開始する"""
        ret = webcface.cffi.wcfStart(self._wcli)
        if ret != webcface.cffi.WCF_OK:
            raise RuntimeError("wcfStart failed: " + ret)

    def wait_connection(self) -> None:
        """サーバーに接続が成功するまで待機する。

        接続していない場合、start()を呼び出す。
        """
        raise NotImplementedError()

    def sync(self) -> None:
        """送信用にセットしたデータとリクエストデータをすべて送信キューに入れる。

        実際に送信をするのは別スレッドであり、この関数はブロックしない。

        サーバーに接続していない場合、start()を呼び出す。
        """
        self.start()
        ret = webcface.cffi.wcfSync(self._wcli)
        if ret != webcface.cffi.WCF_OK:
            raise RuntimeError("wcfSync failed: " + ret)

    def member(self, member_name) -> webcface.member.Member:
        """他のメンバーにアクセスする"""
        return webcface.member.Member(self, member_name)

    def members(self) -> Iterable[webcface.member.Member]:
        """サーバーに接続されている他のmemberをすべて取得する。

        自分自身と、無名のmemberを除く。
        """
        raise NotImplementedError()

    @property
    def on_member_entry(self) -> blinker.NamedSignal:
        """Memberが追加されたときのイベント

        コールバックの引数にはMemberオブジェクトが渡される。

        * 呼び出したいコールバック関数をfuncとして
        :code:`client.on_member_entry.connect(func)`
        などとすれば関数を登録できる。
        * または :code:`@client.on_member_entry.connect` をデコレーターとして使う。
        """
        raise NotImplementedError()
        # return self._data_check().signal("member_entry")

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
        raise NotImplementedError()
        # return self._data_check().svr_name

    @property
    def server_version(self) -> str:
        """サーバーのバージョン"""
        raise NotImplementedError()
        # return self._data_check().svr_version
