import math

from hull_serial.imu_odometry_integrator import ImuOdometryIntegrator, quat_rotate_vector


def _calibrate(integrator: ImuOdometryIntegrator) -> None:
    for i in range(120):
        integrator.update(
            timestamp_us=i * 10_000,
            qx=0.0,
            qy=0.0,
            qz=0.0,
            qw=1.0,
            acc_x=0.0,
            acc_y=0.0,
            acc_z=9.80665,
            gyro_x=0.0,
            gyro_y=0.0,
            gyro_z=0.0,
        )
    assert integrator.calibrated


def test_quat_rotate_identity():
    wx, wy, wz = quat_rotate_vector(0.0, 0.0, 0.0, 1.0, 1.0, 2.0, 3.0)
    assert abs(wx - 1.0) < 1e-6
    assert abs(wy - 2.0) < 1e-6
    assert abs(wz - 3.0) < 1e-6


def test_stationary_device_stays_at_origin():
    integrator = ImuOdometryIntegrator(gravity_calib_samples=20)
    _calibrate(integrator)

    for i in range(120, 220):
        sample = integrator.update(
            timestamp_us=i * 10_000,
            qx=0.0,
            qy=0.0,
            qz=0.0,
            qw=1.0,
            acc_x=0.0,
            acc_y=0.0,
            acc_z=9.80665,
            gyro_x=0.0,
            gyro_y=0.0,
            gyro_z=0.0,
        )
        assert sample is not None
        assert sample.calibrated is True
        assert abs(sample.position_x) < 0.05
        assert abs(sample.position_y) < 0.05
        assert abs(sample.position_z) < 0.05


def test_constant_acceleration_integrates_position():
    integrator = ImuOdometryIntegrator(
        gravity_calib_samples=20,
        zupt_accel_threshold=0.0,
        zupt_gyro_threshold=0.0,
        velocity_damping=0.0,
        motion_accel_threshold=0.0,
        bias_learning_rate=0.0,
    )
    _calibrate(integrator)

    sample = integrator.update(
        timestamp_us=1_210_000,
        qx=0.0,
        qy=0.0,
        qz=0.0,
        qw=1.0,
        acc_x=1.0,
        acc_y=0.0,
        acc_z=9.80665,
        gyro_x=0.0,
        gyro_y=0.0,
        gyro_z=0.0,
    )
    assert sample is not None
    assert sample.position_x > 0.0002
    assert sample.velocity_x > 0.015
    assert math.isclose(sample.velocity_x, 0.02, abs_tol=0.01)


def test_motion_requires_impulse():
    integrator = ImuOdometryIntegrator(
        gravity_calib_samples=20,
        motion_accel_threshold=0.45,
        bias_learning_rate=0.2,
    )
    _calibrate(integrator)

    for i in range(200, 300):
        integrator.update(
            timestamp_us=i * 10_000,
            qx=0.0,
            qy=0.0,
            qz=0.0,
            qw=1.0,
            acc_x=0.0,
            acc_y=0.0,
            acc_z=9.80665,
            gyro_x=0.0,
            gyro_y=0.0,
            gyro_z=0.0,
        )

    sample = integrator.update(
        timestamp_us=3_010_000,
        qx=0.0,
        qy=0.0,
        qz=0.0,
        qw=1.0,
        acc_x=0.0,
        acc_y=0.0,
        acc_z=9.80665,
        gyro_x=0.0,
        gyro_y=0.0,
        gyro_z=0.0,
    )
    assert sample is not None
    assert abs(sample.position_x) < 0.02
    assert abs(sample.position_y) < 0.02
    assert abs(sample.position_z) < 0.02


def test_push_direction_changes_world_motion():
    integrator = ImuOdometryIntegrator(
        gravity_calib_samples=20,
        motion_accel_threshold=0.4,
        bias_learning_rate=0.0,
        velocity_damping=0.0,
        zupt_accel_threshold=0.0,
        zupt_gyro_threshold=10.0,
    )
    _calibrate(integrator)

    q = (0.0, 0.0, 0.0, 1.0)
    base = (0.0, 0.0, 9.80665)

    def push(axis: tuple[float, float, float], timestamp_us: int):
        return integrator.update(
            timestamp_us=timestamp_us,
            qx=q[0],
            qy=q[1],
            qz=q[2],
            qw=q[3],
            acc_x=base[0] + axis[0],
            acc_y=base[1] + axis[1],
            acc_z=base[2] + axis[2],
            gyro_x=0.0,
            gyro_y=0.0,
            gyro_z=0.0,
        )

    x_sample = push((2.0, 0.0, 0.0), 1_210_000)
    integrator.reset()
    _calibrate(integrator)
    y_sample = push((0.0, 2.0, 0.0), 1_210_000)

    assert x_sample is not None and y_sample is not None
    assert abs(x_sample.velocity_x) > abs(x_sample.velocity_y)
    assert abs(y_sample.velocity_y) > abs(y_sample.velocity_x)
