#!/usr/bin/env python3
"""Navigate to a target latitude/longitude using fused GPS+IMU pose."""

from __future__ import annotations

import math

import rclpy
from geometry_msgs.msg import Point, PoseStamped, Twist
from nav_msgs.msg import Odometry, Path
from rclpy.node import Node
from sensor_msgs.msg import Imu, NavSatFix
from std_msgs.msg import Empty, Float64, String

from hull_navigation.geo_utils import (
    bearing_rad,
    deg,
    distance_m,
    lla_to_local_m,
    normalize_angle,
    quat_to_yaw,
)


class GpsNavigatorNode(Node):
    STATE_IDLE = 'IDLE'
    STATE_NAVIGATING = 'NAVIGATING'
    STATE_ARRIVED = 'ARRIVED'

    def __init__(self) -> None:
        super().__init__('gps_navigator')

        self.declare_parameter('map_frame', 'map')
        self.declare_parameter('odom_topic', '/odometry/filtered')
        self.declare_parameter('fix_topic', '/fix')
        self.declare_parameter('goal_topic', '/navigation/goal')
        self.declare_parameter('cancel_topic', '/navigation/cancel')
        self.declare_parameter('plan_topic', '/plan')
        self.declare_parameter('cmd_vel_topic', '/cmd_vel')
        self.declare_parameter('arrival_radius_m', 2.0)
        self.declare_parameter('max_linear_speed', 0.5)
        self.declare_parameter('max_angular_speed', 1.0)
        self.declare_parameter('heading_gain', 1.5)
        self.declare_parameter('slowdown_radius_m', 10.0)
        self.declare_parameter('min_fix_status', 0)
        self.declare_parameter('publish_cmd_vel', False)
        self.declare_parameter('control_rate_hz', 10.0)

        self.map_frame = self.get_parameter('map_frame').value
        self.arrival_radius_m = float(self.get_parameter('arrival_radius_m').value)
        self.max_linear_speed = float(self.get_parameter('max_linear_speed').value)
        self.max_angular_speed = float(self.get_parameter('max_angular_speed').value)
        self.heading_gain = float(self.get_parameter('heading_gain').value)
        self.slowdown_radius_m = float(self.get_parameter('slowdown_radius_m').value)
        self.min_fix_status = int(self.get_parameter('min_fix_status').value)
        self.publish_cmd_vel = bool(self.get_parameter('publish_cmd_vel').value)

        self._origin_lat: float | None = None
        self._origin_lon: float | None = None
        self._origin_alt: float | None = None
        self._current_x = 0.0
        self._current_y = 0.0
        self._current_yaw = 0.0
        self._has_pose = False

        self._goal_lat: float | None = None
        self._goal_lon: float | None = None
        self._goal_alt = 0.0
        self._goal_x: float | None = None
        self._goal_y: float | None = None
        self._state = self.STATE_IDLE
        self._imu_available = False
        self._warned_no_imu_heading = False

        odom_topic = self.get_parameter('odom_topic').value
        fix_topic = self.get_parameter('fix_topic').value
        goal_topic = self.get_parameter('goal_topic').value
        cancel_topic = self.get_parameter('cancel_topic').value
        plan_topic = self.get_parameter('plan_topic').value
        cmd_vel_topic = self.get_parameter('cmd_vel_topic').value

        self.status_pub = self.create_publisher(String, '/navigation/status', 10)
        self.distance_pub = self.create_publisher(Float64, '/navigation/distance_remaining', 10)
        self.bearing_pub = self.create_publisher(Float64, '/navigation/bearing_deg', 10)
        self.heading_pub = self.create_publisher(Float64, '/navigation/current_heading_deg', 10)
        self.heading_error_pub = self.create_publisher(Float64, '/navigation/heading_error_deg', 10)
        self.goal_pose_pub = self.create_publisher(PoseStamped, '/navigation/goal_pose', 10)
        self.plan_pub = self.create_publisher(Path, plan_topic, 10)
        self.cmd_vel_pub = self.create_publisher(Twist, cmd_vel_topic, 10)

        self.create_subscription(Odometry, odom_topic, self._odom_callback, 10)
        self.create_subscription(NavSatFix, fix_topic, self._fix_callback, 10)
        self.create_subscription(NavSatFix, goal_topic, self._goal_callback, 10)
        self.create_subscription(Empty, cancel_topic, self._cancel_callback, 10)
        self.create_subscription(Imu, '/imu/data', self._imu_callback, 10)

        rate = float(self.get_parameter('control_rate_hz').value)
        self.create_timer(1.0 / rate, self._control_loop)

        self.get_logger().info(
            f'GPS navigator ready. Publish goal to {goal_topic} '
            f'(sensor_msgs/NavSatFix), cancel on {cancel_topic}'
        )

    def _fix_callback(self, msg: NavSatFix) -> None:
        if msg.status.status < self.min_fix_status:
            return
        if self._origin_lat is None:
            self._origin_lat = msg.latitude
            self._origin_lon = msg.longitude
            self._origin_alt = msg.altitude
            self.get_logger().info(
                f'Navigator origin: lat={msg.latitude:.7f}, lon={msg.longitude:.7f}'
            )
            if self._goal_lat is not None and self._goal_lon is not None:
                self._activate_goal()

    def _odom_callback(self, msg: Odometry) -> None:
        self._current_x = msg.pose.pose.position.x
        self._current_y = msg.pose.pose.position.y
        if not self._imu_available:
            self._current_yaw = quat_to_yaw(msg.pose.pose.orientation)
        self._has_pose = True

    def _imu_callback(self, msg: Imu) -> None:
        cov = msg.orientation_covariance[0]
        if cov < 0.0:
            return
        self._imu_available = True
        self._warned_no_imu_heading = False
        self._current_yaw = quat_to_yaw(msg.orientation)

    def _goal_callback(self, msg: NavSatFix) -> None:
        if math.isnan(msg.latitude) or math.isnan(msg.longitude):
            self.get_logger().error('Goal rejected: latitude/longitude is NaN')
            return

        self._goal_lat = msg.latitude
        self._goal_lon = msg.longitude
        self._goal_alt = msg.altitude if not math.isnan(msg.altitude) else 0.0

        self.get_logger().info(
            f'New navigation goal: lat={self._goal_lat:.7f}, lon={self._goal_lon:.7f}'
        )

        if self._origin_lat is None:
            self.get_logger().warn('Waiting for GPS origin before activating goal')
            return

        self._activate_goal()

    def _cancel_callback(self, _msg: Empty) -> None:
        self._clear_goal('Navigation cancelled')

    def _activate_goal(self) -> None:
        assert self._goal_lat is not None
        assert self._goal_lon is not None
        assert self._origin_lat is not None
        assert self._origin_lon is not None
        assert self._origin_alt is not None

        self._goal_x, self._goal_y, _ = lla_to_local_m(
            self._origin_lat,
            self._origin_lon,
            self._origin_alt,
            self._goal_lat,
            self._goal_lon,
            self._goal_alt,
        )
        self._state = self.STATE_NAVIGATING
        self._publish_goal_pose()
        self._publish_plan()
        self.get_logger().info(
            f'Goal in map frame: x={self._goal_x:.2f} m, y={self._goal_y:.2f} m'
        )

    def _clear_goal(self, reason: str) -> None:
        self._goal_lat = None
        self._goal_lon = None
        self._goal_x = None
        self._goal_y = None
        self._state = self.STATE_IDLE
        self._publish_status(reason)
        self.cmd_vel_pub.publish(Twist())
        self._publish_plan(clear=True)
        self.get_logger().info(reason)

    def _control_loop(self) -> None:
        if self._state != self.STATE_NAVIGATING:
            self._publish_status(self._state)
            return

        if not self._has_pose or self._goal_x is None or self._goal_y is None:
            return

        dist = distance_m(self._current_x, self._current_y, self._goal_x, self._goal_y)
        bearing = bearing_rad(self._current_x, self._current_y, self._goal_x, self._goal_y)
        heading_error = normalize_angle(bearing - self._current_yaw)

        self.distance_pub.publish(Float64(data=dist))
        self.bearing_pub.publish(Float64(data=deg(bearing)))
        self.heading_pub.publish(Float64(data=deg(self._current_yaw)))
        self.heading_error_pub.publish(Float64(data=deg(heading_error)))

        if not self._imu_available and not self._warned_no_imu_heading:
            self.get_logger().warn(
                'No /imu/data received; heading stuck at 0°. '
                'heading_err equals bearing and will not change when you rotate.'
            )
            self._warned_no_imu_heading = True

        if dist <= self.arrival_radius_m:
            self._state = self.STATE_ARRIVED
            self.cmd_vel_pub.publish(Twist())
            self._publish_status(
                f'ARRIVED at goal (within {self.arrival_radius_m:.1f} m)'
            )
            self.get_logger().info(
                f'Arrived at goal, distance={dist:.2f} m'
            )
            return

        cmd = Twist()
        if self.publish_cmd_vel:
            speed_scale = min(1.0, dist / max(self.slowdown_radius_m, 0.1))
            cmd.linear.x = self.max_linear_speed * speed_scale
            cmd.angular.z = max(
                -self.max_angular_speed,
                min(self.max_angular_speed, self.heading_gain * heading_error),
            )
            self.cmd_vel_pub.publish(cmd)

        self._publish_plan()
        self._publish_status(
            f'NAVIGATING dist={dist:.1f}m bearing={deg(bearing):.0f}° '
            f'heading_err={deg(heading_error):.0f}°'
        )

    def _publish_status(self, text: str) -> None:
        self.status_pub.publish(String(data=text))

    def _publish_goal_pose(self) -> None:
        if self._goal_x is None or self._goal_y is None:
            return
        pose = PoseStamped()
        pose.header.stamp = self.get_clock().now().to_msg()
        pose.header.frame_id = self.map_frame
        pose.pose.position = Point(x=self._goal_x, y=self._goal_y, z=0.0)
        pose.pose.orientation.w = 1.0
        self.goal_pose_pub.publish(pose)

    def _publish_plan(self, clear: bool = False) -> None:
        if clear or not self._has_pose or self._goal_x is None or self._goal_y is None:
            empty = Path()
            empty.header.stamp = self.get_clock().now().to_msg()
            empty.header.frame_id = self.map_frame
            self.plan_pub.publish(empty)
            return
        path = Path()
        path.header.stamp = self.get_clock().now().to_msg()
        path.header.frame_id = self.map_frame

        start = PoseStamped()
        start.header = path.header
        start.pose.position = Point(x=self._current_x, y=self._current_y, z=0.0)
        start.pose.orientation.w = 1.0

        end = PoseStamped()
        end.header = path.header
        end.pose.position = Point(x=self._goal_x, y=self._goal_y, z=0.0)
        end.pose.orientation.w = 1.0

        path.poses = [start, end]
        self.plan_pub.publish(path)


def main(args=None) -> None:
    rclpy.init(args=args)
    node = GpsNavigatorNode()
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
