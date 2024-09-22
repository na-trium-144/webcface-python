from __future__ import annotations
from typing import Optional, Callable, List
from copy import deepcopy
import webcface.field
import webcface.canvas3d_base
import webcface.geometries
import webcface.client_data
import webcface.transform
import webcface.view_components


class Canvas3DComponent(webcface.canvas3d_base.Canvas3DComponentBase):
    _data: Optional[webcface.client_data.ClientData]

    def __init__(
        self,
        base: webcface.canvas3d_base.Canvas3DComponentBase,
        data: Optional[webcface.client_data.ClientData],
    ) -> None:
        super().__init__(
            base._type,
            base._origin_pos,
            base._origin_rot,
            base._color,
            base._geometry_type,
            base._geometry_properties,
            base._field_member,
            base._field_field,
            base._angles,
        )
        self._data = data

    @property
    def type(self) -> int:
        """コンポーネントの種類

        Canvas3DComponentType Enumを使う
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
    def geometry(self) -> Optional[webcface.geometries.Geometry]:
        """表示する図形"""
        if self._geometry_type is None:
            return None
        return webcface.geometries.Geometry(
            self._geometry_type, self._geometry_properties
        )

    # @property
    # def robot_model(self) -> Optional[webcface.robot_model.RobotModel]
    #     pass


class Canvas3D(webcface.field.Field):
    _c3data: Optional[List[webcface.canvas3d_base.Canvas3DComponentBase]]
    _modified: bool

    def __init__(
        self,
        base: webcface.field.Field,
        field: str = "",
    ) -> None:
        """Canvas3Dを指すクラス

        このコンストラクタを直接使わず、
        Member.canvas3d(), Member.canvas3d_entries(), Member.on_canvas3d_entry などを使うこと

        詳細は `Canvas3Dのドキュメント <https://na-trium-144.github.io/webcface/md_20__canvas3d.html>`_ を参照
        """
        super().__init__(
            base._data, base._member, field if field != "" else base._field
        )
        self._c3data = None
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

        コールバックの引数にはCanvas3Dオブジェクトが渡される。

        まだ値をリクエストされてなければ自動でリクエストされる
        """
        self.request()
        data = self._data_check()
        if self._member not in data.on_canvas3d_change:
            data.on_canvas3d_change[self._member] = {}
        data.on_canvas3d_change[self._member][self._field] = func
        return func

    def child(self, field: str) -> Canvas3D:
        """子フィールドを返す

        :return: 「(thisのフィールド名).(子フィールド名)」をフィールド名とするView
        """
        return Canvas3D(self, self._field + "." + field)

    def request(self) -> None:
        """値の受信をリクエストする"""
        req = self._data_check().canvas3d_store.add_req(self._member, self._field)
        if req > 0:
            self._data_check().queue_msg_req(
                [webcface.message.Canvas3DReq.new(self._member, self._field, req)]
            )

    def try_get(self) -> Optional[List[Canvas3DComponent]]:
        """CanvasをlistまたはNoneで返す、まだリクエストされてなければ自動でリクエストされる"""
        self.request()
        v = self._data_check().canvas3d_store.get_recv(self._member, self._field)
        v2: Optional[List[Canvas3DComponent]] = None
        if v is not None:
            v2 = [Canvas3DComponent(vb, self._data) for vb in v]
        return v2

    def get(self) -> List[Canvas3DComponent]:
        """Canvasをlistで返す、まだリクエストされてなければ自動でリクエストされる"""
        v = self.try_get()
        return v if v is not None else []

    def exists(self) -> bool:
        """このフィールドにデータが存在すればtrue
        (ver2.0〜)

        try_get() などとは違って、実際のデータを受信しない。
        リクエストもしない。
        """
        return self._field in self._data_check().canvas3d_store.get_entry(self._member)

    def __enter__(self) -> Canvas3D:
        """with構文の最初でinit"""
        self.init()
        return self

    def init(self) -> Canvas3D:
        """このCanvas3Dオブジェクトにaddした内容を初期化する"""
        self._c3data = []
        self._modified = True
        return self

    def __exit__(self, type, value, tb) -> None:
        """with構文の終わりに自動でsync()を呼ぶ"""
        self.sync()

    def sync(self) -> Canvas3D:
        """Viewの内容をclientに反映し送信可能にする"""
        self._set_check()
        if self._modified and self._c3data is not None:
            self._set_check().canvas3d_store.set_send(self._field, self._c3data)
            self._modified = False
        on_change = (
            self._data_check().on_canvas3d_change.get(self._member, {}).get(self._field)
        )
        if on_change is not None:
            on_change(self)
        return self

    def add(self, *args, **kwargs) -> Canvas3D:
        """要素を追加

        引数は add_geometry() にそのまま渡される
        """
        if (args and isinstance(args[0], webcface.geometries.Geometry)) or (
            "geometry" in kwargs
        ):
            self.add_geometry(*args, **kwargs)
        else:
            raise ValueError("Invalid argument type in Canvas3D.add")
        return self

    def add_geometry(
        self,
        geometry: webcface.geometries.Geometry3D,
        origin: Optional[webcface.transform.Transform] = None,
        color: int = webcface.view_components.ViewColor.INHERIT,
    ) -> Canvas3D:
        """Geometryを追加"""
        if self._c3data is None:
            self.init()
        if origin is None:
            origin = webcface.transform.Transform([0, 0], 0)
        self._c3data.append(
            webcface.canvas3d_base.Canvas3DComponentBase(
                webcface.canvas3d_base.Canvas3DComponentType.GEOMETRY,
                list(origin.pos),
                list(origin.rot),
                color,
                geometry.type,
                geometry._properties,
                None,
                None,
                None,
            )
        )
        self._modified = True
        return self
