#!/usr/bin/env python3
"""Fuse GPS position (/fix) with IMU orientation (/imu/data) for navigation."""

from __future__ import annotations

import rclpy
from geometry_msgs.msg import Point, Pose, PoseStamped, Quaternion, TransformStamped
from nav_msgs.msg import Odometry, Path
from rclpy.node import Node
from sensor_msgs.msg import Imu, NavSatFix
from std_msgs.msg import Header
from tf2_ros import TransformBroadcaster

from hull_navigation.geo_utils import lla_to_local_m


class GpsImuFusionNode(Node):
    def __init__(self) -> None:
        super().__init__('gps_imu_fusion')

        self.declare_parameter('map_frame', 'map')
        self.declare_parameter('base_link_frame', 'base_link')
        self.declare_parameter('fix_topic', '/fix')
        self.declare_parameter('imu_topic', '/imu/data')
        self.declare_parameter('odom_topic', '/odometry/filtered')
        self.declare_parameter('fused_path_topic', '/fused_path')
        self.declare_parameter('publish_tf', True)
        self.declare_parameter('publish_fused_path', True)
        self.declare_parameter('path_min_distance', 0.5)
        self.declare_parameter('min_fix_status', 0)

        self.map_frame = self.get_parameter('map_frame').value
        self.base_link_frame = self.get_parameter('base_link_frame').value
        self.publish_tf = bool(self.get_parameter('publish_tf').value)
        self.publish_fused_path = bool(self.get_parameter('publish_fused_path').value)
        self.path_min_distance = float(self.get_parameter('path_min_distance').value)
        self.min_fix_status = int(self.get_parameter('min_fix_status').value)

        self._origin_lat: float | None = None
        self._origin_lon: float | None = None
        self._origin_alt: float | None = None
        self._position = Point(x=0.0, y=0.0, z=0.0)
        self._orientation = Quaternion(x=0.0, y=0.0, z=0.0, w=1.0)
        self._has_gps = False
        self._has_imu = False
        self._warned_no_imu = False
        self._last_imu_stamp = self.get_clock().now().to_msg()
        self._fused_path = Path()
        self._fused_path.header.frame_id = self.map_frame
        self._last_path_point: Point | None = None

        odom_topic = self.get_parameter('odom_topic').value
        fused_path_topic = self.get_parameter('fused_path_topic').value
        fix_topic = self.get_parameter('fix_topic').value
        imu_topic = self.get_parameter('imu_topic').value

        self.odom_pub = self.create_publisher(Odometry, odom_topic, 10)
        self.path_pub = self.create_publisher(Path, fused_path_topic, 10)
        self.tf_broadcaster = TransformBroadcaster(self)
        self.create_subscription(NavSatFix, fix_topic, self._fix_callback, 10)
        self.create_subscription(Imu, imu_topic, self._imu_callback, 50)
        self.create_timer(0.1, self._republish_if_gps_only)

        self.get_logger().info(
            f'Fusing {fix_topic} + {imu_topic} -> {odom_topic}, '
            f'TF {self.map_frame} -> {self.base_link_frame}, '
            f'path {fused_path_topic}'
        )

    def _fix_callback(self, msg: NavSatFix) -> None:
        if msg.status.status < self.min_fix_status:
            return

        if self._origin_lat is None:
            self._origin_lat = msg.latitude
            self._origin_lon = msg.longitude
            self._origin_alt = msg.altitude
            self.get_logger().info(
                f'GPS origin: lat={msg.latitude:.7f}, lon={msg.longitude:.7f}, '
                f'alt={msg.altitude:.2f}'
            )

        assert self._origin_lat is not None
        assert self._origin_lon is not None
        assert self._origin_alt is not None

        x, y, z = lla_to_local_m(
            self._origin_lat,
            self._origin_lon,
            self._origin_alt,
            msg.latitude,
            msg.longitude,
            msg.altitude,
        )
        self._position = Point(x=x, y=y, z=z)
        self._has_gps = True
        self._publish(msg.header.stamp)

    def _imu_callback(self, msg: Imu) -> None:
        if not self._has_imu:
            self.get_logger().info('IMU orientation available, full fusion active')
        self._orientation = msg.orientation
        self._has_imu = True
        self._warned_no_imu = False
        self._last_imu_stamp = msg.header.stamp
        if self._has_gps:
            self._publish(msg.header.stamp)

    def _republish_if_gps_only(self) -> None:
        if self._has_gps and not self._has_imu:
            self._publish(self.get_clock().now().to_msg())

    def _publish(self, stamp) -> None:
        if not self._has_gps:
            return

        if not self._has_imu and not self._warned_no_imu:
            self.get_logger().warn(
                'GPS ready but no /imu/data yet; publishing map->base_link with '
                'identity orientation until IMU arrives'
            )
            self._warned_no_imu = True

        odom = Odometry()
        odom.header = Header(stamp=stamp, frame_id=self.map_frame)
        odom.child_frame_id = self.base_link_frame
        odom.pose.pose = Pose(position=self._position, orientation=self._orientation)
        if not self._has_imu:
            odom.pose.covariance[35] = -1.0
        self.odom_pub.publish(odom)

        if self.publish_fused_path:
            self._append_path(stamp)

        if not self.publish_tf:
            return

        transform = TransformStamped()
        transform.header.stamp = stamp
        transform.header.frame_id = self.map_frame
        transform.child_frame_id = self.base_link_frame
        transform.transform.translation.x = self._position.x
        transform.transform.translation.y = self._position.y
        transform.transform.translation.z = self._position.z
        transform.transform.rotation = self._orientation
        self.tf_broadcaster.sendTransform(transform)

    def _append_path(self, stamp) -> None:
        if self._last_path_point is None:
            append = True
        else:
            dx = self._position.x - self._last_path_point.x
            dy = self._position.y - self._last_path_point.y
            dz = self._position.z - self._last_path_point.z
            append = (dx * dx + dy * dy + dz * dz) >= self.path_min_distance ** 2

        if not append:
            return

        pose = PoseStamped()
        pose.header.stamp = stamp
        pose.header.frame_id = self.map_frame
        pose.pose.position = self._position
        pose.pose.orientation = self._orientation
        self._fused_path.poses.append(pose)
        self._fused_path.header.stamp = stamp
        self._last_path_point = Point(
            x=self._position.x,
            y=self._position.y,
            z=self._position.z,
        )
        self.path_pub.publish(self._fused_path)


def main(args=None) -> None:
    rclpy.init(args=args)
    node = GpsImuFusionNode()
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
