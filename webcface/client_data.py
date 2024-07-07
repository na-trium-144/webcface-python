from __future__ import annotations
from typing import TypeVar, Generic, Dict, Tuple, Optional, Callable, List, Callable
import threading
import json
import datetime
import logging
import blinker
import webcface.field
import webcface.func_info
import webcface.view_base
import webcface.log_handler
import webcface.canvas2d_base
import webcface.canvas3d_base
import ctypes


class ClientData:
    self_member_name: str
    logging_handler: webcface.log_handler.Handler
    logging_io: webcface.log_handler.LogWriteIO
    wcli: ctypes.c_void_p

    def __init__(self, name: str, wcli: ctypes.c_void_p) -> None:
        self.self_member_name = name
        self.logging_handler = webcface.log_handler.Handler(self)
        self.logging_io = webcface.log_handler.LogWriteIO(self)
        self.wcli = wcli

    def is_self(self, member: str) -> bool:
        return self.self_member_name == member

