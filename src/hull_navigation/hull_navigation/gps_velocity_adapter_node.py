#!/usr/bin/env python3
"""Convert NMEA /vel (TwistStamped) to EKF-compatible TwistWithCovarianceStamped."""

from __future__ import annotations

import math

import rclpy
from geometry_msgs.msg import TwistStamped, TwistWithCovarianceStamped
from rclpy.node import Node


class GpsVelocityAdapterNode(Node):
    """Adapt GPS ground speed from nmea_navsat_driver for robot_localization EKF."""

    def __init__(self) -> None:
        super().__init__('gps_velocity_adapter')

        self.declare_parameter('vel_topic', '/vel')
        self.declare_parameter('output_topic', '/gps/twist')
        self.declare_parameter('min_speed_mps', 0.05)
        self.declare_parameter('base_link_frame', 'base_link')
        self.declare_parameter('linear_covariance', 0.5)
        self.declare_parameter('angular_covariance', 99999.0)

        vel_topic = self.get_parameter('vel_topic').value
        output_topic = self.get_parameter('output_topic').value
        self.min_speed_mps = float(self.get_parameter('min_speed_mps').value)
        self.base_link_frame = self.get_parameter('base_link_frame').value
        self.linear_cov = float(self.get_parameter('linear_covariance').value)
        self.angular_cov = float(self.get_parameter('angular_covariance').value)

        self.pub = self.create_publisher(TwistWithCovarianceStamped, output_topic, 10)
        self.create_subscription(TwistStamped, vel_topic, self._vel_callback, 10)

        self.get_logger().info(
            f'GPS velocity adapter: {vel_topic} -> {output_topic} '
            f'(requires NMEA VTG or RMC sentences from GPS receiver)'
        )

    def _vel_callback(self, msg: TwistStamped) -> None:
        # nmea_navsat_driver publishes ENU-style horizontal velocity:
        #   linear.x = speed * sin(course), linear.y = speed * cos(course)
        vx = msg.twist.linear.x
        vy = msg.twist.linear.y
        if not (math.isfinite(vx) and math.isfinite(vy)):
            return

        speed = math.hypot(vx, vy)
        if speed < self.min_speed_mps:
            speed = 0.0

        out = TwistWithCovarianceStamped()
        out.header = msg.header
        out.header.frame_id = self.base_link_frame
        out.twist.twist.linear.x = speed
        out.twist.covariance[0] = self.linear_cov
        out.twist.covariance[35] = self.angular_cov
        self.pub.publish(out)


def main(args=None) -> None:
    rclpy.init(args=args)
    node = GpsVelocityAdapterNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
