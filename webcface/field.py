from typing import Callable, Optional, Iterable, SupportsFloat, List
import webcface.client_data


class FieldBase:
    _member: str
    _field: str

    def __init__(self, member: str, field: str = "") -> None:
        self._member = member
        self._field = field


class Field(FieldBase):
    _data: "Optional[webcface.client_data.ClientData]"

    def __init__(
        self,
        data: "Optional[webcface.client_data.ClientData]",
        member: str,
        field: str = "",
    ) -> None:
        super().__init__(member, field)
        self._data = data

    def _data_check(self) -> "webcface.client_data.ClientData":
        if isinstance(self._data, webcface.client_data.ClientData):
            return self._data
        raise RuntimeError("Cannot access internal data")

    def _set_check(self) -> "webcface.client_data.ClientData":
        data = self._data_check()
        if data.is_self(self._member):
            return data
        raise ValueError("Cannot set data to member other than self")

    @property
    def member(self) -> "webcface.member.Member":
        """Memberを返す (ver3.1〜)"""
        return webcface.member.Member(self)

    @property
    def name(self) -> str:
        """field名を返す (ver3.1〜)"""
        return self._field

    def child(self, field: str) -> "Field":
        """「(このFieldの名前).(追加の名前)」を新しい名前とするField (ver3.1〜)

        * このFieldの名前が空文字列の場合はピリオドをつけず新しい名前とする。
        """
        if self._field == "":
            new_field = field
        elif field == "":
            new_field = self._field
        else:
            new_field = self._field + "." + field
        return Field(self._data, self._member, new_field)

    def value(self, field: str = "") -> "webcface.value.Value":
        """Valueオブジェクトを生成(ver3.1〜)"""
        return webcface.value.Value(self.child(field))

    def text(self, field: str = "") -> "webcface.text.Text":
        """Textオブジェクトを生成(ver3.1〜)"""
        return webcface.text.Text(self.child(field))

    def variant(self, field: str = "") -> "webcface.text.Variant":
        """Variantオブジェクトを生成 (ver2.0〜)"""
        return webcface.text.Variant(self.child(field))

    def image(self, field: str = "") -> "webcface.image.Image":
        """Imageオブジェクトを生成(ver3.1〜)"""
        return webcface.image.Image(self.child(field))

    def view(self, field: str = "") -> "webcface.view.View":
        """Viewオブジェクトを生成(ver3.1〜)"""
        return webcface.view.View(self.child(field))

    def canvas2d(
        self,
        field: str = "",
        width: Optional[SupportsFloat] = None,
        height: Optional[SupportsFloat] = None,
    ) -> "webcface.canvas2d.Canvas2D":
        """Canvas2Dオブジェクトを生成(ver3.1〜)

        :arg width, height: Canvas2Dのサイズを指定して初期化する
        """
        return webcface.canvas2d.Canvas2D(self, field, width, height)

    def canvas3d(self, field: str = "") -> "webcface.canvas3d.Canvas3D":
        """Canvas3Dオブジェクトを生成(ver3.1〜)"""
        return webcface.canvas3d.Canvas3D(self.child(field))

    def log(self, field: str = "default") -> "webcface.log.Log":
        """Logオブジェクトを生成(ver3.1〜)

        :arg field: (ver2.1〜) Logの名前を指定可能(省略すると"default")
        """
        return webcface.log.Log(self.child(field))

    def func(self, arg: str = "", **kwargs) -> "webcface.func.Func":
        """Funcオブジェクトを生成(ver3.1〜)

        #. member.func(arg: str)
            * 指定した名前のFuncオブジェクトを生成・参照する。
        #. @member.func(arg: str, [**kwargs])
            * デコレータとして使い、デコレートした関数を指定した名前でセットする。
            * デコレート後、関数は元のまま返す。
        #. @member.func([**kwargs])
            * 3と同じだが、名前はデコレートした関数から自動で取得される。

        2, 3 の場合のkwargsは Func.set() を参照。
        """
        return webcface.func.Func(self.child(arg), **kwargs)

    def func_listener(self, field: str = "") -> "webcface.func_listener.FuncListener":
        """FuncListenerオブジェクトを生成(ver3.1〜)"""
        return webcface.func_listener.FuncListener(self.child(field))

    def _entries(self, entries: List[str], store, recurse=True):
        prefix_with_sep = self._field + "." if self._field != "" else ""
        for e in store.get_entry(self._member):
            if self._field == "" or e.startswith(prefix_with_sep):
                if not recurse and "." in e[len(prefix_with_sep) :]:
                    e = e[: e.find(".", len(prefix_with_sep))]
                if e not in entries:
                    entries.append(e)

    def _has_entries(self, store) -> bool:
        prefix_with_sep = self._field + "." if self._field != "" else ""
        for e in store.get_entry(self._member):
            if self._field == "" or e.startswith(prefix_with_sep):
                return True
        return False

    def children(self, recurse=False) -> "Iterable[webcface.field.Field]":
        """「(thisの名前).(追加の名前)」で公開されているデータをすべて取得する (ver3.1〜)

        * データ型を問わずすべてのデータを列挙する。
        * recurseがFalseの場合、名前にさらにピリオドが含まれる場合はその前までの名前を返す。
        * 同名で複数のデータが存在する場合も1回のみカウントする。
        """
        entries: List[str] = []
        self._entries(entries, self._data_check().value_store, recurse)
        self._entries(entries, self._data_check().text_store, recurse)
        self._entries(entries, self._data_check().image_store, recurse)
        self._entries(entries, self._data_check().func_store, recurse)
        self._entries(entries, self._data_check().view_store, recurse)
        self._entries(entries, self._data_check().canvas2d_store, recurse)
        self._entries(entries, self._data_check().canvas3d_store, recurse)
        self._entries(entries, self._data_check().log_store, recurse)
        return map(lambda n: Field(self._data, self._member, n), entries)

    def has_children(self) -> bool:
        """「(thisの名前).(追加の名前)」で公開されているデータが1つ以上あればtrue (ver3.1〜)"""
        return (
            self._has_entries(self._data_check().value_store)
            or self._has_entries(self._data_check().text_store)
            or self._has_entries(self._data_check().image_store)
            or self._has_entries(self._data_check().func_store)
            or self._has_entries(self._data_check().view_store)
            or self._has_entries(self._data_check().canvas2d_store)
            or self._has_entries(self._data_check().canvas3d_store)
            or self._has_entries(self._data_check().log_store)
        )

    def value_entries(self) -> "Iterable[webcface.value.Value]":
        """「(thisの名前).(追加の名前)」で公開されているvalueをすべて取得する (ver3.1〜)"""
        entries: List[str] = []
        self._entries(entries, self._data_check().value_store, True)
        return map(lambda n: webcface.value.Value(self, n), entries)

    def text_entries(self) -> "Iterable[webcface.text.Text]":
        """「(thisの名前).(追加の名前)」で公開されているtextをすべて取得する (ver3.1〜)"""
        entries: List[str] = []
        self._entries(entries, self._data_check().text_store, True)
        return map(lambda n: webcface.text.Text(self, n), entries)

    def image_entries(self) -> "Iterable[webcface.image.Image]":
        """「(thisの名前).(追加の名前)」で公開されているimageをすべて取得する (ver3.1〜)"""
        entries: List[str] = []
        self._entries(entries, self._data_check().image_store, True)
        return map(lambda n: webcface.image.Image(self, n), entries)

    def view_entries(self) -> "Iterable[webcface.view.View]":
        """「(thisの名前).(追加の名前)」で公開されているviewをすべて取得する (ver3.1〜)"""
        entries: List[str] = []
        self._entries(entries, self._data_check().view_store, True)
        return map(lambda n: webcface.view.View(self, n), entries)

    def func_entries(self) -> "Iterable[webcface.func.Func]":
        """「(thisの名前).(追加の名前)」で公開されているfuncをすべて取得する (ver3.1〜)"""
        entries: List[str] = []
        self._entries(entries, self._data_check().func_store, True)
        return map(lambda n: webcface.func.Func(self, n), entries)

    def canvas2d_entries(self) -> "Iterable[webcface.canvas2d.Canvas2D]":
        """「(thisの名前).(追加の名前)」で公開されているcanvas2dをすべて取得する (ver3.1〜)"""
        entries: List[str] = []
        self._entries(entries, self._data_check().canvas2d_store, True)
        return map(lambda n: webcface.canvas2d.Canvas2D(self, n), entries)

    def canvas3d_entries(self) -> "Iterable[webcface.canvas3d.Canvas3D]":
        """「(thisの名前).(追加の名前)」で公開されているcanvas3dをすべて取得する (ver3.1〜)"""
        entries: List[str] = []
        self._entries(entries, self._data_check().canvas3d_store, True)
        return map(lambda n: webcface.canvas3d.Canvas3D(self, n), entries)

    def log_entries(self) -> "Iterable[webcface.log.Log]":
        """「(thisの名前).(追加の名前)」で公開されているlogをすべて取得する (ver3.1〜)"""
        entries: List[str] = []
        self._entries(entries, self._data_check().log_store, True)
        return map(lambda n: webcface.log.Log(self, n), entries)
