from typing import List, Tuple, Union, SupportsFloat, Optional, Sequence
from enum import IntEnum
from webcface.typing import convertible_to_float, is_float_sequence
import webcface.transform_impl


class Point:
    """3次元or2次元の座標

    手動でコンストラクタを呼んでもいいが、
    PointをうけとるAPIは基本的に Sequence[SupportsFloat] を受け付け、
    内部でPointに変換される。
    """

    _x: float
    _y: float
    _z: float

    def __init__(
        self,
        pos: Sequence[SupportsFloat],
    ) -> None:
        """座標を初期化

        :arg pos: 座標
        2次元の場合 :code:`[float, float]`,
        3次元の場合 :code:`[float, float, float]` など
        """
        assert len(pos) in (2, 3), "Point must be (x, y) or (x, y, z), got " + str(pos)
        self._x = float(pos[0])
        self._y = float(pos[1])
        self._z = float(pos[2]) if len(pos) == 3 else 0.0

    @property
    def pos(self) -> Tuple[float, float, float]:
        """座標を返す

        2次元の場合は pos[0:2] を使う
        """
        return (self._x, self._y, self._z)

    @pos.setter
    def pos(self, new_pos: Sequence[SupportsFloat]) -> None:
        """座標をセット

        mypyが型に関してエラーを出す場合はset_pos()を使うと良いかも
        """
        self.set_pos(new_pos)

    def set_pos(self, pos: Sequence[SupportsFloat]) -> None:
        """座標をセット

        :arg pos: 座標
        2次元の場合 :code:`[float, float]`,
        3次元の場合 :code:`[float, float, float]` など
        """
        assert len(pos) in (2, 3), "Point must be (x, y) or (x, y, z), got " + str(pos)
        self._x = float(pos[0])
        self._y = float(pos[1])
        self._z = float(pos[2]) if len(pos) == 3 else 0.0

    def __eq__(self, other: object) -> bool:
        """Pointと比較した場合座標の差が 1e-8 未満ならTrue

        (ver3.0〜) Transformとは比較できない
        """
        if isinstance(other, Transform):
            raise TypeError("Transform can't be compared with Point")
        elif isinstance(other, Point):
            return (
                abs(self._x - other._x) < 1e-8
                and abs(self._y - other._y) < 1e-8
                and abs(self._z - other._z) < 1e-8
            )
        else:
            return NotImplemented

    def __ne__(self, other: object) -> bool:
        return not self == other

    def __add__(self, other: "Point") -> "Point":
        if isinstance(other, (Transform, Rotation)):
            raise TypeError("Transform or Rotation can't be added to Point")
        if isinstance(other, Point):
            return Point([a + b for a, b in zip(self.pos, other.pos)])
        return NotImplemented

    def __iadd__(self, other: "Point") -> "Point":
        if isinstance(other, (Transform, Rotation)):
            raise TypeError("Transform or Rotation can't be added to Point")
        if isinstance(other, Point):
            self.set_pos([a + b for a, b in zip(self.pos, other.pos)])
            return self
        return NotImplemented

    def __sub__(self, other: "Point") -> "Point":
        if isinstance(other, (Transform, Rotation)):
            raise TypeError("Transform or Rotation can't be subtracted from Point")
        if isinstance(other, Point):
            return Point([a - b for a, b in zip(self.pos, other.pos)])
        return NotImplemented

    def __isub__(self, other: "Point") -> "Point":
        if isinstance(other, (Transform, Rotation)):
            raise TypeError("Transform or Rotation can't be subtracted to Point")
        if isinstance(other, Point):
            self.set_pos([a - b for a, b in zip(self.pos, other.pos)])
            return self
        return NotImplemented

    def __neg__(self) -> "Point":
        return Point([-a for a in self.pos])

    def __pos__(self) -> "Point":
        return Point(self.pos)

    def __mul__(self, other: SupportsFloat) -> "Point":
        if isinstance(other, (Transform, Rotation, Point)):
            raise TypeError(
                "Transform, Rotation or Point can't be multiplied to Point from right"
            )
        return Point([a * float(other) for a in self.pos])

    def __rmul__(self, other: SupportsFloat) -> "Point":
        if isinstance(other, (Transform, Rotation, Point)):
            return NotImplemented  # should be defined in the other class
        return Point([a * float(other) for a in self.pos])

    def __imul__(self, other: SupportsFloat) -> "Point":
        if isinstance(other, (Transform, Rotation, Point)):
            raise TypeError(
                "Transform, Rotation or Point can't be multiplied to Point from right"
            )
        self.set_pos([a * float(other) for a in self.pos])
        return self

    def __div__(self, other: SupportsFloat) -> "Point":
        if isinstance(other, (Transform, Rotation, Point)):
            raise TypeError("Transform, Rotation or Point can't be divided from Point")
        return Point([a / float(other) for a in self.pos])

    def __idiv__(self, other: SupportsFloat) -> "Point":
        if isinstance(other, (Transform, Rotation, Point)):
            raise TypeError("Transform, Rotation or Point can't be multiplied to Point")
        self.set_pos([a / float(other) for a in self.pos])
        return self


