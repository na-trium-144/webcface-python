from __future__ import annotations
from typing import List, Tuple, Union, SupportsFloat

ConvertibleToPoint = Union[
    List[SupportsFloat],
    Tuple[SupportsFloat, SupportsFloat],
    Tuple[SupportsFloat, SupportsFloat, SupportsFloat],
]
ConvertibleToRotation = Union[
    SupportsFloat,
    List[SupportsFloat],
    Tuple[SupportsFloat, SupportsFloat, SupportsFloat],
]
ConvertibleToTransform = Tuple[ConvertibleToPoint, ConvertibleToRotation]


class Point:
    """3次元or2次元の座標"""

    _pos: Tuple[float, float, float]

    def __init__(
        self,
        pos: ConvertibleToPoint,
    ) -> None:
        """引数についてはset_pos()を参照"""
        self.set_pos(pos)

    @property
    def pos(self) -> Tuple[float, float, float]:
        """座標を返す

        2次元の場合は pos[0:2] を使う
        """
        return self._pos

    @pos.setter
    def pos(self, new_pos: ConvertibleToPoint) -> None:
        """座標をセット

        mypyが型に関してエラーを出す場合はset_pos()を使うと良いかも
        """
        self.set_pos(new_pos)

    def set_pos(self, new_pos: ConvertibleToPoint) -> None:
        """座標をセット

        :arg new_pos: 座標 2次元の場合 :code:`[float, float]`, 3次元の場合 :code:`[float, float, float]` など
        """
        if len(new_pos) == 2:
            self._pos = (float(new_pos[0]), float(new_pos[1]), 0.0)
        elif len(new_pos) == 3:
            self._pos = (float(new_pos[0]), float(new_pos[1]), float(new_pos[2]))
        else:
            raise ValueError(f"invalid pos format (len = {len(new_pos)})")

    def __eq__(self, other: object) -> bool:
        """Pointと比較した場合座標が一致すればTrue"""
        if isinstance(other, Transform):
            return False
        elif isinstance(other, Point):
            return self._pos == other._pos
        else:
            return False

    def __add__(self, other: Point) -> Point:
        if isinstance(other, Point):
            return Point([a + b for a, b in zip(self.pos, other.pos)])
        return NotImplemented

    def __iadd__(self, other: Point) -> Point:
        if isinstance(other, Point):
            self._pos = [a + b for a, b in zip(self.pos, other.pos)]
            return self
        return NotImplemented

    def __sub__(self, other: Point) -> Point:
        if isinstance(other, Point):
            return Point([a - b for a, b in zip(self.pos, other.pos)])
        return NotImplemented

    def __isub__(self, other: Point) -> Point:
        if isinstance(other, Point):
            self._pos = [a - b for a, b in zip(self.pos, other.pos)]
            return self
        return NotImplemented

    def __neg__(self) -> Point:
        return Point([-a for a in self.pos])

    def __pos__(self) -> Point:
        return Point(self.pos)

    def __mul__(self, other: SupportsFloat) -> Point:
        return Point([a * float(other) for a in self.pos])

    def __rmul__(self, other: SupportsFloat) -> Point:
        return Point([a * float(other) for a in self.pos])

    def __imul__(self, other: SupportsFloat) -> Point:
        self._pos = [a * float(other) for a in self.pos]
        return self

    def __div__(self, other: SupportsFloat) -> Point:
        return Point([a / float(other) for a in self.pos])

    def __idiv__(self, other: SupportsFloat) -> Point:
        self._pos = [a / float(other) for a in self.pos]
        return self


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

    @property
    def rot(self) -> Tuple[float, float, float]:
        """回転角を取得

        2次元の場合は rot[0] を使う
        """
        return self._rot

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
        if isinstance(new_rot, SupportsFloat):
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
