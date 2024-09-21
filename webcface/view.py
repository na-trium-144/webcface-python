from __future__ import annotations
from typing import Optional, Callable, List, Callable, SupportsFloat, Union
from copy import deepcopy
import webcface.field
import webcface.text
import webcface.view_base
import webcface.view_components
import webcface.client_data
import webcface.func


class ViewComponent(webcface.view_base.ViewComponentBase):
    _data: Optional[webcface.client_data.ClientData]
    _on_click_func_tmp: Optional[Callable]
    _bind_tmp: Optional[webcface.text.InputRef]
    _init: Optional[Union[float, bool, str]]

    @staticmethod
    def from_base(
        base: webcface.view_base.ViewComponentBase,
        data: Optional[webcface.client_data.ClientData],
    ) -> ViewComponent:
        vc = ViewComponent(
            type=base._type,
            text=base._text,
            on_click=base._on_click_func,
            text_color=base._text_color,
            bg_color=base._bg_color,
            min=base._min,
            max=base._max,
            step=base._step,
            option=base._option,
        )
        vc._text_ref = base._text_ref
        vc._data = data
        return vc

    def __init__(
        self,
        type: int = 0,
        text: str = "",
        on_click: Optional[Union[webcface.field.FieldBase, Callable]] = None,
        text_color: int = 0,
        bg_color: int = 0,
        on_change: Optional[Union[webcface.func.Func, Callable]] = None,
        bind: Optional[webcface.text.InputRef] = None,
        min: Optional[SupportsFloat] = None,
        max: Optional[SupportsFloat] = None,
        step: Optional[SupportsFloat] = None,
        option: Optional[List[Union[SupportsFloat, bool, str]]] = None,
        init: Optional[Union[SupportsFloat, bool, str]] = None,
    ) -> None:
        """コンポーネントを作成

        :arg type: コンポーネントの種類 (text(), button()などコンポーネントを作成する各種関数を使えば自動で設定される)
        :arg text: 表示する文字列
        :arg on_click: クリック時に実行する関数
        :arg text_color: 文字の色 (ViewColorのEnumを使う)
        :arg bg_color: 背景の色 (ViewColorのEnumを使う)
        :arg on_change: (ver2.0〜) Inputの値が変更されたときに実行する関数
        :arg bind: (ver2.0〜) Inputの値をバインドするInputRef
            (on_changeとbindはどちらか片方のみを指定すること)
        :arg min: (ver2.0〜) Inputの最小値/最小文字数
        :arg max: (ver2.0〜) Inputの最大値/最大文字数
        :arg step: (ver2.0〜) Inputの刻み幅
        :arg option: (ver2.0〜) Inputの選択肢
        """
        option2: List[Union[str, bool, float]] = []
        if option is not None:
            for op in option:
                if isinstance(op, bool):
                    option2.append(op)
                elif isinstance(init, SupportsFloat):
                    option2.append(float(op))
                else:
                    option2.append(str(op))
        super().__init__(
            type,
            text,
            None,
            None,
            text_color,
            bg_color,
            None if min is None else float(min),
            None if max is None else float(max),
            None if step is None else float(step),
            option2,
        )
        self._data = None
        self._on_click_func = None
        self._text_ref = None
        self._on_click_func_tmp = None
        if init is None:
            self._init = None
        elif isinstance(init, bool):
            self._init = init
        elif isinstance(init, SupportsFloat):
            self._init = float(init)
        else:
            self._init = str(init)
        if on_change is not None:
            if isinstance(on_change, webcface.func.Func):
                bind_new = webcface.text.InputRef()

                def on_change_impl(val: Union[float, bool, str]):
                    if bind_new._state is not None:
                        bind_new._state.set(val)
                    return on_change.run(val)

                bind = bind_new
                on_click = on_change_impl
            elif callable(on_change):
                bind_new = webcface.text.InputRef()

                def on_change_impl(val: Union[float, bool, str]):
                    if bind_new._state is not None:
                        bind_new._state.set(val)
                    return on_change(val)

                bind = bind_new
                on_click = on_change_impl
        elif bind is not None:

            def on_change_impl(val: Union[float, bool, str]):
                if bind._state is not None:
                    bind._state.set(val)

            on_click = on_change_impl
        self._bind_tmp = bind
        if isinstance(on_click, webcface.field.FieldBase):
            self._on_click_func = on_click
        elif callable(on_click):
            self._on_click_func_tmp = on_click
        if isinstance(on_click, webcface.field.Field) and on_click._data is not None:
            self._data = on_click._data
        if isinstance(on_change, webcface.field.Field) and on_change._data is not None:
            self._data = on_change._data

    def lock_tmp(
        self, data: webcface.client_data.ClientData, field_id: str
    ) -> ViewComponent:
        """on_clickをFuncオブジェクトにlockする"""
        if self._on_click_func_tmp is not None:
            on_click = webcface.func.Func(
                webcface.field.Field(data, data.self_member_name), field_id
            )
            on_click.set(self._on_click_func_tmp)
            self._on_click_func = on_click
        if self._bind_tmp is not None:
            text_ref = webcface.text.Variant(
                webcface.field.Field(data, data.self_member_name), field_id
            )
            self._bind_tmp._state = text_ref
            self._text_ref = text_ref
            if self._init is not None and text_ref.try_get() is None:
                text_ref.set(self._init)
        self._data = data
        return self

    def __eq__(self, other) -> bool:
        """プロパティの比較

        :return: プロパティが全部等しければTrueになる
        """
        return (
            isinstance(other, ViewComponent)
            and self._type == other._type
            and self._text == other._text
            and (
                (self._on_click_func is None and other._on_click_func is None)
                or (
                    self._on_click_func is not None
                    and other._on_click_func is not None
                    and self._on_click_func._member == other._on_click_func._member
                    and self._on_click_func._field == other._on_click_func._field
                )
            )
            and (
                (self._text_ref is None and other._text_ref is None)
                or (
                    self._text_ref is not None
                    and other._text_ref is not None
                    and self._text_ref._member == other._text_ref._member
                    and self._text_ref._field == other._text_ref._field
                )
            )
            and self._text_color == other._text_color
            and self._bg_color == other._bg_color
            and self._min == other._min
            and self._max == other._max
            and self._step == other._step
            and self._option == other._option
        )

    def __ne__(self, other) -> bool:
        return not self == other

    @property
    def type(self) -> int:
        """コンポーネントの種類

        ViewComponentType Enumを使う
        """
        return self._type

    @property
    def text(self) -> str:
        """表示する文字列"""
        return self._text

    @property
    def on_click(self) -> Optional[webcface.func.Func]:
        """クリックしたときに呼び出す関数"""
        if self._on_click_func is not None:
            if self._data is None:
                raise RuntimeError("internal data not set")
            return webcface.func.Func(
                webcface.field.Field(
                    self._data, self._on_click_func._member, self._on_click_func._field
                )
            )
        return None

    @property
    def on_change(self) -> Optional[webcface.func.Func]:
        """値が変化したときに呼び出す関数
        (ver2.0〜)

        run_asyncの引数に変更後の値を入れて呼び出すことで、inputの値を変更する

        内部実装はon_clickと共通になっている
        """
        return self.on_click

    @property
    def bind(self) -> Optional[webcface.text.Variant]:
        """inputの現在の値を取得
        (ver2.0〜)

        viewを作成したときにbindしたかon_changeをセットしたかに関わらず、
        値の変更はbindではなくon_changeから行う
        """
        if self._text_ref is not None:
            if self._data is None:
                raise RuntimeError("internal data not set")
            return webcface.text.Variant(
                webcface.field.Field(
                    self._data, self._text_ref._member, self._text_ref._field
                )
            )
        return None

    @property
    def text_color(self) -> int:
        """文字の色

        ViewColor Enumを使う
        """
        return self._text_color

    @property
    def bg_color(self) -> int:
        """背景の色

        ViewColor Enumを使う
        """
        return self._bg_color

    @property
    def min(self) -> Optional[float]:
        """inputの最小値
        (ver2.0〜)
        """
        return self._min

    @property
    def max(self) -> Optional[float]:
        """inputの最大値
        (ver2.0〜)
        """
        return self._max

    @property
    def step(self) -> Optional[float]:
        """inputの刻み幅
        (ver2.0〜)
        """
        return self._step

    @property
    def option(self) -> List[Union[float, bool, str]]:
        """inputの選択肢
        (ver2.0〜)
        """
        return self._option


