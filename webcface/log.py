from __future__ import annotations
from typing import Optional, List, Callable
import logging
import io
import datetime
import webcface.field
import webcface.member
import webcface.log_handler


class Log(webcface.field.Field):
    keep_lines: int = 1000

    def __init__(self, base: webcface.field.Field, field: str = "") -> None:
        """Logを指すクラス

        このコンストラクタを直接使わず、
        Member.log() を使うこと

        詳細は `Logのドキュメント <https://na-trium-144.github.io/webcface/md_40__log.html>`_ を参照
        """
        super().__init__(
            base._data, base._member, field if field != "" else base._field
        )

    @property
    def member(self) -> webcface.member.Member:
        """Memberを返す"""
        return webcface.member.Member(self)

    @property
    def name(self) -> str:
        """field名を返す(ver2.1〜)"""
        return self._field

    def on_change(self, func: Callable) -> Callable:
        """logが追加されたときのイベント
        (ver2.0〜)

        コールバックの引数にはLogオブジェクトが渡される。

        まだ値をリクエストされてなければ自動でリクエストされる
        """
        self.request()
        self._data_check().on_log_change[self._member] = func
        return func

    def request(self) -> None:
        """値の受信をリクエストする"""
        req = self._data_check().log_store.add_req(self._member, self._field)
        if req:
            self._data_check().queue_msg_req(
                [webcface.message.LogReq.new(self._member, self._field, req)]
            )

    def try_get(self) -> Optional[List[webcface.log_handler.LogLine]]:
        """ログをlistまたはNoneで返す、まだリクエストされてなければ自動でリクエストされる"""
        self.request()
        log_data = self._data_check().log_store.get_recv(self._member, self._field)
        if log_data is not None:
            return log_data.data[:]
        else:
            return None

    def get(self) -> List[webcface.log_handler.LogLine]:
        """ログをlistで返す、まだリクエストされてなければ自動でリクエストされる"""
        v = self.try_get()
        return v if v is not None else []

    def clear(self) -> Log:
        """受信したログを空にする

        リクエスト状態はクリアしない"""
        log_data = self._data_check().log_store.get_recv(self._member, self._field)
        if log_data is not None:
            log_data.data = []
        return self

    def exists(self) -> bool:
        """このメンバーがログを1行以上出力していればtrue
        (ver2.0〜)

        try_get() などとは違って、実際のデータを受信しない。
        リクエストもしない。
        """
        return self._field in self._data_check().log_store.get_entry(self._member)

    def append(
        self,
        level: int,
        message: str,
        time: datetime.datetime = datetime.datetime.now(),
    ) -> None:
        """ログをwebcfaceに送信する
        (ver2.0〜)

        コンソールなどには出力されない
        """
        data = self._set_check()
        with data.log_store.lock:
            log_data = data.log_store.get_recv(self._member, self._field)
            if log_data is None:
                log_data = webcface.log_handler.LogData()
            log_data.data.append(webcface.log_handler.LogLine(level, time, message))
            data.log_store.set_send(self._field, log_data)

    @property
    def handler(self) -> logging.Handler:
        """webcfaceに出力するloggingのHandler
        (ver2.1〜)

        :return: logger.addHandler にセットして使う
        """
        return webcface.log_handler.Handler(self._data_check(), self._field)

    @property
    def io(self) -> io.TextIOBase:
        """webcfaceとstderrに出力するio
        (ver2.1〜)
        """
        return webcface.log_handler.LogWriteIO(self._data_check(), self._field)
