from __future__ import annotations
from typing import TypeVar, Generic, Dict, Tuple, Optional, Callable
import threading
import json
import blinker
import webcface.field
import webcface.func_info
import webcface.view_base
import webcface.log_handler

T = TypeVar("T")


class SyncDataStore2(Generic[T]):
    self_member_name: str
    data_send: Dict[str, T]
    data_send_prev: Dict[str, T]
    data_recv: Dict[str, Dict[str, T]]
    entry: Dict[str, list[str]]
    req: Dict[str, Dict[str, int]]
    lock: threading.RLock

    def __init__(self, name: str) -> None:
        self.self_member_name = name
        self.data_send = {}
        self.data_send_prev = {}
        self.data_recv = {}
        self.entry = {}
        self.req = {}
        self.lock = threading.RLock()

    def is_self(self, member: str) -> bool:
        return self.self_member_name == member

    def set_send(self, field: str, data: T) -> None:
        with self.lock:
            self.data_send[field] = data
            self.set_recv(self.self_member_name, field, data)

    def set_recv(self, member: str, field: str, data: T) -> None:
        with self.lock:
            if member not in self.data_recv:
                self.data_recv[member] = {}
            self.data_recv[member][field] = data

    def add_req(self, member: str, field: str) -> int:
        with self.lock:
            if not self.is_self(member) and self.req.get(member, {}).get(field, 0) == 0:
                max_req = 0
                for r in self.req.values():
                    max_req = max(max_req, max(r.values()))
                new_req = max_req + 1
                if member not in self.req:
                    self.req[member] = {}
                self.req[member][field] = new_req
                return new_req
            return 0

    def get_recv(self, member: str, field: str) -> Optional[T]:
        with self.lock:
            d = self.data_recv.get(member, {}).get(field)
            return d

    def unset_recv(self, member: str, field: str) -> bool:
        with self.lock:
            if self.data_recv.get(member, {}).get(field) is not None:
                del self.data_recv[member][field]
            if not self.is_self(member) and self.req.get(member, {}).get(field, 0) > 0:
                self.req[member][field] = 0
                return True
            return False

    def get_members(self) -> list[str]:
        with self.lock:
            return list(self.entry.keys())

    def get_entry(self, member: str) -> list[str]:
        with self.lock:
            return self.entry.get(member, [])

    def add_member(self, member: str) -> None:
        with self.lock:
            self.entry[member] = []

    def set_entry(self, member: str, field: str) -> None:
        with self.lock:
            if member not in self.entry:
                self.entry[member] = []
            self.entry[member].append(field)

    def transfer_send(self, is_first: bool) -> Dict[str, T]:
        with self.lock:
            if is_first:
                self.data_send = {}
                self.data_send_prev = {}
                data_current = self.data_recv.get(self.self_member_name, {})
                for k, v in data_current.items():
                    self.data_send_prev[k] = v
                return data_current
            else:
                s = self.data_send
                self.data_send_prev = s
                self.data_send = {}
                return s

    def get_send_prev(self, is_first: bool) -> Dict[str, T]:
        with self.lock:
            if is_first:
                return {}
            else:
                return self.data_send_prev

    def transfer_req(self) -> Dict[str, Dict[str, int]]:
        with self.lock:
            # if is_first:
            # self.req_send = {}
            return self.req
            # else:
            #     r = self.req_send
            #     self.req_send = {}
            #     return r

    def get_req(self, i: int, sub_field: str) -> Tuple[str, str]:
        with self.lock:
            for rm, r in self.req.items():
                for rf, ri in r.items():
                    if ri == i:
                        if sub_field != "":
                            return (rm, rf + "." + sub_field)
                        else:
                            return (rm, rf)
            return ("", "")


class SyncDataStore1(Generic[T]):
    self_member_name: str
    data_recv: Dict[str, T]
    req: Dict[str, bool]
    lock: threading.RLock

    def __init__(self, name: str) -> None:
        self.self_member_name = name
        self.data_recv = {}
        self.req = {}
        self.lock = threading.RLock()

    def is_self(self, member: str) -> bool:
        return self.self_member_name == member

    def set_recv(self, member: str, data: T) -> None:
        with self.lock:
            self.data_recv[member] = data

    def add_req(self, member: str) -> bool:
        with self.lock:
            if not self.is_self(member) and not self.req.get(member, False):
                self.req[member] = True
                return True
            return False

    def get_recv(self, member: str) -> Optional[T]:
        with self.lock:
            return self.data_recv.get(member, None)

    def clear_req(self, member: str) -> bool:
        with self.lock:
            if not self.is_self(member) and self.req.get(member, False):
                self.req[member] = False
                return True
            return False

    def transfer_req(self) -> Dict[str, bool]:
        with self.lock:
            # if is_first:
            #     self.req_send = {}
            return self.req
            # else:
            #     r = self.req_send
            #     self.req_send = {}
            #     return r


