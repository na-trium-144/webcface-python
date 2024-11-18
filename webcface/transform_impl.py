import math
from typing import Tuple, SupportsFloat, Sequence, List
import webcface.transform

# https://en.wikipedia.org/wiki/Euler_angles にあるものを写した

Vector3 = Tuple[float, float, float]
Matrix3 = Tuple[Vector3, Vector3, Vector3]


def euler_to_matrix(
    angles: Sequence[SupportsFloat], axis: "webcface.transform.AxisSequence"
) -> Matrix3:
    c0 = math.cos(float(angles[0]))
    c1 = math.cos(float(angles[1]))
    c2 = math.cos(float(angles[2]))
    s0 = math.sin(float(angles[0]))
    s1 = math.sin(float(angles[1]))
    s2 = math.sin(float(angles[2]))
    if axis == webcface.transform.AxisSequence.XZX:
        return (
            (c1, -c2 * s1, s1 * s2),
            (c0 * s1, c0 * c1 * c2 - s0 * s2, -c2 * s0 - c0 * c1 * s2),
            (s0 * s1, c0 * s2 + c1 * c2 * s0, c0 * c2 - c1 * s0 * s2),
        )
    if axis == webcface.transform.AxisSequence.XYX:
        return (
            (c1, s1 * s2, c2 * s1),
            (s0 * s1, c0 * c2 - c1 * s0 * s2, -c0 * s2 - c1 * c2 * s0),
            (-c0 * s1, c2 * s0 + c0 * c1 * s2, c0 * c1 * c2 - s0 * s2),
        )
    if axis == webcface.transform.AxisSequence.YXY:
        return (
            (c0 * c2 - c1 * s0 * s2, s0 * s1, c0 * s2 + c1 * c2 * s0),
            (s1 * s2, c1, -c2 * s1),
            (-c2 * s0 - c0 * c1 * s2, c0 * s1, c0 * c1 * c2 - s0 * s2),
        )
    if axis == webcface.transform.AxisSequence.YZY:
        return (
            (c0 * c1 * c2 - s0 * s2, -c0 * s1, c2 * s0 + c0 * c1 * s2),
            (c2 * s1, c1, s1 * s2),
            (-c0 * s2 - c1 * c2 * s0, s0 * s1, c0 * c2 - c1 * s0 * s2),
        )
    if axis == webcface.transform.AxisSequence.ZYZ:
        return (
            (c0 * c1 * c2 - s0 * s2, -c2 * s0 - c0 * c1 * s2, c0 * s1),
            (c0 * s2 + c1 * c2 * s0, c0 * c2 - c1 * s0 * s2, s0 * s1),
            (-c2 * s1, s1 * s2, c1),
        )
    if axis == webcface.transform.AxisSequence.ZXZ:
        return (
            (c0 * c2 - c1 * s0 * s2, -c0 * s2 - c1 * c2 * s0, s0 * s1),
            (c2 * s0 + c0 * c1 * s2, c0 * c1 * c2 - s0 * s2, -c0 * s1),
            (s1 * s2, c2 * s1, c1),
        )
    if axis == webcface.transform.AxisSequence.XZY:
        return (
            (c1 * c2, -s1, c1 * s2),
            (s0 * s2 + c0 * c2 * s1, c0 * c1, c0 * s1 * s2 - c2 * s0),
            (c2 * s0 * s1 - c0 * s2, c1 * s0, c0 * c2 + s0 * s1 * s2),
        )
    if axis == webcface.transform.AxisSequence.XYZ:
        return (
            (c1 * c2, -c1 * s2, s1),
            (c0 * s2 + c2 * s0 * s1, c0 * c2 - s0 * s1 * s2, -c1 * s0),
            (s0 * s2 - c0 * c2 * s1, c2 * s0 + c0 * s1 * s2, c0 * c1),
        )
    if axis == webcface.transform.AxisSequence.YXZ:
        return (
            (c0 * c2 + s0 * s1 * s2, c2 * s0 * s1 - c0 * s2, c1 * s0),
            (c1 * s2, c1 * c2, -s1),
            (c0 * s1 * s2 - c2 * s0, c0 * c2 * s1 + s0 * s2, c0 * c1),
        )
    if axis == webcface.transform.AxisSequence.YZX:
        return (
            (c0 * c1, s0 * s2 - c0 * c2 * s1, c2 * s0 + c0 * s1 * s2),
            (s1, c1 * c2, -c1 * s2),
            (-c1 * s0, c0 * s2 + c2 * s0 * s1, c0 * c2 - s0 * s1 * s2),
        )
    if axis == webcface.transform.AxisSequence.ZYX:
        return (
            (c0 * c1, c0 * s1 * s2 - c2 * s0, s0 * s2 + c0 * c2 * s1),
            (c1 * s0, c0 * c2 + s0 * s1 * s2, c2 * s0 * s1 - c0 * s2),
            (-s1, c1 * s2, c1 * c2),
        )
    if axis == webcface.transform.AxisSequence.ZXY:
        return (
            (c0 * c2 - s0 * s1 * s2, -c1 * s0, c0 * s2 + c2 * s0 * s1),
            (c2 * s0 + c0 * s1 * s2, c0 * c1, s0 * s2 - c0 * c2 * s1),
            (-c1 * s2, s1, c1 * c2),
        )
    raise ValueError("Invalid axis sequence")


