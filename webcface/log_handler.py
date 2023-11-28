from __future__ import annotations
import io
from typing import Iterable
import sys
import logging
import datetime
import webcface.client_data


class LogLine:
    level: int
    time: datetime.datetime
    message: str

    def __init__(self, level: int, time: datetime.datetime, message: str) -> None:
        self.level = level
        self.time = time
        self.message = message


class Handler(logging.Handler):
    _data: webcface.client_data.ClientData

    def __init__(self, data: webcface.client_data.ClientData) -> None:
        super().__init__(logging.NOTSET)
        self._data = data

    def emit(self, record: logging.LogRecord) -> None:
        self.write(
            LogLine(
                record.levelno // 10,
                datetime.datetime.fromtimestamp(record.created),
                record.message,
            )
        )

    def write(self, line: LogLine) -> None:
        with self._data.log_store.lock:
            ls = self._data.log_store.get_recv(self._data.self_member_name)
            assert ls is not None
            ls.append(line)


class LogWriteIO(io.TextIOBase):
    _data: webcface.client_data.ClientData

    def __init__(self, data: webcface.client_data.ClientData) -> None:
        super().__init__()
        self._data = data

    def isatty(self) -> bool:
        """:return: False"""
        return False

    def readable(self) -> bool:
        """:return: False"""
        return False

    def seekable(self) -> bool:
        """:return: False"""
        return False

    def writable(self) -> bool:
        """:return: True"""
        return True

    def write(self, s: str) -> int:
        """webcfaceに文字列を出力すると同時にsys.__stderr__にも流す"""
        for l in s.split("\n"):
            if len(l) > 0:
                self._data.log_handler.write(LogLine(2, datetime.datetime.now(), l))
        return sys.__stdout__.write(s)
