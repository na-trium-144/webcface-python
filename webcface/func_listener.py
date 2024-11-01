from typing import Optional, Union, List
import webcface.field
import webcface.func_info


class FuncListener(webcface.field.Field):
    def __init__(
        self,
        base: "Optional[webcface.field.Field]",
        field: str = "",
    ) -> None:
        """Funcを指すクラス

        このコンストラクタを直接使わず、
        Member.func_listener() を使うこと

        詳細は `Funcのドキュメント <https://na-trium-144.github.io/webcface/md_30__func.html>`_ を参照
        """
        if base is None:
            super().__init__(None, "", "")
        else:
            super().__init__(
                base._data, base._member, field if field != "" else base._field
            )

    @property
    def member(self) -> "webcface.member.Member":
        """Memberを返す"""
        return webcface.member.Member(self)

    @property
    def name(self) -> str:
        """field名を返す"""
        return self._field

    def _set_info(self, info: "webcface.func_info.FuncInfo") -> None:
        self._set_check().func_store.set_send(self._field, info)

    def _handlers(self):
        if self._field not in self._set_check().func_listener_handlers:
            self._set_check().func_listener_handlers[self._field] = []
        return self._set_check().func_listener_handlers[self._field]

    def listen(
        self,
        return_type: Optional[Union[int, type]] = None,
        args: "Optional[List[webcface.func_info.Arg]]" = None,
    ) -> "FuncListener":
        """関数呼び出しの待ち受けを開始する"""
        args_num = len(args) if args is not None else 0

        def listener(handle: webcface.func_info.CallHandle):
            if handle.assert_args_num(args_num):
                self._handlers().append(handle)

        self._set_info(
            webcface.func_info.FuncInfo(listener, return_type, args, handle=True)
        )
        return self

    def fetch_call(self) -> "Optional[webcface.func_info.CallHandle]":
        """関数が呼び出されていればhandleを返す"""
        if len(self._handlers()) >= 1:
            return self._handlers().pop(0)
        return None
