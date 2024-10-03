from __future__ import annotations
import io
from typing import Iterable, List
import sys
import logging
import datetime
import webcface.client_data


class LogData:
    data: List[LogLine]
    sent_lines: int

    def __init__(self) -> None:
        self.data = []
        self.sent_lines = 0


class LogLine:
    level: int
    time: datetime.datetime
    message: str

    def __init__(self, level: int, time: datetime.datetime, message: str) -> None:
        self.level = level
        self.time = time
        self.message = message


class Handler(logging.Handler):
    _log: webcface.log.Log

    def __init__(self, data: webcface.client_data.ClientData, name: str) -> None:
        super().__init__(logging.NOTSET)
        self._log = webcface.log.Log(
            webcface.field.Field(data, data.self_member_name), name
        )

    def emit(self, record: logging.LogRecord) -> None:
        self._log.append(
            record.levelno // 10,
            record.getMessage(),
            datetime.datetime.fromtimestamp(record.created),
        )


class LogWriteIO(io.TextIOBase):
    _log: webcface.log.Log

    def __init__(self, data: webcface.client_data.ClientData, name: str) -> None:
        super().__init__()
        self._log = webcface.log.Log(
            webcface.field.Field(data, data.self_member_name), name
        )

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
                self._log.append(2, l, datetime.datetime.now())
        return sys.__stderr__.write(s)
