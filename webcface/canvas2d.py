from typing import Optional, Callable, List, SupportsFloat, Union, Dict
import webcface.field
import webcface.canvas2d_base
import webcface.geometries
import webcface.client_data
import webcface.transform
import webcface.view_base
import webcface.temporal_component


class Canvas2DData:
    tmp_components: "List[webcface.temporal_component.TemporalComponent]"
    components: "Dict[str, webcface.canvas2d_base.Canvas2DComponentBase]"
    ids: List[str]
    width: float
    height: float

    def __init__(self, width: float, height: float) -> None:
        if width <= 0 or height <= 0:
            raise ValueError(f"Invalid Canvas2D size ({width} x {height})")
        self.tmp_components = []
        self.components = {}
        self.ids = []
        self.width = width
        self.height = height


class Canvas2DComponent(webcface.canvas2d_base.Canvas2DComponentBase):
    _data: Optional[webcface.client_data.ClientData]
    _id: str

    def __init__(
        self,
        base: "webcface.canvas2d_base.Canvas2DComponentBase",
        data: "Optional[webcface.client_data.ClientData]",
        id: str,
    ) -> None:
        super().__init__(
            base._type,
            base._origin_pos,
            base._origin_rot,
            base._color,
            base._fill,
            base._stroke_width,
            base._geometry_type,
            base._geometry_properties,
        )
        self._data = data
        self._id = id

    def __eq__(self, other) -> bool:
        """プロパティの比較 (ver3.0〜)

        :return: id以外のプロパティが全部等しければTrueになる
        """
        return isinstance(
            other, Canvas2DComponent
        ) and webcface.canvas2d_base.Canvas2DComponentBase.__eq__(self, other)

    def __ne__(self, other) -> bool:
        return not self == other

    @property
    def id(self) -> str:
        """要素のid (ver3.0〜)"""
        return self._id

    @property
    def type(self) -> int:
        """コンポーネントの種類

        Canvas2DComponentType Enumを使う
        """
        return self._type

    @property
    def origin(self) -> "webcface.transform.Transform":
        """表示する要素の移動"""
        return webcface.transform.Transform(self._origin_pos, self._origin_rot)

    @property
    def color(self) -> int:
        """色 (ViewColor)"""
        return self._color

    @property
    def fill(self) -> int:
        """塗りつぶしの色 (ViewColor)"""
        return self._fill

    @property
    def stroke_width(self) -> float:
        """線の太さ"""
        return self._stroke_width

    @property
    def geometry(self) -> "webcface.geometries.Geometry":
        """表示する図形"""
        return webcface.geometries.Geometry(
            self._geometry_type, self._geometry_properties
        )


