from typing import TypeVar, Generic, Dict, Tuple, Optional, Callable, List, Union
import threading
import datetime
import logging
import webcface.field
import webcface.func_info
import webcface.view_base
import webcface.log_handler
import webcface.canvas2d_base
import webcface.canvas3d_base
import webcface.image_frame

T = TypeVar("T")
R = TypeVar("R")


class SyncDataStore2(Generic[T, R]):
    self_member_name: str
    data_send: Dict[str, T]
    data_send_prev: Dict[str, T]
    data_recv: Dict[str, Dict[str, T]]
    entry: Dict[str, List[str]]
    req: Dict[str, Dict[str, int]]
    req_info: Dict[str, Dict[str, R]]
    lock: threading.RLock
    should_send: Callable

    def __init__(self, name: str, should_send: Optional[Callable] = None) -> None:
        self.self_member_name = name
        self.data_send = {}
        self.data_send_prev = {}
        self.data_recv = {}
        self.entry = {}
        self.req = {}
        self.req_info = {}
        self.lock = threading.RLock()
        self.should_send = should_send or SyncDataStore2.should_send_always

    def is_self(self, member: str) -> bool:
        return self.self_member_name == member

    @staticmethod
    def should_send_always(prev, current) -> bool:
        return True

    @staticmethod
    def should_not_send_twice(prev, current) -> bool:
        if prev is None:
            return True
        return False

    @staticmethod
    def should_send_on_change(prev, current) -> bool:
        if prev is None or prev != current:
            return True
        return False

    def set_send(self, field: str, data: T) -> None:
        with self.lock:
            if self.should_send(
                self.data_recv.get(self.self_member_name, {}).get(field), data
            ):
                self.data_send[field] = data
            self.set_recv(self.self_member_name, field, data)

    def set_recv(self, member: str, field: str, data: T) -> None:
        with self.lock:
            if member not in self.data_recv:
                self.data_recv[member] = {}
            self.data_recv[member][field] = data

    def add_req(self, member: str, field: str, req_data: Optional[R] = None) -> int:
        with self.lock:
            if not self.is_self(member) and self.req.get(member, {}).get(field, 0) == 0:
                max_req = 0
                for r in self.req.values():
                    max_req = max(max_req, max(r.values()))
                new_req = max_req + 1
                if member not in self.req:
                    self.req[member] = {}
                self.req[member][field] = new_req
                if req_data is not None:
                    if member not in self.req_info:
                        self.req_info[member] = {}
                    self.req_info[member][field] = req_data
                return new_req
            elif (
                not self.is_self(member)
                and req_data is not None
                and self.req_info.get(member, {}).get(field) != req_data
            ):
                if member not in self.req_info:
                    self.req_info[member] = {}
                self.req_info[member][field] = req_data
                return self.req[member][field]
            return 0

    def get_req_info(self, member: str, field: str) -> Optional[R]:
        with self.lock:
            return self.req_info.get(member, {}).get(field)

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

    def get_members(self) -> List[str]:
        with self.lock:
            return list(self.entry.keys())

    def get_entry(self, member: str) -> List[str]:
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
    entry: List[str]
    lock: threading.RLock

    def __init__(self, name: str) -> None:
        self.self_member_name = name
        self.data_recv = {}
        self.req = {}
        self.entry = []
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

    def set_entry(self, member: str) -> None:
        with self.lock:
            if member not in self.entry:
                self.entry.append(member)

    def clear_entry(self, member: str) -> None:
        with self.lock:
            if member in self.entry:
                self.entry.remove(member)

    def get_entry(self, member: str) -> bool:
        with self.lock:
            return member in self.entry

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
    results: "List[Optional[webcface.func_info.PromiseData]]"
    lock: threading.Lock

    def __init__(self):
        self.results = []
        self.lock = threading.Lock()

    def add_result(
        self,
        caller: str,
        base: "webcface.field.Field",
    ) -> "webcface.func_info.Promise":
        with self.lock:
            caller_id = len(self.results)
            r = webcface.func_info.PromiseData(base, caller_id, caller)
            self.results.append(r)
            return webcface.func_info.Promise(r)

    def get_result(self, caller_id: int) -> "webcface.func_info.PromiseData":
        with self.lock:
            r = self.results[caller_id]
            if r is None:
                raise IndexError()
            return r

    def del_result(self, caller_id: int) -> None:
        with self.lock:
            if caller_id < len(self.results):
                self.results[caller_id] = None