class AxisSequence(IntEnum):
    """オイラー角の回転順序 (ver3.0〜)

    * 右手系の座標系で、
    内的回転(intrinsic rotation)でz軸,y軸,x軸の順に回転させる系
    = 外的回転(extrinsic rotation)でX軸,Y軸,Z軸の順に回転させる系
    = 回転行列がZ(α)Y(β)X(γ)と表される系
    を、 AxisSequence::ZYX と表記する。
    * ver2.3までの実装はすべてZYXで、現在もWebCFaceの内部表現は基本的にZYXの系である。
    * またWebCFaceのインタフェースでオイラー角の回転角を指定する場合、
    軸の指定順は内的回転を指す。(AxisSequenceにおける左から右の並び順と一致。)
    """

    ZXZ = 0
    XYX = 1
    YZY = 2
    ZYZ = 3
    XZX = 4
    YXY = 5
    XYZ = 6
    YZX = 7
    ZXY = 8
    XZY = 9
    ZYX = 10
    YXZ = 11


class Rotation:
    """3次元の回転 (ver3.0〜)

    * 内部ではz-y-x系のオイラー角または3x3回転行列で保持している。
    * 送受信時にはすべてこのzyxのオイラー角に変換される。
    * 2次元の回転を表すのにも使われ、
    その場合オイラー角 rot() の最初の要素(=z軸周りの回転)を使って回転を表し、
    残りの要素(x,y軸周りの回転)を0とする。
    """

    _az: Optional[float]
    _ay: Optional[float]
    _ax: Optional[float]
    _rmat: Optional[
        Tuple[
            Tuple[float, float, float],
            Tuple[float, float, float],
            Tuple[float, float, float],
        ]
    ]

    def __init__(self, az, ay, ax, rmat):
        """このコンストラクタではなく、rot_from_* 関数を使うこと"""
        if az is None and ay is None and ax is None:
            assert rmat is not None
            self._rmat = tuple(tuple(float(v) for v in r) for r in rmat)
            self._az = None
            self._ay = None
            self._ax = None
        else:
            assert rmat is None
            assert az is not None and ay is not None and ax is not None
            self._az = float(az)
            self._ay = float(ay)
            self._ax = float(ax)
            self._rmat = None

    @property
    def rot(self) -> Tuple[float, float, float]:
        """回転角を取得

        2次元の場合は rot[0] を使う

        .. deprecated:: ver3.0
        """
        return self.rot_euler()

    def rot_2d(self) -> float:
        """2次元の回転角を取得 (ver3.0〜)"""
        return self.rot_euler()[0]

    def rot_euler(self, axis=AxisSequence.ZYX) -> Tuple[float, float, float]:
        """回転角をオイラー角として取得 (ver3.0〜)

        :arg axis: オイラー角の回転順序
        """
        if axis == AxisSequence.ZYX:
            if self._az is None or self._ay is None or self._ax is None:
                assert self._rmat is not None
                (self._az, self._ay, self._ax) = (
                    webcface.transform_impl.matrix_to_euler(self._rmat, axis)
                )
            return (self._az, self._ay, self._ax)
        else:
            return webcface.transform_impl.matrix_to_euler(self.rot_matrix(), axis)

    def rot_matrix(
        self,
    ) -> Tuple[
        Tuple[float, float, float],
        Tuple[float, float, float],
        Tuple[float, float, float],
    ]:
        """回転角を回転行列として取得 (ver3.0〜)"""
        if self._rmat is None:
            assert (
                self._az is not None and self._ay is not None and self._ax is not None
            )
            self._rmat = webcface.transform_impl.euler_to_matrix(
                (self._az, self._ay, self._ax), AxisSequence.ZYX
            )
        return self._rmat

    def rot_quat(self) -> Tuple[float, float, float, float]:
        """回転角をクォータニオン(w, x, y, z)として取得 (ver3.0〜)"""
        return webcface.transform_impl.matrix_to_quaternion(self.rot_matrix())

    def rot_axis_angle(self) -> Tuple[Tuple[float, float, float], float]:
        """回転角を軸と角度((x, y, z), angle)として取得 (ver3.0〜)"""
        return webcface.transform_impl.quaternion_to_axis_angle(self.rot_quat())

    def __eq__(self, other: object) -> bool:
        """Rotationと比較した場合回転行列の各要素の差が 1e-8 未満ならTrue

        Transformとも比較できる
        """
        if isinstance(other, Transform):
            return other == Transform(self)
        elif isinstance(other, Rotation):
            return all(
                all(abs(a - b) < 1e-8 for a, b in zip(ra, rb))
                for ra, rb in zip(self.rot_matrix(), other.rot_matrix())
            )
        else:
            return NotImplemented

    def __ne__(self, other: object) -> bool:
        return not self == other

    def applied_to_point(
        self, other: Union["Point", Sequence[SupportsFloat]]
    ) -> "Point":
        """Point を回転させた結果を返す

        :arg other: 回転させる対象
        """
        if not isinstance(other, Point):
            other = Point(other)
        return Point(
            webcface.transform_impl.apply_rot_point(self.rot_matrix(), other.pos)
        )

    def applied_to_rotation(self, other: "Rotation") -> "Rotation":
        """Rotation を回転させた結果を返す

        :arg other: 回転させる対象
        """
        return Rotation(
            None,
            None,
            None,
            webcface.transform_impl.apply_rot_rot(
                self.rot_matrix(), other.rot_matrix()
            ),
        )

    def applied_to_transform(self, other: "Transform") -> "Transform":
        """Transform を回転させた結果を返す

        :arg other: 回転させる対象
        """
        return Transform(
            self.applied_to_point(other._point),
            self.applied_to_rotation(other._rotation),
        )

    def __mul__(
        self, other: Union["Point", "Rotation", "Transform"]
    ) -> Union["Point", "Rotation", "Transform"]:
        if isinstance(other, Transform):
            return self.applied_to_transform(other)
        if isinstance(other, Point):
            return self.applied_to_point(other)
        if isinstance(other, Rotation):
            return self.applied_to_rotation(other)
        return NotImplemented

    def __imul__(self, other: "Rotation") -> "Rotation":
        if isinstance(other, Transform):
            raise TypeError("Rotation * Transform is not Rotation")
        elif isinstance(other, Point):
            raise TypeError("Rotation * Point is not Rotation")
        elif isinstance(other, Rotation):
            result = self.applied_to_rotation(other)
        else:
            return TypeError("Rotation can't be multiplied to " + str(type(other)))
        self._az = None
        self._ay = None
        self._ax = None
        self._rmat = result._rmat
        return self

    def inversed(self) -> "Rotation":
        """逆回転を取得"""
        return Rotation(
            None,
            None,
            None,
            webcface.transform_impl.inverse_matrix(self.rot_matrix()),
        )


