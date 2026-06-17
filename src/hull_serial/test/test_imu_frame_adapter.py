import math

from hull_serial.imu_frame_adapter import ImuFrameAdapter, ddm360b_frame_adapter, quat_from_rpy
from hull_serial.imu_odometry_integrator import quat_rotate_vector


def test_ddm360b_vertical_motion_maps_to_world_z():
    adapter = ddm360b_frame_adapter()
    q_mod = (-0.12601763010025024, -0.012571737170219421, 0.990138053894043, -0.05990026891231537)

    qx, qy, qz, qw = adapter.adapt_orientation(*q_mod)
    impulse = adapter.adapt_linear_acceleration(12.0, 0.0, 0.0)
    world = quat_rotate_vector(qx, qy, qz, qw, *impulse)

    assert world[2] > abs(world[0])
    assert world[2] > abs(world[1])
    assert world[2] > 8.0


def test_adapter_remap_acc_axes():
    adapter = ImuFrameAdapter(
        orientation_rpy_offset_deg=(0.0, 0.0, 0.0),
        acc_remap=(2, 1, 0),
        acc_sign=(1.0, -1.0, 1.0),
    )
    acc = adapter.adapt_linear_acceleration(1.0, 2.0, 3.0)
    assert acc == (3.0, -2.0, 1.0)


def test_post_multiply_differs_from_pre_multiply():
    q_mod = (0.1, 0.2, 0.3, 0.9)
    pre = ImuFrameAdapter(
        orientation_rpy_offset_deg=(0.0, -90.0, 0.0),
        orientation_fix_order='pre',
    )
    post = ImuFrameAdapter(
        orientation_rpy_offset_deg=(0.0, -90.0, 0.0),
        orientation_fix_order='post',
    )
    assert pre.adapt_orientation(*q_mod) != post.adapt_orientation(*q_mod)


def test_quat_from_rpy_identity():
    q = quat_from_rpy(0.0, 0.0, 0.0)
    assert math.isclose(q[3], 1.0, abs_tol=1e-6)
