"""Dead-reckoning integrator: orientation + acceleration -> position in odom frame."""

from __future__ import annotations

import math
from dataclasses import dataclass


def quat_rotate_vector(
    qx: float,
    qy: float,
    qz: float,
    qw: float,
    vx: float,
    vy: float,
    vz: float,
) -> tuple[float, float, float]:
    """Rotate vector from body frame to world frame using Hamilton quaternion."""
    tx = 2.0 * (qy * vz - qz * vy)
    ty = 2.0 * (qz * vx - qx * vz)
    tz = 2.0 * (qx * vy - qy * vx)
    return (
        vx + qw * tx + (qy * tz - qz * ty),
        vy + qw * ty + (qz * tx - qx * tz),
        vz + qw * tz + (qx * ty - qy * tx),
    )


def vector_norm(x: float, y: float, z: float) -> float:
    return math.sqrt(x * x + y * y + z * z)


def _normalize(x: float, y: float, z: float) -> tuple[float, float, float]:
    norm = vector_norm(x, y, z)
    if norm < 1e-9:
        return 0.0, 0.0, 0.0
    return x / norm, y / norm, z / norm


@dataclass
class ImuOdometryState:
    position_x: float = 0.0
    position_y: float = 0.0
    position_z: float = 0.0
    velocity_x: float = 0.0
    velocity_y: float = 0.0
    velocity_z: float = 0.0


@dataclass
class ImuOdometrySample:
    position_x: float
    position_y: float
    position_z: float
    velocity_x: float
    velocity_y: float
    velocity_z: float
    linear_accel_world_x: float
    linear_accel_world_y: float
    linear_accel_world_z: float
    dt: float
    stationary: bool
    calibrated: bool