class Canvas2D(webcface.field.Field):
    _c2data: "Optional[Canvas2DData]"
    _modified: bool

    def __init__(
        self,
        base: "webcface.field.Field",
        field: str = "",
        width: Optional[SupportsFloat] = None,
        height: Optional[SupportsFloat] = None,
    ) -> None:
        """Canvas2Dを指すクラス

        引数にwidthとheightを渡すとinitされる

        このコンストラクタを直接使わず、
        Member.canvas2d(), Member.canvas2d_entries(), Member.on_canvas2d_entry などを使うこと

        詳細は `Canvas2Dのドキュメント <https://na-trium-144.github.io/webcface/md_14__canvas2d.html>`_ を参照
        """
        super().__init__(
            base._data, base._member, field if field != "" else base._field
        )
        self._c2data = None
        self._modified = False
        if width is not None and height is not None:
            self.init(width, height)

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

        コールバックの引数にはCanvas2Dオブジェクトが渡される。

        まだ値をリクエストされてなければ自動でリクエストされる
        """
        self.request()
        data = self._data_check()
        if self._member not in data.on_canvas2d_change:
            data.on_canvas2d_change[self._member] = {}
        data.on_canvas2d_change[self._member][self._field] = func
        return func

    def child(self, field: str) -> "Canvas2D":
        """子フィールドを返す

        :return: 「(thisのフィールド名).(子フィールド名)」をフィールド名とするView
        """
        return Canvas2D(self, self._field + "." + field)

    def request(self) -> None:
        """値の受信をリクエストする"""
        req = self._data_check().canvas2d_store.add_req(self._member, self._field)
        if req > 0:
            self._data_check().queue_msg_req(
                [webcface.message.Canvas2DReq.new(self._member, self._field, req)]
            )

    def try_get(self) -> "Optional[List[Canvas2DComponent]]":
        """CanvasをlistまたはNoneで返す、まだリクエストされてなければ自動でリクエストされる"""
        self.request()
        v = self._data_check().canvas2d_store.get_recv(self._member, self._field)
        v2: Optional[List[Canvas2DComponent]] = None
        if v is not None:
            v2 = [
                Canvas2DComponent(v.components[v_id], self._data, v_id)
                for v_id in v.ids
            ]
        return v2

    def get(self) -> "List[Canvas2DComponent]":
        """Canvasをlistで返す、まだリクエストされてなければ自動でリクエストされる"""
        v = self.try_get()
        return v if v is not None else []

    def exists(self) -> bool:
        """このフィールドにデータが存在すればtrue
        (ver2.0〜)

        try_get() などとは違って、実際のデータを受信しない。
        リクエストもしない。
        """
        return self._field in self._data_check().canvas2d_store.get_entry(self._member)

    @property
    def width(self) -> float:
        """Canvasのサイズを返す、まだリクエストされてなければ自動でリクエストされる

        init()されている場合はその値を返す"""
        if self._c2data is not None:
            return self._c2data.width
        else:
            self.request()
            v = self._data_check().canvas2d_store.get_recv(self._member, self._field)
            if v is not None:
                return v.width
            else:
                return 0

    @property
    def height(self) -> float:
        """Canvasのサイズを返す、まだリクエストされてなければ自動でリクエストされる

        init()されている場合はその値を返す"""
        if self._c2data is not None:
            return self._c2data.height
        else:
            self.request()
            v = self._data_check().canvas2d_store.get_recv(self._member, self._field)
            if v is not None:
                return v.height
            else:
                return 0

    def __enter__(self) -> "Canvas2D":
        """with構文の最初でなにもしない"""
        return self

    def init(self, width: SupportsFloat, height: SupportsFloat) -> "Canvas2D":
        """このCanvas2Dオブジェクトにaddした内容を初期化する
        and Canvas2Dのサイズを指定する
        """
        self._c2data = Canvas2DData(float(width), float(height))
        self._modified = True
        return self

    def __exit__(self, type, value, tb) -> None:
        """with構文の終わりに自動でsync()を呼ぶ"""
        self.sync()

    def sync(self) -> "Canvas2D":
        """Viewの内容をclientに反映し送信可能にする"""
        self._set_check()
        if self._modified and self._c2data is not None:
            data = self._set_check()
            data_idx: Dict[int, int] = {}
            for c in self._c2data.tmp_components:
                idx = data_idx.get(c._canvas2d_type, 0)
                data_idx[c._canvas2d_type] = idx + 1
                c.lock_tmp(data, "c2", self._field, f"..{c._canvas2d_type}.{idx}")
                self._c2data.components[c.id] = c.to_canvas2d()
                self._c2data.ids.append(c.id)
            self._set_check().canvas2d_store.set_send(self._field, self._c2data)
            self._modified = False
        on_change = (
            self._data_check().on_canvas2d_change.get(self._member, {}).get(self._field)
        )
        if on_change is not None:
            on_change(self)
        return self

    def add(
        self,
        *args: Union[
            "webcface.temporal_component.TemporalComponent",
            "webcface.geometries.Geometry2D",
        ],
        **kwargs,
    ) -> "Canvas2D":
        """要素を追加

        初期化時またはinit()で事前にサイズを指定していなければエラー

        :arg args: 追加する要素
        (ver3.0〜:複数指定した場合すべて追加される。)
        :arg kwargs: (ver3.0〜) argsが初期化済みの要素でない場合、要素の初期化時に渡すオプション。
        詳細は TemporalComponent のコンストラクタを参照
        """
        if self._c2data is None:
            raise ValueError("Canvas2D not initialized")
        assert len(args) > 0, "no components given to Canvas2D.add()"
        for c in args:
            if isinstance(c, webcface.temporal_component.TemporalComponent):
                if len(kwargs) > 0:
                    raise ValueError(
                        f"kwargs is not allowed because {c} is already a component"
                    )
                self._c2data.tmp_components.append(c)
            elif isinstance(c, webcface.geometries.Geometry):
                self._c2data.tmp_components.append(
                    webcface.temporal_component.TemporalComponent(
                        canvas2d_type=webcface.canvas2d_base.Canvas2DComponentType.GEOMETRY,
                        geometry=c,
                        **kwargs,
                    )
                )
            else:
                raise ValueError(f"Invalid component {c}")
        self._modified = True
        return self
