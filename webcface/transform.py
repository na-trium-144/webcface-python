from typing import List, Tuple, Union, SupportsFloat, Optional
from enum import Enum
from collections.abc import Sequence
from webcface.typing import convertible_to_float


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


class AxisSequence(Enum):
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
        """
        return (self._az, self._ay, self._ax)

    @staticmethod
    def from_euler(angles: Sequence[SupportsFloat], axis: AxisSequence) -> "Rotation":
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


class Transform(Point):
    """3次元の座標と回転

    内部ではx, y, zの座標とz-y-x系のオイラー角で保持している。
    """

    _rot: Tuple[float, float, float]

    def __init__(
        self,
        pos: ConvertibleToPoint,
        rot: ConvertibleToRotation,
    ) -> None:
        """引数についてはset_pos(), set_rot()を参照"""
        super().__init__(pos)
        self.set_rot(rot)


    @rot.setter
    def rot(self, new_rot: ConvertibleToRotation) -> None:
        """回転角をセット

        mypyが型に関してエラーを出す場合はset_rot()を使うと良いかも
        """
        self.set_rot(new_rot)

    def set_rot(self, new_rot: ConvertibleToRotation) -> None:
        """回転角をセット

        :arg new_rot: 座標 2次元の場合 :code:`float`, 3次元の場合 :code:`[float, float, float]` など
        """
        if convertible_to_float(new_rot):
            self._rot = (float(new_rot), 0.0, 0.0)
        elif len(new_rot) == 3:
            self._rot = (float(new_rot[0]), float(new_rot[1]), float(new_rot[2]))
        else:
            raise ValueError(f"invalid pos format (len = {len(new_rot)})")

    def __eq__(self, other: object) -> bool:
        """Transformと比較した場合座標と回転が一致すればTrue"""
        if isinstance(other, Transform):
            return self._pos == other._pos and self._rot == other._rot
        else:
            return False


def identity() -> Transform:
    return Transform([0, 0, 0], [0, 0, 0])
