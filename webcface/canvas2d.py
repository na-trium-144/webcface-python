from __future__ import annotations
from typing import Optional, Callable, List
from copy import deepcopy
import blinker
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
    _components: List[webcface.canvas2d_base.Canvas2DComponentBase]
    _width: float
    _height: float
    _modified: bool

    def __init__(self, base: webcface.field.Field, field: str = "") -> None:
        """Canvas2Dを指すクラス

        このコンストラクタを直接使わず、
        Member.canvas2d(), Member.canvas2d_entries(), Member.on_canvas2d_entry などを使うこと

        詳細は `Canvas2Dのドキュメント <https://na-trium-144.github.io/webcface/md_14__canvas2d.html>`_ を参照
        """
        super().__init__(
            base._data, base._member, field if field != "" else base._field
        )
        self._components = []
        self._modified = False
        self._width = 0.0
        self._height = 0.0

    @property
    def member(self) -> webcface.member.Member:
        """Memberを返す"""
        return webcface.member.Member(self)

    @property
    def name(self) -> str:
        """field名を返す"""
        return self._field

    @property
    def signal(self) -> blinker.NamedSignal:
        """値が変化したときのイベント

        コールバックの引数にはViewオブジェクトが渡される。

        まだリクエストされてなければ自動でリクエストする。
        """
        self.request()
        return self._data_check().signal("canvas2d_change", self._member, self._field)

    def child(self, field: str) -> Canvas2D:
        """子フィールドを返す

        :return: 「(thisのフィールド名).(子フィールド名)」をフィールド名とするView
        """
        return Canvas2D(self, self._field + "." + field)

    def request(self) -> None:
        """値の受信をリクエストする"""
        req = self._data_check().canvas2d_store.add_req(self._member, self._field)
        if req > 0:
            self._data_check().queue_msg(
                [webcface.message.Canvas2DReq.new(self._member, self._field, req)]
            )

    def try_get(self) -> Optional[List[Canvas2DComponent]]:
        """ViewをlistまたはNoneで返す、まだリクエストされてなければ自動でリクエストされる"""
        self.request()
        v = self._data_check().canvas2d_store.get_recv(self._member, self._field)
        v2: Optional[List[Canvas2DComponent]] = None
        if v is not None:
            v2 = [Canvas2DComponent(vb) for vb in v]
        return v2

    def get(self) -> List[Canvas2DComponent]:
        """Viewをlistで返す、まだリクエストされてなければ自動でリクエストされる"""
        v = self.try_get()
        return v if v is not None else []

    def _set(
        self, components: List[webcface.canvas2d_base.Canvas2DComponentBase]
    ) -> Canvas2D:
        self._set_check().canvas2d_store.set_send(self._field, components)
        self.signal.send(self)
        return self

    def __enter__(self) -> Canvas2D:
        """with構文の最初で自動でinit()を呼ぶ"""
        self.init()
        return self

    def init(self, width: int | float, height: int | float) -> Canvas2D:
        """このViewオブジェクトにaddした内容を初期化する"""
        self._components = []
        self._width = float(width)
        self._height = float(height)
        self._modified = True
        return self

    def __exit__(self, type, value, tb) -> None:
        """with構文の終わりに自動でsync()を呼ぶ"""
        self.sync()

    def sync(self) -> Canvas2D:
        """Viewの内容をclientに反映し送信可能にする"""
        self._set_check()
        if self._modified:
            self._set(self._components)
            self._modified = False
        return self

    def add(
        self,
        geometry: webcface.geometries.Geometry2D,
        origin: Optional[webcface.transform.Transform] = None,
        color: int = webcface.view_components.ViewColor.INHERIT,
        fill: int = webcface.view_components.ViewColor.INHERIT,
        stroke_width: int | float = 1,
    ) -> Canvas2D:
        """コンポーネントを追加

        事前にinit()でサイズを指定していなければエラー
        """
        if self._width <= 0 or self._height <= 0:
            raise ValueError(f"Invalid canvas2d size ({self._width} x {self._height})")
        if origin is None:
            origin = webcface.transform.Transform([0, 0], 0)
        self._components.append(
            webcface.canvas2d_base.Canvas2DComponentBase(
                webcface.canvas2d_base.Canvas2DComponentType.GEOMETRY,
                list(origin.pos[0:2]),
                origin.rot[0],
                color,
                fill,
                stroke_width,
                geometry.type,
                geometry._properties,
            )
        )
        self._modified = True
        return self