class FuncResultStore:
    results: list[webcface.func_info.AsyncFuncResult]
    lock: threading.Lock

    def __init__(self):
        self.results = []
        self.lock = threading.Lock()

    def add_result(
        self, caller: str, base: webcface.field.Field
    ) -> webcface.func_info.AsyncFuncResult:
        with self.lock:
            caller_id = len(self.results)
            r = webcface.func_info.AsyncFuncResult(caller_id, caller, base)
            self.results.append(r)
            return r

    def get_result(self, caller_id: int) -> webcface.func_info.AsyncFuncResult:
        with self.lock:
            return self.results[caller_id]


class ClientData:
    self_member_name: str
    value_store: SyncDataStore2[list[float]]
    text_store: SyncDataStore2[str]
    func_store: SyncDataStore2[webcface.func_info.FuncInfo]
    view_store: SyncDataStore2[list[webcface.view_base.ViewComponentBase]]
    log_store: SyncDataStore1[list[webcface.log_handler.LogLine]]
    func_result_store: FuncResultStore
    logging_handler: webcface.log_handler.Handler
    log_sent_lines: int
    logging_io: webcface.log_handler.LogWriteIO
    member_ids: Dict[str, int]
    member_lib_name: Dict[int, str]
    member_lib_ver: Dict[int, str]
    member_remote_addr: Dict[int, str]
    svr_name: str
    svr_version: str
    ping_status_req: bool
    ping_status_req_send: bool
    ping_status: dict[int, int]
    _msg_queue: list[list[webcface.message.MessageBase]]
    _msg_cv: threading.Condition

    def __init__(self, name: str) -> None:
        self.self_member_name = name
        self.value_store = SyncDataStore2[list[float]](name)
        self.text_store = SyncDataStore2[str](name)
        self.func_store = SyncDataStore2[webcface.func_info.FuncInfo](name)
        self.view_store = SyncDataStore2[list[webcface.view_base.ViewComponentBase]](
            name
        )
        self.log_store = SyncDataStore1[list[webcface.log_handler.LogLine]](name)
        self.log_store.set_recv(name, [])
        self.log_sent_lines = 0
        self.func_result_store = FuncResultStore()
        self.logging_handler = webcface.log_handler.Handler(self)
        self.logging_io = webcface.log_handler.LogWriteIO(self)
        self.member_ids = {}
        self.member_lib_name = {}
        self.member_lib_ver = {}
        self.member_remote_addr = {}
        self.svr_name = ""
        self.svr_version = ""
        self.ping_status_req = False
        self.ping_status_req_send = False
        self.ping_status = {}
        self._msg_queue = []
        self._msg_cv = threading.Condition()

    def queue_msg(self, msgs: list[webcface.message.MessageBase]) -> None:
        with self._msg_cv:
            self._msg_queue.append(msgs)
            self._msg_cv.notify_all()

    def clear_msg(self) -> None:
        with self._msg_cv:
            self._msg_queue = []

    def has_msg(self) -> bool:
        return len(self._msg_queue) > 0

    def wait_msg(self) -> None:
        with self._msg_cv:
            while len(self._msg_queue) == 0:
                self._msg_cv.wait()

    def pop_msg(self) -> Optional[list[webcface.message.MessageBase]]:
        with self._msg_cv:
            if len(self._msg_queue) == 0:
                return None
            return self._msg_queue.pop(0)

    def is_self(self, member: str) -> bool:
        return self.self_member_name == member

    def get_member_name_from_id(self, m_id: int) -> str:
        for k, v in self.member_ids.items():
            if v == m_id:
                return k
        return ""

    def get_member_id_from_name(self, name: str) -> int:
        return self.member_ids.get(name, 0)

    def signal(
        self, signal_type: str, member: str = "", field: str = ""
    ) -> blinker.NamedSignal:
        if signal_type == "member_entry":
            assert member == "" and field == ""
            key = [id(self), signal_type]
        elif (
            signal_type == "value_entry"
            or signal_type == "text_entry"
            or signal_type == "view_entry"
            or signal_type == "func_entry"
            or signal_type == "log_append"
            or signal_type == "sync"
            or signal_type == "ping"
        ):
            assert member != "" and field == ""
            key = [id(self), signal_type, member]
        elif (
            signal_type == "value_change"
            or signal_type == "text_change"
            or signal_type == "view_change"
        ):
            assert member != "" and field != ""
            key = [id(self), signal_type, member, field]
        else:
            raise ValueError("invalid signal type " + signal_type)
        return blinker.signal(json.dumps(key))
