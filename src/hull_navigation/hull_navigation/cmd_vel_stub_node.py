#!/usr/bin/env python3
"""Placeholder actuator node: receives Nav2 cmd_vel, watchdog, optional republish."""

from __future__ import annotations

import rclpy
from geometry_msgs.msg import Twist
from rclpy.node import Node
from std_msgs.msg import Empty


class CmdVelStubNode(Node):
    def __init__(self) -> None:
        super().__init__('cmd_vel_stub')

        self.declare_parameter('cmd_vel_topic', '/cmd_vel')
        self.declare_parameter('cmd_vel_out_topic', '/cmd_vel/actuator')
        self.declare_parameter('cancel_topic', '/navigation/cancel')
        self.declare_parameter('watchdog_timeout_s', 0.5)
        self.declare_parameter('log_interval_s', 2.0)
        self.declare_parameter('republish_for_actuator', False)

        cmd_vel_topic = self.get_parameter('cmd_vel_topic').value
        cancel_topic = self.get_parameter('cancel_topic').value
        self.out_topic = self.get_parameter('cmd_vel_out_topic').value
        self.watchdog_timeout_s = float(self.get_parameter('watchdog_timeout_s').value)
        self.log_interval_s = float(self.get_parameter('log_interval_s').value)
        self.republish = bool(self.get_parameter('republish_for_actuator').value)

        self._last_cmd_time = self.get_clock().now()
        self._last_log_time = self.get_clock().now()
        self._last_cmd = Twist()

        self.out_pub = self.create_publisher(Twist, self.out_topic, 10)
        self.create_subscription(Twist, cmd_vel_topic, self._cmd_callback, 10)
        self.create_subscription(Empty, cancel_topic, self._cancel_callback, 10)
        self.create_timer(0.1, self._watchdog)

        self.get_logger().info(
            f'cmd_vel stub listening on {cmd_vel_topic} '
            f'(actuator output reserved on {self.out_topic})'
        )

    def _cmd_callback(self, msg: Twist) -> None:
        self._last_cmd = msg
        self._last_cmd_time = self.get_clock().now()

        now = self.get_clock().now()
        if (now - self._last_log_time).nanoseconds >= self.log_interval_s * 1e9:
            self.get_logger().info(
                f'cmd_vel: linear.x={msg.linear.x:.3f} m/s, '
                f'angular.z={msg.angular.z:.3f} rad/s'
            )
            self._last_log_time = now

        if self.republish:
            self.out_pub.publish(msg)

    def _cancel_callback(self, _msg: Empty) -> None:
        self._last_cmd = Twist()
        self._last_cmd_time = self.get_clock().now()
        if self.republish:
            self.out_pub.publish(Twist())
        self.get_logger().info('Navigation cancel received, zeroing cmd_vel output')

    def _watchdog(self) -> None:
        elapsed = (self.get_clock().now() - self._last_cmd_time).nanoseconds * 1e-9
        if elapsed > self.watchdog_timeout_s:
            if (
                abs(self._last_cmd.linear.x) > 1e-6
                or abs(self._last_cmd.angular.z) > 1e-6
            ):
                self.get_logger().warn(
                    f'cmd_vel watchdog: no command for {elapsed:.1f}s, zeroing output'
                )
            self._last_cmd = Twist()
            if self.republish:
                self.out_pub.publish(Twist())


def main(args=None) -> None:
    rclpy.init(args=args)
    node = CmdVelStubNode()
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