# |cos(asin(x)) - 1| がだいたい1ε以下となるxを0とする
# sin = x, cos = 1 - x^2 / 2 で近似しちゃうと
# x * x / 2 < ε
# |x| < sqrt(2ε)


def is_zero(value: float) -> bool:
    sqrt_2_epsilon = 2.1073424255447e-08
    return value >= -sqrt_2_epsilon and value < sqrt_2_epsilon


# 精度やロバスト性を上げるため、asinやacosは使わないで計算する
# 計算式は使いまわす
# wikipediaの α,β,γ をここでは a,b,c と置いている


def matrix_to_proper_euler(
    rmat: Sequence[Sequence[SupportsFloat]], axis: "webcface.transform.AxisSequence"
) -> Vector3:
    if axis == webcface.transform.AxisSequence.XZX:
        cb = float(rmat[0][0])
        sa_sb = float(rmat[2][0])
        ca_sb = float(rmat[1][0])
        sc_sb = float(rmat[0][2])
        cc_sb = -float(rmat[0][1])
        sc_ca = float(rmat[2][1])
        cc_ca = float(rmat[2][2])
    elif axis == webcface.transform.AxisSequence.XYX:
        cb = float(rmat[0][0])
        sa_sb = float(rmat[1][0])
        ca_sb = -float(rmat[2][0])
        sc_sb = float(rmat[0][1])
        cc_sb = float(rmat[0][2])
        sc_ca = -float(rmat[1][2])
        cc_ca = float(rmat[1][1])
    elif axis == webcface.transform.AxisSequence.YXY:
        cb = float(rmat[1][1])
        sa_sb = float(rmat[0][1])
        ca_sb = float(rmat[2][1])
        sc_sb = float(rmat[1][0])
        cc_sb = -float(rmat[1][2])
        sc_ca = float(rmat[0][2])
        cc_ca = float(rmat[0][0])
    elif axis == webcface.transform.AxisSequence.YZY:
        cb = float(rmat[1][1])
        sa_sb = float(rmat[2][1])
        ca_sb = -float(rmat[0][1])
        sc_sb = float(rmat[1][2])
        cc_sb = float(rmat[1][0])
        sc_ca = -float(rmat[2][0])
        cc_ca = float(rmat[2][2])
    elif axis == webcface.transform.AxisSequence.ZYZ:
        cb = float(rmat[2][2])
        sa_sb = float(rmat[1][2])
        ca_sb = float(rmat[0][2])
        sc_sb = float(rmat[2][1])
        cc_sb = -float(rmat[2][0])
        sc_ca = float(rmat[1][0])
        cc_ca = float(rmat[1][1])
    elif axis == webcface.transform.AxisSequence.ZXZ:
        cb = float(rmat[2][2])
        sa_sb = float(rmat[0][2])
        ca_sb = -float(rmat[1][2])
        sc_sb = float(rmat[2][0])
        cc_sb = float(rmat[2][1])
        sc_ca = -float(rmat[0][1])
        cc_ca = float(rmat[0][0])
    else:
        raise ValueError("Invalid axis sequence")
    if (is_zero(sa_sb) and is_zero(ca_sb)) or (is_zero(sc_sb) and is_zero(cc_sb)):
        return (
            0,  # singularity: let sa=0, ca=1
            0 if cb >= 0 else -math.pi,  # sb = 0, cb = 1,-1
            math.atan2(sc_ca, cc_ca),
        )
    else:
        a = math.atan2(sa_sb, ca_sb)
        return (
            a,
            math.atan2(sa_sb * math.sin(a) + ca_sb * math.cos(a), cb),
            math.atan2(sc_sb, cc_sb),
        )