class ClientData:
    self_member_name: str
    value_store: SyncDataStore2[List[float], None]
    text_store: SyncDataStore2[Union[float, bool, str], None]
    image_store: (
        "SyncDataStore2[webcface.image_frame.ImageFrame, webcface.image_frame.ImageReq]"
    )
    func_store: "SyncDataStore2[webcface.func_info.FuncInfo, None]"
    view_store: "SyncDataStore2[webcface.view.ViewData, None]"
    canvas2d_store: "SyncDataStore2[webcface.canvas2d.Canvas2DData, None]"
    canvas3d_store: "SyncDataStore2[webcface.canvas3d.Canvas3DData, None]"
    log_store: "SyncDataStore2[webcface.log_handler.LogData, None]"
    sync_time_store: SyncDataStore1[datetime.datetime]
    func_result_store: FuncResultStore
    func_listener_handlers: "Dict[str, List[webcface.func_info.CallHandle]]"
    member_ids: Dict[str, int]
    member_lib_name: Dict[int, str]
    member_lib_ver: Dict[int, str]
    member_remote_addr: Dict[int, str]
    svr_name: str
    svr_version: str
    svr_hostname: str
    ping_status_req: bool
    ping_status: Dict[int, int]
    connected: bool
    _connection_cv: threading.Condition
    _msg_first: bool  # syncInitメッセージをqueueに入れたらtrue
    _msg_queue: "List[List[webcface.message.MessageBase]]"
    _msg_cv: threading.Condition
    recv_queue: List[bytes]
    recv_cv: threading.Condition
    logger_internal: logging.Logger
    self_member_id: Optional[int]
    sync_init_end: bool
    auto_reconnect: bool
    on_member_entry: Optional[Callable]
    on_ping: Dict[str, Callable]
    on_value_entry: Dict[str, Callable]
    on_text_entry: Dict[str, Callable]
    on_image_entry: Dict[str, Callable]
    on_view_entry: Dict[str, Callable]
    on_func_entry: Dict[str, Callable]
    on_canvas2d_entry: Dict[str, Callable]
    on_canvas3d_entry: Dict[str, Callable]
    on_log_entry: Dict[str, Callable]
    on_sync: Dict[str, Callable]
    on_value_change: Dict[str, Dict[str, Callable]]
    on_text_change: Dict[str, Dict[str, Callable]]
    on_image_change: Dict[str, Dict[str, Callable]]
    on_view_change: Dict[str, Dict[str, Callable]]
    on_canvas2d_change: Dict[str, Dict[str, Callable]]
    on_canvas3d_change: Dict[str, Dict[str, Callable]]
    on_log_change: Dict[str, Callable]

    def __init__(
        self, name: str, logger_internal: logging.Logger, auto_reconnect: bool
    ) -> None:
        self.self_member_name = name
        self.value_store = SyncDataStore2[List[float], None](
            name, SyncDataStore2.should_send_on_change
        )
        self.text_store = SyncDataStore2[Union[float, bool, str], None](
            name, SyncDataStore2.should_send_on_change
        )
        self.image_store = SyncDataStore2[
            webcface.image_frame.ImageFrame, webcface.image_frame.ImageReq
        ](name)
        self.func_store = SyncDataStore2[webcface.func_info.FuncInfo, None](
            name, SyncDataStore2.should_not_send_twice
        )
        self.view_store = SyncDataStore2[webcface.view.ViewData, None](name)
        self.canvas2d_store = SyncDataStore2[webcface.canvas2d.Canvas2DData, None](name)
        self.canvas3d_store = SyncDataStore2[webcface.canvas3d.Canvas3DData, None](name)
        self.log_store = SyncDataStore2[webcface.log_handler.LogData, None](name)
        self.sync_time_store = SyncDataStore1[datetime.datetime](name)
        self.func_result_store = FuncResultStore()
        self.func_listener_handlers = {}
        self.member_ids = {}
        self.member_lib_name = {}
        self.member_lib_ver = {}
        self.member_remote_addr = {}
        self.svr_name = ""
        self.svr_version = ""
        self.svr_hostname = ""
        self.ping_status_req = False
        self.ping_status = {}
        self.connected = False
        self._connection_cv = threading.Condition()
        self._msg_first = False
        self._msg_queue = []
        self._msg_cv = threading.Condition()
        self.recv_queue = []
        self.recv_cv = threading.Condition()
        self.logger_internal = logger_internal
        self.self_member_id = None
        self.sync_init_end = False
        self.auto_reconnect = auto_reconnect
        self.on_member_entry = None
        self.on_ping = {}
        self.on_value_entry = {}
        self.on_view_entry = {}
        self.on_text_entry = {}
        self.on_image_entry = {}
        self.on_func_entry = {}
        self.on_canvas2d_entry = {}
        self.on_canvas3d_entry = {}
        self.on_log_entry = {}
        self.on_sync = {}
        self.on_value_change = {}
        self.on_text_change = {}
        self.on_image_change = {}
        self.on_view_change = {}
        self.on_canvas2d_change = {}
        self.on_canvas3d_change = {}
        self.on_log_change = {}

    def queue_first(self) -> None:
        with self._msg_cv:
            self._msg_queue.insert(0, webcface.client_impl.sync_data_first(self))
            self._msg_first = True

    def queue_msg_always(self, msgs: "List[webcface.message.MessageBase]") -> None:
        """メッセージをキューに入れる"""
        with self._msg_cv:
            self._msg_queue.append(msgs)
            self._msg_cv.notify_all()

    def queue_msg_online(self, msgs: "List[webcface.message.MessageBase]") -> bool:
        """接続できていればキューに入れtrueを返す"""
        with self._connection_cv:
            if self.connected:
                with self._msg_cv:
                    self._msg_queue.append(msgs)
                    self._msg_cv.notify_all()
                return True
            return False

    def queue_msg_req(self, msgs: "List[webcface.message.MessageBase]") -> bool:
        """msg_firstが空でなければキューに入れtrueを返す"""
        with self._msg_cv:
            if self._msg_first:
                self._msg_queue.append(msgs)
                self._msg_cv.notify_all()
                return True
            return False

    def clear_msg(self) -> None:
        with self._msg_cv:
            self._msg_queue = []
            self._msg_first = False
            self._msg_cv.notify_all()

    def has_msg(self) -> bool:
        return len(self._msg_queue) > 0

    def wait_msg(self, timeout: Optional[float] = None) -> None:
        with self._msg_cv:
            while len(self._msg_queue) == 0:
                self._msg_cv.wait(timeout)
                if timeout is not None:
                    break

    def wait_empty(self, timeout: Optional[float] = None) -> None:
        with self._msg_cv:
            while len(self._msg_queue) > 0:
                self._msg_cv.wait(timeout)
                if timeout is not None:
                    break

    def pop_msg(self) -> "Optional[List[webcface.message.MessageBase]]":
        with self._msg_cv:
            if len(self._msg_queue) == 0:
                return None
            msg = self._msg_queue.pop(0)
            self._msg_cv.notify_all()
            return msg

    def is_self(self, member: str) -> bool:
        return self.self_member_name == member

    def get_member_name_from_id(self, m_id: int) -> str:
        for k, v in self.member_ids.items():
            if v == m_id:
                return k
        return ""

    def get_member_id_from_name(self, name: str) -> int:
        return self.member_ids.get(name, 0)