class ImuOdometryIntegrator:
    """Integrate IMU acceleration into position using ESP32 timestamps."""

    def __init__(
        self,
        gravity: float = 9.80665,
        max_dt: float = 0.5,
        zupt_accel_threshold: float = 0.2,
        zupt_gyro_threshold: float = 0.12,
        gravity_calib_samples: int = 100,
        velocity_damping: float = 0.2,
        max_velocity: float = 2.0,
        bias_learning_rate: float = 0.03,
        motion_accel_threshold: float = 0.45,
    ) -> None:
        self.gravity = gravity
        self.max_dt = max_dt
        self.zupt_accel_threshold = zupt_accel_threshold
        self.zupt_gyro_threshold = zupt_gyro_threshold
        self.gravity_calib_samples = gravity_calib_samples
        self.velocity_damping = velocity_damping
        self.max_velocity = max_velocity
        self.bias_learning_rate = bias_learning_rate
        self.motion_accel_threshold = motion_accel_threshold
        self.state = ImuOdometryState()
        self._last_timestamp_us: int | None = None
        self._gravity_world: tuple[float, float, float] | None = None
        self._gravity_sum = [0.0, 0.0, 0.0]
        self._gravity_count = 0
        self._accel_bias = [0.0, 0.0, 0.0]

    @property
    def calibrated(self) -> bool:
        return self._gravity_world is not None

    def reset(self) -> None:
        self.state = ImuOdometryState()
        self._last_timestamp_us = None
        self._gravity_world = None
        self._gravity_sum = [0.0, 0.0, 0.0]
        self._gravity_count = 0
        self._accel_bias = [0.0, 0.0, 0.0]

    def _current_sample(
        self,
        dt: float,
        stationary: bool,
        calibrated: bool,
        linear_acc: tuple[float, float, float] = (0.0, 0.0, 0.0),
    ) -> ImuOdometrySample:
        return ImuOdometrySample(
            position_x=self.state.position_x,
            position_y=self.state.position_y,
            position_z=self.state.position_z,
            velocity_x=self.state.velocity_x,
            velocity_y=self.state.velocity_y,
            velocity_z=self.state.velocity_z,
            linear_accel_world_x=linear_acc[0],
            linear_accel_world_y=linear_acc[1],
            linear_accel_world_z=linear_acc[2],
            dt=dt,
            stationary=stationary,
            calibrated=calibrated,
        )

    def _calibrate_gravity(
        self,
        acc_world: tuple[float, float, float],
        gyro_x: float,
        gyro_y: float,
        gyro_z: float,
    ) -> bool:
        if vector_norm(gyro_x, gyro_y, gyro_z) > self.zupt_gyro_threshold:
            return False

        self._gravity_sum[0] += acc_world[0]
        self._gravity_sum[1] += acc_world[1]
        self._gravity_sum[2] += acc_world[2]
        self._gravity_count += 1
        if self._gravity_count < self.gravity_calib_samples:
            return False

        avg = (
            self._gravity_sum[0] / self._gravity_count,
            self._gravity_sum[1] / self._gravity_count,
            self._gravity_sum[2] / self._gravity_count,
        )
        direction = _normalize(*avg)
        self._gravity_world = (
            direction[0] * self.gravity,
            direction[1] * self.gravity,
            direction[2] * self.gravity,
        )
        return True

    def _update_accel_bias(
        self,
        linear_acc: tuple[float, float, float],
        gyro_x: float,
        gyro_y: float,
        gyro_z: float,
    ) -> None:
        if vector_norm(gyro_x, gyro_y, gyro_z) > self.zupt_gyro_threshold:
            return

        alpha = self.bias_learning_rate
        self._accel_bias[0] = (1.0 - alpha) * self._accel_bias[0] + alpha * linear_acc[0]
        self._accel_bias[1] = (1.0 - alpha) * self._accel_bias[1] + alpha * linear_acc[1]
        self._accel_bias[2] = (1.0 - alpha) * self._accel_bias[2] + alpha * linear_acc[2]

    def _corrected_linear_acc(
        self,
        linear_acc: tuple[float, float, float],
    ) -> tuple[float, float, float]:
        return (
            linear_acc[0] - self._accel_bias[0],
            linear_acc[1] - self._accel_bias[1],
            linear_acc[2] - self._accel_bias[2],
        )

    def _apply_velocity_damping(self, dt: float) -> None:
        if self.velocity_damping <= 0.0:
            return
        decay = max(0.0, 1.0 - self.velocity_damping * dt)
        self.state.velocity_x *= decay
        self.state.velocity_y *= decay
        self.state.velocity_z *= decay

    def _clamp_velocity(self) -> None:
        speed = vector_norm(
            self.state.velocity_x,
            self.state.velocity_y,
            self.state.velocity_z,
        )
        if speed <= self.max_velocity:
            return
        scale = self.max_velocity / speed
        self.state.velocity_x *= scale
        self.state.velocity_y *= scale
        self.state.velocity_z *= scale

    def update(
        self,
        timestamp_us: int,
        qx: float,
        qy: float,
        qz: float,
        qw: float,
        acc_x: float,
        acc_y: float,
        acc_z: float,
        gyro_x: float,
        gyro_y: float,
        gyro_z: float,
    ) -> ImuOdometrySample | None:
        acc_world = quat_rotate_vector(qx, qy, qz, qw, acc_x, acc_y, acc_z)

        if self._last_timestamp_us is None:
            self._last_timestamp_us = timestamp_us
            self._calibrate_gravity(acc_world, gyro_x, gyro_y, gyro_z)
            return self._current_sample(0.0, True, self.calibrated)

        dt = (timestamp_us - self._last_timestamp_us) * 1e-6
        self._last_timestamp_us = timestamp_us
        if dt <= 0.0 or dt > self.max_dt:
            return None

        if not self.calibrated:
            self._calibrate_gravity(acc_world, gyro_x, gyro_y, gyro_z)
            return self._current_sample(dt, True, self.calibrated)

        gravity = self._gravity_world
        assert gravity is not None
        linear_acc = (
            acc_world[0] - gravity[0],
            acc_world[1] - gravity[1],
            acc_world[2] - gravity[2],
        )
        self._update_accel_bias(linear_acc, gyro_x, gyro_y, gyro_z)
        corrected_acc = self._corrected_linear_acc(linear_acc)

        stationary = (
            vector_norm(*corrected_acc) < self.zupt_accel_threshold
            and vector_norm(gyro_x, gyro_y, gyro_z) < self.zupt_gyro_threshold
        )
        moving = vector_norm(*corrected_acc) >= self.motion_accel_threshold

        if stationary or not moving:
            self.state.velocity_x = 0.0
            self.state.velocity_y = 0.0
            self.state.velocity_z = 0.0
        else:
            self.state.velocity_x += corrected_acc[0] * dt
            self.state.velocity_y += corrected_acc[1] * dt
            self.state.velocity_z += corrected_acc[2] * dt
            self._apply_velocity_damping(dt)
            self._clamp_velocity()

        self.state.position_x += self.state.velocity_x * dt
        self.state.position_y += self.state.velocity_y * dt
        self.state.position_z += self.state.velocity_z * dt

        return ImuOdometrySample(
            position_x=self.state.position_x,
            position_y=self.state.position_y,
            position_z=self.state.position_z,
            velocity_x=self.state.velocity_x,
            velocity_y=self.state.velocity_y,
            velocity_z=self.state.velocity_z,
            linear_accel_world_x=corrected_acc[0],
            linear_accel_world_y=corrected_acc[1],
            linear_accel_world_z=corrected_acc[2],
            dt=dt,
            stationary=stationary,
            calibrated=True,
        )