def rot_from_euler(
    angles: Sequence[SupportsFloat], axis=AxisSequence.ZYX
) -> "Rotation":
    """オイラー角からRotationを作成

    :arg angles: オイラー角
    :arg axis: オイラー角の回転順序
    """
    assert len(angles) == 3, "Euler angle must be 3 dimensional, got " + str(angles)
    if axis == AxisSequence.ZYX:
        return Rotation(angles[0], angles[1], angles[2], None)
    else:
        return Rotation(
            None, None, None, webcface.transform_impl.euler_to_matrix(angles, axis)
        )


def rot_from_matrix(rmat: Sequence[Sequence[SupportsFloat]]) -> "Rotation":
    """回転行列からRotationを作成

    :arg rmat: 回転行列
    """
    assert len(rmat) == 3, "Rotation matrix must be 3x3, got " + str(rmat)
    assert all(len(r) == 3 for r in rmat), "Rotation matrix must be 3x3, got " + str(
        rmat
    )
    return Rotation(None, None, None, rmat)


def rot_from_quat(quat: Sequence[SupportsFloat]) -> "Rotation":
    """クォータニオンからRotationを作成

    :arg quat: クォータニオン (w, x, y, z)
    """
    assert len(quat) == 4, "Quaternion must be 4 dimensional, got " + str(quat)
    return rot_from_matrix(webcface.transform_impl.quaternion_to_matrix(quat))