def matrix_to_tait_bryan_euler(
    rmat: Sequence[Sequence[SupportsFloat]], axis: "webcface.transform.AxisSequence"
) -> Vector3:
    if axis == webcface.transform.AxisSequence.XZY:
        sb = -float(rmat[0][1])
        sa_cb = float(rmat[2][1])
        ca_cb = float(rmat[1][1])
        sc_cb = float(rmat[0][2])
        cc_cb = float(rmat[0][0])
        sc_ca = -float(rmat[2][0])
        cc_ca = float(rmat[2][2])
    elif axis == webcface.transform.AxisSequence.XYZ:
        sb = float(rmat[0][2])
        sa_cb = -float(rmat[1][2])
        ca_cb = float(rmat[2][2])
        sc_cb = -float(rmat[0][1])
        cc_cb = float(rmat[0][0])
        sc_ca = float(rmat[1][0])
        cc_ca = float(rmat[1][1])
    elif axis == webcface.transform.AxisSequence.YXZ:
        sb = -float(rmat[1][2])
        sa_cb = float(rmat[0][2])
        ca_cb = float(rmat[2][2])
        sc_cb = float(rmat[1][0])
        cc_cb = float(rmat[1][1])
        sc_ca = -float(rmat[0][1])
        cc_ca = float(rmat[0][0])
    elif axis == webcface.transform.AxisSequence.YZX:
        sb = float(rmat[1][0])
        sa_cb = -float(rmat[2][0])
        ca_cb = float(rmat[0][0])
        sc_cb = -float(rmat[1][2])
        cc_cb = float(rmat[1][1])
        sc_ca = float(rmat[2][1])
        cc_ca = float(rmat[2][2])
    elif axis == webcface.transform.AxisSequence.ZYX:
        sb = -float(rmat[2][0])
        sa_cb = float(rmat[1][0])
        ca_cb = float(rmat[0][0])
        sc_cb = float(rmat[2][1])
        cc_cb = float(rmat[2][2])
        sc_ca = -float(rmat[1][2])
        cc_ca = float(rmat[1][1])
    elif axis == webcface.transform.AxisSequence.ZXY:
        sb = float(rmat[2][1])
        sa_cb = -float(rmat[0][1])
        ca_cb = float(rmat[1][1])
        sc_cb = -float(rmat[2][0])
        cc_cb = float(rmat[2][2])
        sc_ca = float(rmat[0][2])
        cc_ca = float(rmat[0][0])
    else:
        raise ValueError("Invalid axis sequence")
    if (is_zero(sa_cb) and is_zero(ca_cb)) or (is_zero(sc_cb) and is_zero(cc_cb)):
        return (
            0,  # singularity: let sa=0, ca=1
            math.pi / 2 if sb >= 0 else -math.pi / 2,  # sb = 1,-1  cb = 0
            math.atan2(sc_ca, cc_ca),
        )
    else:
        a = math.atan2(sa_cb, ca_cb)
        return (
            a,
            math.atan2(sb, sa_cb * math.sin(a) + ca_cb * math.cos(a)),
            math.atan2(sc_cb, cc_cb),
        )


def matrix_to_euler(
    rmat: Sequence[Sequence[SupportsFloat]], axis: "webcface.transform.AxisSequence"
) -> Vector3:
    if axis >= 0 and axis < 6:
        return matrix_to_proper_euler(rmat, axis)
    if axis >= 6 and axis < 12:
        return matrix_to_tait_bryan_euler(rmat, axis)
    raise ValueError("Invalid axis sequence")


def quaternion_to_matrix(quat: Sequence[SupportsFloat]) -> Matrix3:
    w = float(quat[0])
    x = float(quat[1])
    y = float(quat[2])
    z = float(quat[3])
    return (
        (1 - 2 * y * y - 2 * z * z, 2 * x * y - 2 * z * w, 2 * x * z + 2 * y * w),
        (2 * x * y + 2 * z * w, 1 - 2 * x * x - 2 * z * z, 2 * y * z - 2 * x * w),
        (2 * x * z - 2 * y * w, 2 * y * z + 2 * x * w, 1 - 2 * x * x - 2 * y * y),
    )


