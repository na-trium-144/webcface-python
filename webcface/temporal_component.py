from typing import Optional, List, Callable, SupportsFloat, Union, Sequence, Tuple, Dict
from webcface.typing import convertible_to_float
import webcface.client_data
import webcface.text
import webcface.field
import webcface.view_base


class TemporalComponent:
    _data: "Optional[webcface.client_data.ClientData]"
    _on_click_func_tmp: Optional[Callable]
    _bind_tmp: "Optional[webcface.text.InputRef]"
    _init: Optional[Union[float, bool, str]]

    # view
    _view_type: int
    _text: str
    _on_click_func: "Optional[webcface.field.FieldBase]"
    _text_ref: "Optional[webcface.field.FieldBase]"
    _text_color: int
    _bg_color: int
    _min: Optional[float]
    _max: Optional[float]
    _step: Optional[float]
    _option: List[Union[float, bool, str]]

    # canvas2d
    _canvas2d_type: int
    _origin: "webcface.transform.Transform"
    # _color: int  -> text_color
    # _fill: int  -> bg_color
    _stroke_width: float
    _geometry: "webcface.geometries.Geometry"

    # canvas3d
    _canvas3d_type: int
    # _origin
    # _color: int
    # _geometry_type: Optional[int]
    # _geometry_properties: List[float]
    # _field_member: Optional[str]
    # _field_field: Optional[str]
    _field: "Optional[webcface.field.FieldBase]"
    _angles: Dict[str, float]

    def __init__(
        self,
        view_type: int = 0,
        canvas2d_type: int = 0,
        canvas3d_type: int = 0,
        text: str = "",
        on_click: "Optional[Union[webcface.field.FieldBase, Callable]]" = None,
        text_color: Optional[int] = None,
        bg_color: Optional[int] = None,
        on_change: "Optional[Union[webcface.func.Func, Callable]]" = None,
        bind: "Optional[webcface.text.InputRef]" = None,
        min: Optional[SupportsFloat] = None,
        max: Optional[SupportsFloat] = None,
        step: Optional[SupportsFloat] = None,
        option: Optional[Sequence[Union[SupportsFloat, bool, str]]] = None,
        init: Optional[Union[SupportsFloat, bool, str]] = None,
        origin: Optional[
            Union[
                "webcface.transform.Point",
                Sequence[SupportsFloat],
                "webcface.transform.Transform",
                Tuple[
                    Union["webcface.transform.Point", Sequence[SupportsFloat]],
                    "webcface.transform.Rotation",
                ],
            ]
        ] = None,
        color: Optional[int] = None,
        fill: Optional[int] = None,
        stroke_width: Optional[SupportsFloat] = None,
        text_size: Optional[SupportsFloat] = None,
        geometry: Optional["webcface.geometries.Geometry"] = None,
        # robot_model: Optional[webcface.robot_model.RobotModel] = None,
        angles: Optional[Dict[str, SupportsFloat]] = None,
    ) -> None:
        """View, Canvas2D, Canvas3Dの要素を初期化するコンストラクタ。(ver3.0〜)

        非対応の引数はadd時に無視される。

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
        :arg origin: 要素の位置を移動する
        :arg color: 要素の色 (text_colorと同じ)
        :arg fill: 要素の塗りつぶし色 (bg_colorと同じ)
        :arg stroke_width: 線の太さ
        :arg text_size: (ver3.0〜) 文字サイズ (内部的にはstroke_widthと同一)
        :arg geometry: 表示する図形
        """
        self._type = type
        self._text = text
        self._on_click_func = None
        self._text_ref = None
        self._text_color = 0
        if text_color is not None:
            self._text_color = text_color
        elif color is not None:
            self._text_color = color
        self._bg_color = 0
        if bg_color is not None:
            self._bg_color = bg_color
        elif fill is not None:
            self._bg_color = fill
        self._min = None if min is None else float(min)
        self._max = None if max is None else float(max)
        self._step = None if step is None else float(step)
        self._option = []
        if option is not None:
            for op in option:
                if isinstance(op, bool):
                    self._option.append(op)
                elif convertible_to_float(init):
                    self._option.append(float(op))
                else:
                    self._option.append(str(op))
        self._stroke_width = 0
        if stroke_width is not None:
            self._stroke_width = float(stroke_width)
        elif text_size is not None:
            self._stroke_width = float(text_size)
        self._origin = webcface.transform.identity()
        if isinstance(origin, webcface.transform.Point):
            self._origin = webcface.transform.translation(origin)
        elif isinstance(origin, webcface.transform.Transform):
            self._origin = origin
        elif origin is not None:
            if all(convertible_to_float(v) for v in origin):
                self._origin = webcface.transform.translation(origin)  # type:ignore
            elif len(origin) == 2:
                self._origin = webcface.transform.Transform(*origin)
            else:
                raise ValueError("Invalid argument for origin: " + str(origin))
        if geometry is None:
            self._geometry = webcface.geometries.Geometry(0, [])
        else:
            self._geometry = geometry
        self._angles = {}
        if angles is not None:
            for k, v in angles.items():
                self._angles[k] = float(v)
        self._field = None  # todo

        self._data = None
        self._on_click_func_tmp = None
        if init is None:
            self._init = None
        elif isinstance(init, bool):
            self._init = init
        elif convertible_to_float(init):
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
        if (
            isinstance(self._field, webcface.field.Field)
            and self._field._data is not None
        ):
            self._data = self._field._data

    def lock_tmp(self, data: "webcface.client_data.ClientData", field_id: str) -> None:
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

    def to_view(self) -> "webcface.view_base.ViewComponentBase":
        return webcface.view_base.ViewComponentBase(
            self._type,
            self._text,
            self._on_click_func,
            self._text_ref,
            self._text_color,
            self._bg_color,
            self._min,
            self._max,
            self._step,
            self._option,
        )
