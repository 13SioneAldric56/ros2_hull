#!/usr/bin/env python3
"""Send a lat/lon navigation goal to the GPS navigator."""

from __future__ import annotations

import sys

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import NavSatFix


def main() -> None:
    if len(sys.argv) < 3:
        print('Usage: send_nav_goal <latitude> <longitude> [altitude]')
        print('Example: send_nav_goal 22.405100 113.536800')
        raise SystemExit(1)

    lat = float(sys.argv[1])
    lon = float(sys.argv[2])
    alt = float(sys.argv[3]) if len(sys.argv) > 3 else 0.0

    rclpy.init()
    node = Node('send_nav_goal')
    pub = node.create_publisher(NavSatFix, '/navigation/goal', 10)

    msg = NavSatFix()
    msg.latitude = lat
    msg.longitude = lon
    msg.altitude = alt

    # Wait for navigator to discover this publisher (ROS 2 DDS latency).
    deadline = node.get_clock().now().nanoseconds + int(5e9)
    while pub.get_subscription_count() < 1:
        if node.get_clock().now().nanoseconds > deadline:
            node.get_logger().error(
                'No subscriber on /navigation/goal after 5s. '
                'Is navigation.launch.py running?'
            )
            raise SystemExit(1)
        rclpy.spin_once(node, timeout_sec=0.1)

    pub.publish(msg)
    rclpy.spin_once(node, timeout_sec=0.2)

    node.get_logger().info(f'Sent navigation goal: lat={lat}, lon={lon}, alt={alt}')
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