class View(webcface.field.Field):
    _components: List[Union[ViewComponent, str, bool, float, int]]
    _modified: bool

    def __init__(self, base: webcface.field.Field, field: str = "") -> None:
        """Viewを指すクラス

        このコンストラクタを直接使わず、
        Member.view(), Member.views(), Member.onViewEntry などを使うこと

        詳細は `Viewのドキュメント <https://na-trium-144.github.io/webcface/md_13__view.html>`_ を参照
        """
        super().__init__(
            base._data, base._member, field if field != "" else base._field
        )
        self._components = []
        self._modified = False

    @property
    def member(self) -> webcface.member.Member:
        """Memberを返す"""
        return webcface.member.Member(self)

    @property
    def name(self) -> str:
        """field名を返す"""
        return self._field

    def on_change(self, func: Callable) -> Callable:
        """値が変化したときのイベント
        (ver2.0〜)

        コールバックの引数にはViewオブジェクトが渡される。

        まだ値をリクエストされてなければ自動でリクエストされる
        """
        self.request()
        data = self._data_check()
        if self._member not in data.on_view_change:
            data.on_view_change[self._member] = {}
        data.on_view_change[self._member][self._field] = func
        return func

    def child(self, field: str) -> View:
        """子フィールドを返す

        :return: 「(thisのフィールド名).(子フィールド名)」をフィールド名とするView
        """
        return View(self, self._field + "." + field)

    def request(self) -> None:
        """値の受信をリクエストする"""
        req = self._data_check().view_store.add_req(self._member, self._field)
        if req > 0:
            self._data_check().queue_msg_req(
                [webcface.message.ViewReq.new(self._member, self._field, req)]
            )

    def try_get(self) -> Optional[List[ViewComponent]]:
        """ViewをlistまたはNoneで返す、まだリクエストされてなければ自動でリクエストされる"""
        self.request()
        v = self._data_check().view_store.get_recv(self._member, self._field)
        v2: Optional[List[ViewComponent]] = None
        if v is not None:
            v2 = [ViewComponent.from_base(vb, self._data) for vb in v]
        return v2

    def get(self) -> List[ViewComponent]:
        """Viewをlistで返す、まだリクエストされてなければ自動でリクエストされる"""
        v = self.try_get()
        return v if v is not None else []

    def exists(self) -> bool:
        """このフィールドにデータが存在すればtrue
        (ver2.0〜)

        try_get() などとは違って、実際のデータを受信しない。
        リクエストもしない。
        """
        return self._field in self._data_check().view_store.get_entry(self._member)

    def set(
        self, components: List[Union[ViewComponent, str, bool, SupportsFloat]]
    ) -> View:
        """Viewのリストをセットする"""
        data2 = []
        for c in components:
            if isinstance(c, ViewComponent):
                data2.append(c)
            elif isinstance(c, str):
                while "\n" in c:
                    s = c[: c.find("\n")]
                    data2.append(webcface.view_components.text(s))
                    data2.append(webcface.view_components.new_line())
                    c = c[c.find("\n") + 1 :]
                if c != "":
                    data2.append(webcface.view_components.text(c))
            else:
                data2.append(webcface.view_components.text(str(c)))
        for i, c in enumerate(data2):
            data2[i] = c.lock_tmp(self._set_check(), f"..v{self._field}.{i}")
        data = self._set_check()
        data.view_store.set_send(self._field, list(data2))
        on_change = data.on_view_change.get(self._member, {}).get(self._field)
        if on_change is not None:
            on_change(self)
        return self

    def __enter__(self) -> View:
        """with構文の最初で自動でinit()を呼ぶ"""
        self.init()
        return self

    def init(self) -> View:
        """このViewオブジェクトにaddした内容を初期化する"""
        self._components = []
        self._modified = True
        return self

    def __exit__(self, type, value, tb) -> None:
        """with構文の終わりに自動でsync()を呼ぶ"""
        self.sync()

    def sync(self) -> View:
        """Viewの内容をclientに反映し送信可能にする"""
        self._set_check()
        if self._modified:
            self.set(self._components)
            self._modified = False
        return self

    def add(self, *args: Union[ViewComponent, str, bool, SupportsFloat]) -> View:
        """コンポーネントを追加

        Viewオブジェクトが生成されて最初のaddのとき自動でinit()をする
        """
        for c in args:
            self._components.append(c)
        self._modified = True
        return self
