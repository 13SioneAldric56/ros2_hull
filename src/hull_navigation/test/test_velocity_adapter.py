import math

from geometry_msgs.msg import TwistStamped, TwistWithCovarianceStamped
from hull_navigation.geo_utils import quat_to_yaw, yaw_to_quaternion
from hull_navigation.gps_velocity_adapter_node import GpsVelocityAdapterNode
import rclpy


def test_velocity_adapter_computes_speed():
    rclpy.init()
    node = GpsVelocityAdapterNode()
    received: list[TwistWithCovarianceStamped] = []

    def cb(msg: TwistWithCovarianceStamped) -> None:
        received.append(msg)

    sub = node.create_subscription(TwistWithCovarianceStamped, '/gps/twist', cb, 10)

    vel = TwistStamped()
    vel.twist.linear.x = 3.0
    vel.twist.linear.y = 4.0
    node._vel_callback(vel)

    rclpy.spin_once(node, timeout_sec=0.1)
    sub.destroy()
    assert len(received) == 1
    assert abs(received[0].twist.twist.linear.x - 5.0) < 1e-6
    node.destroy_node()
    rclpy.shutdown()


def test_yaw_to_quaternion():
    q = yaw_to_quaternion(math.pi / 2.0)
    assert abs(quat_to_yaw(q) - math.pi / 2.0) < 0.01
