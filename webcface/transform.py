from typing import List, Tuple, Union, SupportsFloat, Optional
from enum import IntEnum
from collections.abc import Sequence
from webcface.typing import convertible_to_float
import webcface.transform_impl


class Point:
    """3次元or2次元の座標"""

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
        """Pointと比較した場合座標が一致すればTrue"""
        if isinstance(other, Transform):
            return False
        elif isinstance(other, Point):
            return self.pos == other.pos
        else:
            return False

    def __add__(self, other: "Point") -> "Point":
        if isinstance(other, Point):
            return Point([a + b for a, b in zip(self.pos, other.pos)])
        return NotImplemented

    def __iadd__(self, other: "Point") -> "Point":
        if isinstance(other, Point):
            self.set_pos([a + b for a, b in zip(self.pos, other.pos)])
            return self
        return NotImplemented

    def __sub__(self, other: "Point") -> "Point":
        if isinstance(other, Point):
            return Point([a - b for a, b in zip(self.pos, other.pos)])
        return NotImplemented

    def __isub__(self, other: "Point") -> "Point":
        if isinstance(other, Point):
            self.set_pos([a - b for a, b in zip(self.pos, other.pos)])
            return self
        return NotImplemented

    def __neg__(self) -> "Point":
        return Point([-a for a in self.pos])

    def __pos__(self) -> "Point":
        return Point(self.pos)

    def __mul__(self, other: SupportsFloat) -> "Point":
        return Point([a * float(other) for a in self.pos])

    def __rmul__(self, other: SupportsFloat) -> "Point":
        return Point([a * float(other) for a in self.pos])

    def __imul__(self, other: SupportsFloat) -> "Point":
        self.set_pos([a * float(other) for a in self.pos])
        return self

    def __div__(self, other: SupportsFloat) -> "Point":
        return Point([a / float(other) for a in self.pos])

    def __idiv__(self, other: SupportsFloat) -> "Point":
        self.set_pos([a / float(other) for a in self.pos])
        return self


class AxisSequence(IntEnum):
    """オイラー角の回転順序 (ver2.4〜)

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
    """3次元の回転 (ver2.4〜)

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
        """このコンストラクタではなくstaticメソッドを使うこと"""
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

        .. deprecated:: ver2.4
        """
        return self.rot_euler()

    def rot_euler(self, axis=AxisSequence.ZYX) -> Tuple[float, float, float]:
        """回転角をオイラー角として取得 (ver2.4〜)

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
        """回転角を回転行列として取得 (ver2.4〜)"""
        if self._rmat is None:
            assert (
                self._az is not None and self._ay is not None and self._ax is not None
            )
            self._rmat = webcface.transform_impl.euler_to_matrix(
                (self._az, self._ay, self._ax), AxisSequence.ZYX
            )
        return self._rmat

    def rot_quat(self) -> Tuple[float, float, float, float]:
        """回転角をクォータニオン(w, x, y, z)として取得 (ver2.4〜)"""
        return webcface.transform_impl.matrix_to_quaternion(self.rot_matrix())

    def rot_axis_angle(self) -> Tuple[Tuple[float, float, float], float]:
        """回転角を軸と角度((x, y, z), angle)として取得 (ver2.4〜)"""
        return webcface.transform_impl.quaternion_to_axis_angle(self.rot_quat())

    @staticmethod
    def from_euler(
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

    @staticmethod
    def from_matrix(rmat: Sequence[Sequence[SupportsFloat]]) -> "Rotation":
        """回転行列からRotationを作成

        :arg rmat: 回転行列
        """
        assert len(rmat) == 3, "Rotation matrix must be 3x3, got " + str(rmat)
        assert all(
            len(r) == 3 for r in rmat
        ), "Rotation matrix must be 3x3, got " + str(rmat)
        return Rotation(None, None, None, rmat)

    @staticmethod
    def from_quat(quat: Sequence[SupportsFloat]) -> "Rotation":
        """クォータニオンからRotationを作成

        :arg quat: クォータニオン (w, x, y, z)
        """
        assert len(quat) == 4, "Quaternion must be 4 dimensional, got " + str(quat)
        return Rotation.from_matrix(webcface.transform_impl.quaternion_to_matrix(quat))

    @staticmethod
    def from_axis_angle(
        axis: Sequence[SupportsFloat], angle: SupportsFloat
    ) -> "Rotation":
        """軸と角度からRotationを作成

        :arg axis: 軸
        :arg angle: 角度
        """
        assert len(axis) == 3, "Axis must be 3 dimensional, got " + str(axis)
        return Rotation.from_quat(
            webcface.transform_impl.axis_angle_to_quaternion(axis, angle)
        )


class Transform(Point, Rotation):
    """3次元の座標と回転

    内部ではx, y, zの座標とz-y-x系のオイラー角で保持している。
    """

    def __init__(
        self,
        pos: "Union[Point, Sequence[SupportsFloat]]",
        rot: "Rotation",
    ) -> None:
        if isinstance(pos, Point):
            Point.__init__(self, pos.pos)
        else:
            Point.__init__(self, pos)
        Rotation.__init__(self, rot._az, rot._ay, rot._ax, rot._rmat)

    def __eq__(self, other: object) -> bool:
        """Transformと比較した場合座標と回転が一致すればTrue"""
        if isinstance(other, Transform):
            return self._pos == other._pos and self._rot == other._rot
        else:
            return False


def identity() -> "Transform":
    return Transform([0, 0, 0], Rotation.from_euler([0, 0, 0]))
