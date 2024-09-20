from __future__ import annotations
from typing import Optional, Callable, List, SupportsFloat
from copy import deepcopy
import webcface.field
import webcface.canvas2d_base
import webcface.geometries
import webcface.client_data
import webcface.transform
import webcface.view_components


class Canvas2DComponent(webcface.canvas2d_base.Canvas2DComponentBase):
    # _data: Optional[webcface.client_data.ClientData]

    def __init__(
        self,
        base: webcface.canvas2d_base.Canvas2DComponentBase,
        # data: Optional[webcface.client_data.ClientData]
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

    @property
    def type(self) -> int:
        """コンポーネントの種類

        Canvas2DComponentType Enumを使う
        """
        return self._type

    @property
    def origin(self) -> webcface.transform.Transform:
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
    def geometry(self) -> webcface.geometries.Geometry:
        """表示する図形"""
        return webcface.geometries.Geometry(
            self._geometry_type, self._geometry_properties
        )


class Canvas2D(webcface.field.Field):
    _c2data: Optional[webcface.canvas2d_base.Canvas2DData]
    _modified: bool

    def __init__(
        self,
        base: webcface.field.Field,
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

        コールバックの引数にはCanvas2Dオブジェクトが渡される。

        まだ値をリクエストされてなければ自動でリクエストされる
        """
        self.request()
        data = self._data_check()
        if self._member not in data.on_canvas2d_change:
            data.on_canvas2d_change[self._member] = {}
        data.on_canvas2d_change[self._member][self._field] = func
        return func

    def child(self, field: str) -> Canvas2D:
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

    def try_get(self) -> Optional[List[Canvas2DComponent]]:
        """CanvasをlistまたはNoneで返す、まだリクエストされてなければ自動でリクエストされる"""
        self.request()
        v = self._data_check().canvas2d_store.get_recv(self._member, self._field)
        v2: Optional[List[Canvas2DComponent]] = None
        if v is not None:
            v2 = [Canvas2DComponent(vb) for vb in v.components]
        return v2

    def get(self) -> List[Canvas2DComponent]:
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

    def __enter__(self) -> Canvas2D:
        """with構文の最初でなにもしない"""
        return self

    def init(self, width: SupportsFloat, height: SupportsFloat) -> Canvas2D:
        """このCanvas2Dオブジェクトにaddした内容を初期化する
        and Canvas2Dのサイズを指定する
        """
        self._c2data = webcface.canvas2d_base.Canvas2DData(float(width), float(height))
        self._modified = True
        return self

    def __exit__(self, type, value, tb) -> None:
        """with構文の終わりに自動でsync()を呼ぶ"""
        self.sync()

    def sync(self) -> Canvas2D:
        """Viewの内容をclientに反映し送信可能にする"""
        self._set_check()
        if self._modified and self._c2data is not None:
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
        geometry: webcface.geometries.Geometry2D,
        origin: Optional[webcface.transform.Transform] = None,
        color: int = webcface.view_components.ViewColor.INHERIT,
        fill: int = webcface.view_components.ViewColor.INHERIT,
        stroke_width: SupportsFloat = 1,
    ) -> Canvas2D:
        """コンポーネントを追加

        初期化時またはinit()で事前にサイズを指定していなければエラー
        """
        if self._c2data is None:
            raise ValueError("Canvas2D not initialized")
        if origin is None:
            origin = webcface.transform.Transform([0, 0], 0)
        self._c2data.components.append(
            webcface.canvas2d_base.Canvas2DComponentBase(
                webcface.canvas2d_base.Canvas2DComponentType.GEOMETRY,
                list(origin.pos[0:2]),
                origin.rot[0],
                color,
                fill,
                float(stroke_width),
                geometry.type,
                geometry._properties,
            )
        )
        self._modified = True
        return self
