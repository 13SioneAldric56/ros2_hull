"""Map DDM360B / ESP32 gx_output frame into ROS REP-103 imu_link (X forward, Y left, Z up)."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Literal


def _remap_vector(
    values: tuple[float, float, float],
    remap: tuple[int, int, int],
    sign: tuple[float, float, float],
) -> tuple[float, float, float]:
    return (
        sign[0] * values[remap[0]],
        sign[1] * values[remap[1]],
        sign[2] * values[remap[2]],
    )


def quat_multiply(
    ax: float,
    ay: float,
    az: float,
    aw: float,
    bx: float,
    by: float,
    bz: float,
    bw: float,
) -> tuple[float, float, float, float]:
    return (
        aw * bx + ax * bw + ay * bz - az * by,
        aw * by - ax * bz + ay * bw + az * bx,
        aw * bz + ax * by - ay * bx + az * bw,
        aw * bw - ax * bx - ay * by - az * bz,
    )


def quat_conjugate(qx: float, qy: float, qz: float, qw: float) -> tuple[float, float, float, float]:
    return (-qx, -qy, -qz, qw)


def quat_from_rpy(roll: float, pitch: float, yaw: float) -> tuple[float, float, float, float]:
    """Same Hamilton convention as esp32_hull/main/gx_output.c rpy_deg_to_quat()."""
    half_roll = roll * 0.5
    half_pitch = pitch * 0.5
    half_yaw = yaw * 0.5

    cr = math.cos(half_roll)
    sr = math.sin(half_roll)
    cp = math.cos(half_pitch)
    sp = math.sin(half_pitch)
    cy = math.cos(half_yaw)
    sy = math.sin(half_yaw)

    return (
        sr * cp * cy - cr * sp * sy,
        cr * sp * cy + sr * cp * sy,
        cr * cp * sy - sr * sp * cy,
        cr * cp * cy + sr * sp * sy,
    )


def ddm360b_frame_adapter() -> ImuFrameAdapter:
    """Preset for DDM360B module + esp32_hull gx_output frame."""
    return ImuFrameAdapter(
        orientation_rpy_offset_deg=(0.0, -90.0, 0.0),
        orientation_fix_order='post',
    )


@dataclass(frozen=True)
class ImuFrameAdapter:
    """Apply fixed axis remap and orientation offset from module frame to ROS frame."""

    orientation_rpy_offset_deg: tuple[float, float, float] = (0.0, -90.0, 0.0)
    orientation_fix_order: Literal['pre', 'post'] = 'post'
    invert_orientation: bool = False
    acc_remap: tuple[int, int, int] = (0, 1, 2)
    acc_sign: tuple[float, float, float] = (1.0, 1.0, 1.0)
    gyro_remap: tuple[int, int, int] = (0, 1, 2)
    gyro_sign: tuple[float, float, float] = (1.0, 1.0, 1.0)

    def __post_init__(self) -> None:
        rpy_rad = tuple(math.radians(v) for v in self.orientation_rpy_offset_deg)
        object.__setattr__(self, '_q_fix', quat_from_rpy(*rpy_rad))

    def adapt_orientation(
        self,
        qx: float,
        qy: float,
        qz: float,
        qw: float,
    ) -> tuple[float, float, float, float]:
        if self.invert_orientation:
            qx, qy, qz, qw = quat_conjugate(qx, qy, qz, qw)

        fix = self._q_fix
        if self.orientation_fix_order == 'pre':
            return quat_multiply(fix[0], fix[1], fix[2], fix[3], qx, qy, qz, qw)
        return quat_multiply(qx, qy, qz, qw, fix[0], fix[1], fix[2], fix[3])

    def adapt_linear_acceleration(
        self,
        acc_x: float,
        acc_y: float,
        acc_z: float,
    ) -> tuple[float, float, float]:
        return _remap_vector((acc_x, acc_y, acc_z), self.acc_remap, self.acc_sign)

    def adapt_angular_velocity(
        self,
        gyro_x: float,
        gyro_y: float,
        gyro_z: float,
    ) -> tuple[float, float, float]:
        return _remap_vector((gyro_x, gyro_y, gyro_z), self.gyro_remap, self.gyro_sign)
