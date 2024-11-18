import threading
import logging
from typing import List
import webcface.client_data
import webcface.message
import webcface.client
import webcface.canvas2d_base
import webcface.image_frame
import webcface


def on_recv(
    wcli: "webcface.client.Client",
    data: webcface.client_data.ClientData,
    message: bytes,
) -> None:
    sync_members: List[str] = []
    if len(message) > 0:
        for m in webcface.message.unpack(message):
            if isinstance(m, webcface.message.SyncInitEnd):
                data.svr_name = m.svr_name
                data.svr_version = m.ver
                data.svr_hostname = m.hostname
                data.self_member_id = m.member_id
                data.sync_init_end = True
            if isinstance(m, webcface.message.Ping):
                data.queue_msg_always([webcface.message.Ping.new()])
            if isinstance(m, webcface.message.PingStatus):
                data.ping_status = m.status
                for member2 in wcli.members():
                    on_ping = data.on_ping.get(member2.name)
                    if on_ping is not None:
                        on_ping(member2)
            if isinstance(m, webcface.message.Sync):
                member = data.get_member_name_from_id(m.member_id)
                data.sync_time_store.set_recv(member, m.time)
                sync_members.append(member)
            if isinstance(m, webcface.message.SyncInit):
                data.value_store.add_member(m.member_name)
                data.text_store.add_member(m.member_name)
                data.func_store.add_member(m.member_name)
                data.view_store.add_member(m.member_name)
                data.canvas2d_store.add_member(m.member_name)
                data.canvas3d_store.add_member(m.member_name)
                data.log_store.add_member(m.member_name)
                data.member_ids[m.member_name] = m.member_id
                data.member_lib_name[m.member_id] = m.lib_name
                data.member_lib_ver[m.member_id] = m.lib_ver
                data.member_remote_addr[m.member_id] = m.addr
                if data.on_member_entry is not None:
                    data.on_member_entry(wcli.member(m.member_name))
            if isinstance(m, webcface.message.ValueRes):
                member, field = data.value_store.get_req(m.req_id, m.sub_field)
                data.value_store.set_recv(member, field, m.data)
                on_change = data.on_value_change.get(member, {}).get(field)
                if on_change is not None:
                    on_change(wcli.member(member).value(field))
            if isinstance(m, webcface.message.ValueEntry):
                member = data.get_member_name_from_id(m.member_id)
                data.value_store.set_entry(member, m.field)
                on_entry = data.on_value_entry.get(member)
                if on_entry is not None:
                    on_entry(wcli.member(member).value(m.field))
            if isinstance(m, webcface.message.TextRes):
                member, field = data.text_store.get_req(m.req_id, m.sub_field)
                data.text_store.set_recv(member, field, m.data)
                on_change = data.on_text_change.get(member, {}).get(field)
                if on_change is not None:
                    on_change(wcli.member(member).variant(field))
            if isinstance(m, webcface.message.TextEntry):
                member = data.get_member_name_from_id(m.member_id)
                data.text_store.set_entry(member, m.field)
                on_entry = data.on_text_entry.get(member)
                if on_entry is not None:
                    on_entry(wcli.member(member).text(m.field))
            if isinstance(m, webcface.message.ImageRes):
                member, field = data.image_store.get_req(m.req_id, m.sub_field)
                data.image_store.set_recv(
                    member,
                    field,
                    webcface.image_frame.ImageFrame(
                        m.width, m.height, m.data, m.color_mode, m.cmp_mode
                    ),
                )
                on_change = data.on_image_change.get(member, {}).get(field)
                if on_change is not None:
                    on_change(wcli.member(member).image(field))
            if isinstance(m, webcface.message.ImageEntry):
                member = data.get_member_name_from_id(m.member_id)
                data.image_store.set_entry(member, m.field)
                on_entry = data.on_image_entry.get(member)
                if on_entry is not None:
                    on_entry(wcli.member(member).image(m.field))
            if isinstance(m, webcface.message.ViewRes):
                member, field = data.view_store.get_req(m.req_id, m.sub_field)
                v_prev = data.view_store.get_recv(member, field)
                if v_prev is None:
                    v_prev = webcface.view.ViewData()
                    data.view_store.set_recv(member, field, v_prev)
                if m.ids is not None:
                    v_prev.ids = m.ids
                for i, c in m.data_diff.items():
                    v_prev.components[i] = c
                on_change = data.on_view_change.get(member, {}).get(field)
                if on_change is not None:
                    on_change(wcli.member(member).view(field))
            if isinstance(m, webcface.message.ViewEntry):
                member = data.get_member_name_from_id(m.member_id)
                data.view_store.set_entry(member, m.field)
                on_entry = data.on_view_entry.get(member)
                if on_entry is not None:
                    on_entry(wcli.member(member).view(m.field))
            if isinstance(m, webcface.message.Canvas2DRes):
                member, field = data.canvas2d_store.get_req(m.req_id, m.sub_field)
                c2_prev = data.canvas2d_store.get_recv(member, field)
                if c2_prev is None:
                    c2_prev = webcface.canvas2d.Canvas2DData(1.0, 1.0)
                    data.canvas2d_store.set_recv(member, field, c2_prev)
                c2_prev.width = m.width
                c2_prev.height = m.height
                if m.ids is not None:
                    c2_prev.ids = m.ids
                for i, c2 in m.data_diff.items():
                    c2_prev.components[i] = c2
                on_change = data.on_canvas2d_change.get(member, {}).get(field)
                if on_change is not None:
                    on_change(wcli.member(member).canvas2d(field))
            if isinstance(m, webcface.message.Canvas2DEntry):
                member = data.get_member_name_from_id(m.member_id)
                data.canvas2d_store.set_entry(member, m.field)
                on_entry = data.on_canvas2d_entry.get(member)
                if on_entry is not None:
                    on_entry(wcli.member(member).canvas2d(m.field))
            if isinstance(m, webcface.message.Canvas3DRes):
                member, field = data.canvas3d_store.get_req(m.req_id, m.sub_field)
                c3_prev = data.canvas3d_store.get_recv(member, field)
                if c3_prev is None:
                    c3_prev = webcface.canvas3d.Canvas3DData()
                    data.canvas3d_store.set_recv(member, field, c3_prev)
                if m.ids is not None:
                    c3_prev.ids = m.ids
                for i, c3 in m.data_diff.items():
                    c3_prev.components[i] = c3
                on_change = data.on_canvas3d_change.get(member, {}).get(field)
                if on_change is not None:
                    on_change(wcli.member(member).canvas3d(field))
            if isinstance(m, webcface.message.Canvas3DEntry):
                member = data.get_member_name_from_id(m.member_id)
                data.canvas3d_store.set_entry(member, m.field)
                on_entry = data.on_canvas3d_entry.get(member)
                if on_entry is not None:
                    on_entry(wcli.member(member).canvas3d(m.field))
            if isinstance(m, webcface.message.LogRes):
                member, field = data.log_store.get_req(m.req_id, m.sub_field)
                log_data = data.log_store.get_recv(member, field)
                if log_data is None:
                    log_data = webcface.log_handler.LogData()
                    data.log_store.set_recv(member, field, log_data)
                log_data.data.extend(m.log)
                if (
                    webcface.Log.keep_lines >= 0
                    and len(log_data.data) > webcface.Log.keep_lines
                ):
                    del log_data.data[: -webcface.Log.keep_lines]
                on_change = data.on_log_change.get(member)
                if on_change is not None:
                    on_change(wcli.member(member).log())
            if isinstance(m, webcface.message.LogEntry):
                member = data.get_member_name_from_id(m.member_id)
                data.log_store.set_entry(member, m.field)
                on_entry = data.on_log_entry.get(member)
                if on_entry is not None:
                    on_entry(wcli.member(member).log(m.field))
            if isinstance(m, webcface.message.FuncInfo):
                member = data.get_member_name_from_id(m.member_id)
                data.func_store.set_entry(member, m.field)
                data.func_store.set_recv(member, m.field, m.func_info)
                on_entry = data.on_func_entry.get(member)
                if on_entry is not None:
                    on_entry(wcli.member(member).func(m.field))
            if isinstance(m, webcface.message.Call):
                func_info = data.func_store.get_recv(data.self_member_name, m.field)
                if func_info is not None:
                    data.queue_msg_always(
                        [
                            webcface.message.CallResponse.new(
                                m.caller_id, m.caller_member_id, True
                            )
                        ]
                    )
                    r = webcface.func_info.PromiseData(
                        webcface.field.Field(data, data.self_member_name, m.field)
                    )
                    func_info.run(r, m.args)

                    p = webcface.func_info.Promise(r)

                    @p.on_finish
                    def on_finish(p: webcface.func_info.Promise):
                        data.queue_msg_always(
                            [
                                webcface.message.CallResult.new(
                                    m.caller_id,
                                    m.caller_member_id,
                                    p.is_error,
                                    p.rejection if p.is_error else p.response,
                                )
                            ]
                        )

                else:
                    data.queue_msg_always(
                        [
                            webcface.message.CallResponse.new(
                                m.caller_id, m.caller_member_id, False
                            )
                        ]
                    )
            if isinstance(m, webcface.message.CallResponse):
                try:
                    r = data.func_result_store.get_result(m.caller_id)
                    r._set_reach(m.started)
                    if not m.started:
                        data.func_result_store.del_result(m.caller_id)
                except IndexError:
                    data.logger_internal.error(
                        f"error receiving call response id={m.caller_id}"
                    )
            if isinstance(m, webcface.message.CallResult):
                try:
                    r = data.func_result_store.get_result(m.caller_id)
                    r._set_finish(m.result, m.is_error)
                    data.func_result_store.del_result(m.caller_id)
                except IndexError:
                    data.logger_internal.error(
                        f"error receiving call result id={m.caller_id}"
                    )
        for member in sync_members:
            on_sync = data.on_sync.get(member)
            if on_sync is not None:
                on_sync(wcli.member(member))