def rot_from_axis_angle(
    axis: Sequence[SupportsFloat], angle: SupportsFloat
) -> "Rotation":
    """軸と角度からRotationを作成

    :arg axis: 軸
    :arg angle: 角度
    """
    assert len(axis) == 3, "Axis must be 3 dimensional, got " + str(axis)
    return rot_from_quat(webcface.transform_impl.axis_angle_to_quaternion(axis, angle))


def rot_2d(angle: SupportsFloat) -> "Rotation":
    """2次元の回転を作成 (ver3.0〜)

    rot_z() と同じ。

    :arg angle: 回転角
    """
    return Rotation(angle, 0, 0, None)


def rot_z(angle: SupportsFloat) -> "Rotation":
    """z軸周りの回転を作成 (ver3.0〜)

    :arg angle: 回転角
    """
    return Rotation(angle, 0, 0, None)


def rot_y(angle: SupportsFloat) -> "Rotation":
    """y軸周りの回転を作成 (ver3.0〜)

    :arg angle: 回転角
    """
    return Rotation(0, angle, 0, None)


def rot_x(angle: SupportsFloat) -> "Rotation":
    """x軸周りの回転を作成 (ver3.0〜)

    :arg angle: 回転角
    """
    return Rotation(0, 0, angle, None)


class Transform:
    """3次元の座標と回転

    内部ではx, y, zの座標とz-y-x系のオイラー角で保持している。

    手動でコンストラクタを呼んでもいいが、
    TransformをうけとるAPIは基本的にPointとRotationのタプルを受け付け、
    内部でTransformに変換される。

    平行移動のみの場合は translation() を使用する。
    回転のみの場合はRotationだけ渡せば直接Transformに変換される

    ver3.0〜 Pointを継承せず別のクラスとしての実装に変更
    """

    _point: "Point"
    _rotation: "Rotation"

    def __init__(
        self,
        arg1: Union[
            "Point",
            Sequence[SupportsFloat],
            "Rotation",
        ],
        arg2: Optional[Union["Rotation", SupportsFloat]] = None,
    ) -> None:
        if isinstance(arg1, Rotation):
            self._point = Point([0, 0, 0])
            self._rotation = Rotation(arg1._az, arg1._ay, arg1._ax, arg1._rmat)
        else:
            assert (
                arg2 is not None
            ), "Rotation must be given, use translation() for translation only"
            if isinstance(arg2, Rotation):
                self._rotation = Rotation(arg2._az, arg2._ay, arg2._ax, arg2._rmat)
            else:
                self._rotation = Rotation(arg2, 0, 0, None)
            if isinstance(arg1, Point):
                self._point = Point(arg1.pos)
            else:
                self._point = Point(arg1)

    def __eq__(self, other: object) -> bool:
        """Transformと比較した場合座標と回転がそれぞれ 1e-8 未満の差ならTrue

        (ver3.0〜) Pointとは比較できないが、Rotationとは比較できる
        """
        if isinstance(other, Transform):
            return self._point == other._point and self._rotation == other._rotation
        elif isinstance(other, Rotation):
            return self == Transform(other)
        elif isinstance(other, Point):
            raise TypeError("Point can't be compared with Transform")
        else:
            return NotImplemented

    def __ne__(self, other: object) -> bool:
        return not self == other

    @property
    def pos(self) -> Tuple[float, float, float]:
        """座標を返す

        2次元の場合は pos[0:2] を使う
        """
        return self._point.pos

    @property
    def rot(self) -> Tuple[float, float, float]:
        """回転角を取得

        2次元の場合は rot[0] を使う

        .. deprecated:: ver3.0
        """
        return self.rot_euler()

    def rot_euler(self, axis=AxisSequence.ZYX) -> Tuple[float, float, float]:
        """回転角をオイラー角として取得 (ver3.0〜)

        :arg axis: オイラー角の回転順序
        """
        return self._rotation.rot_euler(axis)

    def rot_matrix(
        self,
    ) -> Tuple[
        Tuple[float, float, float],
        Tuple[float, float, float],
        Tuple[float, float, float],
    ]:
        """回転角を回転行列として取得 (ver3.0〜)"""
        return self._rotation.rot_matrix()

    def rot_quat(self) -> Tuple[float, float, float, float]:
        """回転角をクォータニオン(w, x, y, z)として取得 (ver3.0〜)"""
        return self._rotation.rot_quat()

    def rot_axis_angle(self) -> Tuple[Tuple[float, float, float], float]:
        """回転角を軸と角度((x, y, z), angle)として取得 (ver3.0〜)"""
        return self._rotation.rot_axis_angle()

    def applied_to_point(
        self, other: Union["Point", Sequence[SupportsFloat]]
    ) -> "Point":
        """Point を回転+平行移動させた結果を返す

        :arg other: 変換する対象
        """
        if not isinstance(other, Point):
            other = Point(other)
        return self._rotation.applied_to_point(other) + self._point

    def applied_to_rotation(self, other: "Rotation") -> "Transform":
        """Rotation を回転+平行移動させた結果を返す

        :arg other: 変換する対象
        :return: 返り値はRotationではなくTransform。 applied_to_transformと同じ結果になる
        """
        return self.applied_to_transform(Transform(other))

    def applied_to_transform(self, other: "Transform") -> "Transform":
        """Transform を回転+平行移動させた結果を返す

        :arg other: 変換する対象対象
        """
        return Transform(
            self._rotation.applied_to_point(other._point) + self._point,
            self._rotation.applied_to_rotation(other._rotation),
        )

    def __mul__(
        self, other: Union["Point", "Rotation", "Transform"]
    ) -> Union["Point", "Transform"]:
        if isinstance(other, Transform):
            return self.applied_to_transform(other)
        if isinstance(other, Point):
            return self.applied_to_point(other)
        if isinstance(other, Rotation):
            return self.applied_to_rotation(other)
        return NotImplemented

    def __imul__(self, other: Union["Rotation", "Transform"]) -> "Transform":
        if isinstance(other, Transform):
            result = self.applied_to_transform(other)
        elif isinstance(other, Rotation):
            result = self.applied_to_rotation(other)
        elif isinstance(other, Point):
            raise TypeError("Transform * Point is not Transform")
        else:
            return TypeError("Transform can't be multiplied to " + str(type(other)))
        self._point = result._point
        self._rotation = result._rotation
        return self

    def inversed(self) -> "Transform":
        """逆変換を取得 (ver3.0〜)"""
        pos, mat = webcface.transform_impl.inverse_transform(
            self.pos, self.rot_matrix()
        )
        return Transform(pos, rot_from_matrix(mat))


def identity() -> "Transform":
    """なにもしないTransformを作成"""
    return Transform([0, 0, 0], rot_from_euler([0, 0, 0]))


def translation(pos: Union["Point", Sequence[SupportsFloat]]) -> "Transform":
    """平行移動のみをするTransformを作成 (ver3.0〜)"""
    return Transform(pos, rot_from_euler([0, 0, 0]))


def convert_to_transform(
    origin: Union[
        "webcface.transform.Point",
        Sequence[SupportsFloat],
        "webcface.transform.Transform",
        "webcface.transform.Rotation",
        Tuple[
            Union["webcface.transform.Point", Sequence[SupportsFloat]],
            Union["webcface.transform.Rotation", SupportsFloat],
        ],
    ]
) -> "Transform":
    if isinstance(origin, webcface.transform.Transform):
        return origin
    if isinstance(origin, webcface.transform.Point):
        return webcface.transform.translation(origin)
    if isinstance(origin, webcface.transform.Rotation):
        return webcface.transform.Transform(origin)
    if is_float_sequence(origin):
        return webcface.transform.translation(origin)  # type:ignore
    return webcface.transform.Transform(*origin)