def matrix_to_quaternion(
    rmat: Sequence[Sequence[SupportsFloat]],
) -> Tuple[float, float, float, float]:
    trace = float(rmat[0][0]) + float(rmat[1][1]) + float(rmat[2][2])
    if trace > 0:
        s = math.sqrt(trace + 1.0) * 2
        w = 0.25 * s
        x = (float(rmat[2][1]) - float(rmat[1][2])) / s
        y = (float(rmat[0][2]) - float(rmat[2][0])) / s
        z = (float(rmat[1][0]) - float(rmat[0][1])) / s
    elif float(rmat[0][0]) > float(rmat[1][1]) and float(rmat[0][0]) > float(
        rmat[2][2]
    ):
        s = (
            math.sqrt(1.0 + float(rmat[0][0]) - float(rmat[1][1]) - float(rmat[2][2]))
            * 2
        )
        w = (float(rmat[2][1]) - float(rmat[1][2])) / s
        x = 0.25 * s
        y = (float(rmat[0][1]) + float(rmat[1][0])) / s
        z = (float(rmat[0][2]) + float(rmat[2][0])) / s
    elif float(rmat[1][1]) > float(rmat[2][2]):
        s = (
            math.sqrt(1.0 + float(rmat[1][1]) - float(rmat[0][0]) - float(rmat[2][2]))
            * 2
        )
        w = (float(rmat[0][2]) - float(rmat[2][0])) / s
        x = (float(rmat[0][1]) + float(rmat[1][0])) / s
        y = 0.25 * s
        z = (float(rmat[1][2]) + float(rmat[2][1])) / s
    else:
        s = (
            math.sqrt(1.0 + float(rmat[2][2]) - float(rmat[0][0]) - float(rmat[1][1]))
            * 2
        )
        w = (float(rmat[1][0]) - float(rmat[0][1])) / s
        x = (float(rmat[0][2]) + float(rmat[2][0])) / s
        y = (float(rmat[1][2]) + float(rmat[2][1])) / s
        z = 0.25 * s
    return (w, x, y, z)


def axis_angle_to_quaternion(
    axis: Sequence[SupportsFloat], angle: SupportsFloat
) -> Tuple[float, float, float, float]:
    half_angle = float(angle) / 2
    s = math.sin(half_angle)
    norm = math.hypot(float(axis[0]), float(axis[1]), float(axis[2]))
    if norm == 0:
        return (1, 0, 0, 0)
    else:
        return (
            math.cos(half_angle),
            float(axis[0]) / norm * s,
            float(axis[1]) / norm * s,
            float(axis[2]) / norm * s,
        )


def quaternion_to_axis_angle(
    quat: Sequence[SupportsFloat],
) -> Tuple[Tuple[float, float, float], float]:
    w = float(quat[0])
    x = float(quat[1])
    y = float(quat[2])
    z = float(quat[3])
    angle = 2 * math.acos(w)
    return ((x, y, z), angle)


def apply_rot_point(left: Matrix3, right: Vector3) -> Vector3:
    new_pos: List[float] = [0, 0, 0]
    for i in range(3):
        new_pos[i] = (
            left[i][0] * right[0] + left[i][1] * right[1] + left[i][2] * right[2]
        )
    return (new_pos[0], new_pos[1], new_pos[2])


def apply_rot_rot(left: Matrix3, right: Matrix3) -> Matrix3:
    new_pos: List[List[float]] = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
    for i in range(3):
        for j in range(3):
            new_pos[i][j] = (
                left[i][0] * right[0][j]
                + left[i][1] * right[1][j]
                + left[i][2] * right[2][j]
            )
    return (
        (new_pos[0][0], new_pos[0][1], new_pos[0][2]),
        (new_pos[1][0], new_pos[1][1], new_pos[1][2]),
        (new_pos[2][0], new_pos[2][1], new_pos[2][2]),
    )


def inverse_matrix(mat: Matrix3) -> Matrix3:
    return (
        (mat[0][0], mat[1][0], mat[2][0]),
        (mat[0][1], mat[1][1], mat[2][1]),
        (mat[0][2], mat[1][2], mat[2][2]),
    )


def inverse_transform(pos: Vector3, mat: Matrix3) -> Tuple[Vector3, Matrix3]:
    inv = inverse_matrix(mat)
    return (apply_rot_point(inv, pos), inv)