def sync_data_first(
    data: webcface.client_data.ClientData,
) -> List[webcface.message.MessageBase]:
    msgs: List[webcface.message.MessageBase] = []
    msgs.append(
        webcface.message.SyncInit.new(
            data.self_member_name, "python", webcface.__version__
        )
    )

    with data.value_store.lock:
        for m, r in data.value_store.transfer_req().items():
            for k, i in r.items():
                msgs.append(webcface.message.ValueReq.new(m, k, i))
    with data.text_store.lock:
        for m, r in data.text_store.transfer_req().items():
            for k, i in r.items():
                msgs.append(webcface.message.TextReq.new(m, k, i))
    with data.image_store.lock:
        for m, r in data.image_store.transfer_req().items():
            for k, i in r.items():
                info = data.image_store.get_req_info(m, k)
                if info is None:
                    info = webcface.image_frame.ImageReq(
                        None, None, None, None, None, None
                    )
                msgs.append(webcface.message.ImageReq.new(m, k, i, info))
    with data.view_store.lock:
        for m, r in data.view_store.transfer_req().items():
            for k, i in r.items():
                msgs.append(webcface.message.ViewReq.new(m, k, i))
    with data.canvas2d_store.lock:
        for m, r in data.canvas2d_store.transfer_req().items():
            for k, i in r.items():
                msgs.append(webcface.message.Canvas2DReq.new(m, k, i))
    with data.canvas3d_store.lock:
        for m, r in data.canvas3d_store.transfer_req().items():
            for k, i in r.items():
                msgs.append(webcface.message.Canvas3DReq.new(m, k, i))
    with data.log_store.lock:
        for m, r2 in data.log_store.transfer_req().items():
            for k, i in r.items():
                msgs.append(webcface.message.LogReq.new(m, k, i))

    msgs.extend(sync_data(data, True))
    return msgs


