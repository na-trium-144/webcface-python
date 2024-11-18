from typing import Optional, Callable, List, Dict, Union
import webcface.field
import webcface.canvas3d_base
import webcface.geometries
import webcface.client_data
import webcface.transform
import webcface.view_base


class Canvas3DData:
    tmp_components: "List[webcface.temporal_component.TemporalComponent]"
    components: "Dict[str, webcface.canvas3d_base.Canvas3DComponentBase]"
    ids: List[str]

    def __init__(self) -> None:
        self.tmp_components = []
        self.components = {}
        self.ids = []


class Canvas3DComponent(webcface.canvas3d_base.Canvas3DComponentBase):
    _data: "Optional[webcface.client_data.ClientData]"
    _id: str

    def __init__(
        self,
        base: "webcface.canvas3d_base.Canvas3DComponentBase",
        data: "Optional[webcface.client_data.ClientData]",
        id: str,
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
        self._id = id

    def __eq__(self, other) -> bool:
        """プロパティの比較 (ver3.0〜)

        :return: id以外のプロパティが全部等しければTrueになる
        """
        return isinstance(
            other, Canvas3DComponent
        ) and webcface.canvas3d_base.Canvas3DComponentBase.__eq__(self, other)

    def __ne__(self, other) -> bool:
        return not self == other

    @property
    def id(self) -> str:
        """要素のid (ver3.0〜)"""
        return self._id

    @property
    def type(self) -> int:
        """コンポーネントの種類

        Canvas3DComponentType Enumを使う
        """
        return self._type

    @property
    def origin(self) -> "webcface.transform.Transform":
        """表示する要素の移動"""
        return webcface.transform.Transform(
            self._origin_pos, webcface.transform.rot_from_euler(self._origin_rot)
        )

    @property
    def color(self) -> int:
        """色 (ViewColor)"""
        return self._color

    @property
    def geometry(self) -> "Optional[webcface.geometries.Geometry]":
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
    _c3data: "Optional[Canvas3DData]"
    _modified: bool

    def __init__(
        self,
        base: "webcface.field.Field",
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

        コールバックの引数にはCanvas3Dオブジェクトが渡される。

        まだ値をリクエストされてなければ自動でリクエストされる
        """
        self.request()
        data = self._data_check()
        if self._member not in data.on_canvas3d_change:
            data.on_canvas3d_change[self._member] = {}
        data.on_canvas3d_change[self._member][self._field] = func
        return func

    def child(self, field: str) -> "Canvas3D":
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
            v2 = [
                Canvas3DComponent(v.components[v_id], self._data, v_id)
                for v_id in v.ids
            ]
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

    def __enter__(self) -> "Canvas3D":
        """with構文の最初でinit"""
        self.init()
        return self

    def init(self) -> "Canvas3D":
        """このCanvas3Dオブジェクトにaddした内容を初期化する"""
        self._c3data = Canvas3DData()
        self._modified = True
        return self

    def __exit__(self, type, value, tb) -> None:
        """with構文の終わりに自動でsync()を呼ぶ"""
        self.sync()

    def sync(self) -> "Canvas3D":
        """Viewの内容をclientに反映し送信可能にする"""
        self._set_check()
        if self._modified and self._c3data is not None:
            data = self._set_check()
            data_idx: Dict[int, int] = {}
            for c in self._c3data.tmp_components:
                idx = data_idx.get(c._canvas3d_type, 0)
                data_idx[c._canvas3d_type] = idx + 1
                c.lock_tmp(data, "c3", self._field, f"..{c._canvas3d_type}.{idx}")
                self._c3data.components[c.id] = c.to_canvas3d()
                self._c3data.ids.append(c.id)
            data.canvas3d_store.set_send(self._field, self._c3data)
            self._modified = False
        on_change = (
            self._data_check().on_canvas3d_change.get(self._member, {}).get(self._field)
        )
        if on_change is not None:
            on_change(self)
        return self

    def add(
        self,
        *args: Union[
            "webcface.temporal_component.TemporalComponent",
            "webcface.geometries.Geometry3D",
        ],
        **kwargs,
    ) -> "Canvas3D":
        """要素を追加

        :arg args: (ver3.0〜) 追加する要素 (複数指定した場合すべて追加される。)
        :arg kwargs: (ver3.0〜) argsが初期化済みの要素でない場合、要素の初期化時に渡すオプション。
        詳細は TemporalComponent のコンストラクタを参照
        """
        if self._c3data is None:
            self.init()
        assert self._c3data is not None
        assert len(args) > 0, "no components given to Canvas3D.add()"
        for c in args:
            if isinstance(c, webcface.temporal_component.TemporalComponent):
                if len(kwargs) > 0:
                    raise ValueError(
                        f"kwargs is not allowed because {c} is already a component"
                    )
                self._c3data.tmp_components.append(c)
            elif isinstance(c, webcface.geometries.Geometry):
                self._c3data.tmp_components.append(
                    webcface.temporal_component.TemporalComponent(
                        canvas3d_type=webcface.canvas3d_base.Canvas3DComponentType.GEOMETRY,
                        geometry=c,
                        **kwargs,
                    )
                )
            else:
                raise ValueError(f"Invalid component {c}")
        self._modified = True
        return self

    def add_geometry(
        self,
        geometry: "webcface.geometries.Geometry3D",
        origin: "Optional[webcface.transform.Transform]" = None,
        color: int = webcface.view_base.ViewColor.INHERIT,
    ) -> "Canvas3D":
        """Geometryを追加

        .. deprecated:: ver3.0
        """
        return self.add(geometry, origin=origin, color=color)
