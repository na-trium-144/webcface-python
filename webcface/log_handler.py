from __future__ import annotations
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
    _send_queue: list[LogLine]

    def __init__(self, data: webcface.client_data.ClientData) -> None:
        super().__init__(logging.NOTSET)
        self._data = data
        self._send_queue = []

    def emit(self, record: logging.LogRecord) -> None:
        ll = LogLine(
            record.levelno // 10,
            datetime.datetime.fromtimestamp(record.created),
            record.message,
        )
        self._send_queue.append(ll)
        ls = self._data.log_store.get_recv(self._data.self_member_name)
        if ls is None:
            ls = []
            self._data.log_store.set_recv(self._data.self_member_name, ls)
        ls.append(ll)