def sync_data(
    data: webcface.client_data.ClientData,
    is_first: bool,
) -> List[webcface.message.MessageBase]:
    msgs: List[webcface.message.MessageBase] = []
    msgs.append(webcface.message.Sync.new())

    with data.value_store.lock:
        for k, v in data.value_store.transfer_send(is_first).items():
            msgs.append(webcface.message.Value.new(k, v))
    with data.text_store.lock:
        for k, v2 in data.text_store.transfer_send(is_first).items():
            msgs.append(webcface.message.Text.new(k, v2))
    with data.image_store.lock:
        for k, v8 in data.image_store.transfer_send(is_first).items():
            msgs.append(
                webcface.message.Image.new(
                    k, v8.data, v8.width, v8.height, v8.color_mode, v8.compress_mode
                )
            )
    with data.view_store.lock:
        view_send_prev = data.view_store.get_send_prev(is_first)
        view_send = data.view_store.transfer_send(is_first)
        for k, v4 in view_send.items():
            v_prev = view_send_prev.get(k)
            v_diff = {}
            for i in v4.ids:
                if (
                    v_prev is None
                    or i not in v_prev.components
                    or v_prev.components[i] != v4.components[i]
                ):
                    v_diff[i] = v4.components[i]
            ids_changed = v_prev is None or v_prev.ids != v4.ids
            msgs.append(
                webcface.message.View.new(k, v_diff, (v4.ids if ids_changed else None))
            )
    with data.canvas2d_store.lock:
        canvas2d_send_prev = data.canvas2d_store.get_send_prev(is_first)
        canvas2d_send = data.canvas2d_store.transfer_send(is_first)
        for k, v5 in canvas2d_send.items():
            c2_prev = canvas2d_send_prev.get(k)
            c2_diff = {}
            for i in v5.ids:
                if (
                    c2_prev is None
                    or i not in c2_prev.components
                    or c2_prev.components[i] != v5.components[i]
                ):
                    c2_diff[i] = v5.components[i]
            ids_changed = c2_prev is None or c2_prev.ids != v5.ids
            msgs.append(
                webcface.message.Canvas2D.new(
                    k, v5.width, v5.height, c2_diff, (v5.ids if ids_changed else None)
                )
            )
    with data.canvas3d_store.lock:
        canvas3d_send_prev = data.canvas3d_store.get_send_prev(is_first)
        canvas3d_send = data.canvas3d_store.transfer_send(is_first)
        for k, v6 in canvas3d_send.items():
            c3_prev = canvas3d_send_prev.get(k)
            c3_diff = {}
            for i in v6.ids:
                if (
                    c3_prev is None
                    or i not in c3_prev.components
                    or c3_prev.components[i] != v6.components[i]
                ):
                    c3_diff[i] = v6.components[i]
            ids_changed = c3_prev is None or c3_prev.ids != v6.ids
            msgs.append(
                webcface.message.Canvas3D.new(
                    k, c3_diff, (v6.ids if ids_changed else None)
                )
            )
    with data.log_store.lock:
        log_send = data.log_store.transfer_send(is_first)
        for k, v7 in log_send.items():
            if is_first:
                log_send_data = v7.data
            else:
                log_send_data = v7.data[v7.sent_lines :]
            v7.sent_lines = len(v7.data)
            if len(log_send_data) > 0:
                msgs.append(webcface.message.Log.new(k, log_send_data))
    with data.func_store.lock:
        for k, v3 in data.func_store.transfer_send(is_first).items():
            if not k.startswith("."):
                msgs.append(webcface.message.FuncInfo.new(k, v3))

    return msgs
