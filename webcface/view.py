from typing import Optional, List, Callable, SupportsFloat, Union, Dict
from copy import deepcopy
import webcface.field
import webcface.text
import webcface.view_base
import webcface.components
import webcface.client_data
import webcface.func
import webcface.temporal_component
from webcface.typing import convertible_to_float


class ViewData:
    tmp_components: "List[webcface.temporal_component.TemporalComponent]"
    components: "Dict[str, webcface.view_base.ViewComponentBase]"
    ids: List[str]

    def __init__(self) -> None:
        self.tmp_components = []
        self.components = {}
        self.ids = []


class ViewComponent(webcface.view_base.ViewComponentBase):
    _data: "Optional[webcface.client_data.ClientData]"
    _id: str

    def __init__(
        self,
        base: "webcface.view_base.ViewComponentBase",
        data: "Optional[webcface.client_data.ClientData]",
        id: str,
    ) -> None:
        super().__init__(
            type=base._type,
            text=base._text,
            on_click=base._on_click_func,
            text_ref=base._text_ref,
            text_color=base._text_color,
            bg_color=base._bg_color,
            min=base._min,
            max=base._max,
            step=base._step,
            option=base._option,
        )
        self._data = data
        self._id = id

    def __eq__(self, other) -> bool:
        """プロパティの比較

        :return: id以外のプロパティが全部等しければTrueになる
        """
        return isinstance(
            other, ViewComponent
        ) and webcface.view_base.ViewComponentBase.__eq__(self, other)

    def __ne__(self, other) -> bool:
        return not self == other

    @property
    def id(self) -> str:
        """要素のid (ver3.0〜)"""
        return self._id

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
    def on_click(self) -> "Optional[webcface.func.Func]":
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
    def on_change(self) -> "Optional[webcface.func.Func]":
        """値が変化したときに呼び出す関数
        (ver2.0〜)

        run_asyncの引数に変更後の値を入れて呼び出すことで、inputの値を変更する

        内部実装はon_clickと共通になっている
        """
        return self.on_click

    @property
    def bind(self) -> "Optional[webcface.text.Variant]":
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
    _vdata: "Optional[ViewData]"
    _modified: bool

    def __init__(self, base: "webcface.field.Field", field: str = "") -> None:
        """Viewを指すクラス

        このコンストラクタを直接使わず、
        Member.view(), Member.views(), Member.onViewEntry などを使うこと

        詳細は `Viewのドキュメント <https://na-trium-144.github.io/webcface/md_13__view.html>`_ を参照
        """
        super().__init__(
            base._data, base._member, field if field != "" else base._field
        )
        self._vdata = None
        self._modified = False

    @property
    def member(self) -> "webcface.member.Member":
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

    def child(self, field: str) -> "View":
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
            v2 = [ViewComponent(v.components[v_id], self._data, v_id) for v_id in v.ids]
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
        self,
        components: List[
            Union[
                "webcface.temporal_component.TemporalComponent",
                str,
                bool,
                SupportsFloat,
            ]
        ],
    ) -> "View":
        """Viewのリストをセットする

        .. deprecated:: ver3.0
        """
        for c in components:
            self.add(c)
        return self

    def __enter__(self) -> "View":
        """with構文の最初で自動でinit()を呼ぶ"""
        self.init()
        return self

    def init(self) -> "View":
        """このViewオブジェクトにaddした内容を初期化する"""
        self._vdata = ViewData()
        self._modified = True
        return self

    def __exit__(self, type, value, tb) -> None:
        """with構文の終わりに自動でsync()を呼ぶ"""
        self.sync()

    def sync(self) -> "View":
        """Viewの内容をclientに反映し送信可能にする"""
        self._set_check()
        if self._modified and self._vdata is not None:
            data = self._set_check()
            self._vdata.components = {}
            self._vdata.ids = []
            data_idx: Dict[int, int] = {}
            for c in self._vdata.tmp_components:
                idx = data_idx.get(c._view_type, 0)
                data_idx[c._view_type] = idx + 1
                c.lock_tmp(data, "v", self._field, f"..{c._view_type}.{idx}")
                self._vdata.components[c.id] = c.to_view()
                self._vdata.ids.append(c.id)
            data.view_store.set_send(self._field, self._vdata)
            on_change = data.on_view_change.get(self._member, {}).get(self._field)
            if on_change is not None:
                on_change(self)
            self._modified = False
        return self

    def add(
        self,
        *args: Union[
            "webcface.temporal_component.TemporalComponent", str, bool, SupportsFloat
        ],
        **kwargs,
    ) -> "View":
        """Viewに要素を追加

        :arg args: 追加する要素
        複数指定した場合すべて追加される。
        :arg kwargs: (ver3.0〜) argsが初期化済みの要素でない場合、要素の初期化時に渡すオプション。
        詳細は TemporalComponent のコンストラクタを参照
        """
        if self._vdata is None:
            self.init()
        assert self._vdata is not None
        assert len(args) > 0, "no components given to View.add()"
        for c in args:
            if isinstance(c, webcface.temporal_component.TemporalComponent):
                if len(kwargs) > 0:
                    raise ValueError(
                        f"kwargs is not allowed because {c} is already a component"
                    )
                self._vdata.tmp_components.append(c)
            elif isinstance(c, str):
                while "\n" in c:
                    s = c[: c.find("\n")]
                    self._vdata.tmp_components.append(
                        webcface.components.text(s, **kwargs)
                    )
                    self._vdata.tmp_components.append(
                        webcface.components.new_line(**kwargs)
                    )
                    c = c[c.find("\n") + 1 :]
                if c != "":
                    self._vdata.tmp_components.append(
                        webcface.components.text(c, **kwargs)
                    )
            else:
                self._vdata.tmp_components.append(
                    webcface.components.text(str(c), **kwargs)
                )
        self._modified = True
        return self
