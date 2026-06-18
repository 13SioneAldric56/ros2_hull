#!/usr/bin/env python3
"""Bridge lat/lon navigation goals to Nav2 NavigateToPose action."""

from __future__ import annotations

import math

import rclpy
from action_msgs.msg import GoalStatus
from geometry_msgs.msg import PoseStamped
from nav2_msgs.action import NavigateToPose
from rclpy.action import ActionClient
from rclpy.callback_groups import MutuallyExclusiveCallbackGroup
from rclpy.duration import Duration
from rclpy.node import Node
from rclpy.time import Time
from robot_localization.srv import FromLL
from sensor_msgs.msg import NavSatFix
from std_msgs.msg import Empty, Float64, String
from tf2_ros import Buffer, TransformException, TransformListener

from hull_navigation.geo_utils import bearing_rad, quat_to_yaw, yaw_to_quaternion


class GpsGoalBridgeNode(Node):
    STATE_IDLE = 'IDLE'
    STATE_NAVIGATING = 'NAVIGATING'
    STATE_ARRIVED = 'ARRIVED'
    STATE_FAILED = 'FAILED'

    def __init__(self) -> None:
        super().__init__('gps_goal_bridge')

        self.declare_parameter('map_frame', 'map')
        self.declare_parameter('goal_topic', '/navigation/goal')
        self.declare_parameter('cancel_topic', '/navigation/cancel')
        self.declare_parameter('from_ll_service', '/fromLL')
        self.declare_parameter('navigate_action', 'navigate_to_pose')
        self.declare_parameter('base_link_frame', 'base_link')
        self.declare_parameter('arrival_radius_m', 5.0)
        self.declare_parameter('goal_timeout_s', 600.0)

        self.map_frame = self.get_parameter('map_frame').value
        self.base_link_frame = self.get_parameter('base_link_frame').value
        self.from_ll_service = self.get_parameter('from_ll_service').value
        self.arrival_radius_m = float(self.get_parameter('arrival_radius_m').value)
        self.goal_timeout_s = float(self.get_parameter('goal_timeout_s').value)

        self._state = self.STATE_IDLE
        self._goal_handle = None
        self._current_x = 0.0
        self._current_y = 0.0
        self._current_yaw = 0.0
        self._has_pose = False
        self._goal_x: float | None = None
        self._goal_y: float | None = None
        self._warned_bad_tf = False

        self._action_group = MutuallyExclusiveCallbackGroup()
        self._service_group = MutuallyExclusiveCallbackGroup()

        action_name = self.get_parameter('navigate_action').value
        self._nav_client = ActionClient(
            self,
            NavigateToPose,
            action_name,
            callback_group=self._action_group,
        )
        self._from_ll_client = self.create_client(
            FromLL,
            self.from_ll_service,
            callback_group=self._service_group,
        )
        self._tf_buffer = Buffer()
        self._tf_listener = TransformListener(self._tf_buffer, self)

        self.status_pub = self.create_publisher(String, '/navigation/status', 10)
        self.distance_pub = self.create_publisher(Float64, '/navigation/distance_remaining', 10)
        self.goal_pose_pub = self.create_publisher(PoseStamped, '/navigation/goal_pose', 10)

        goal_topic = self.get_parameter('goal_topic').value
        cancel_topic = self.get_parameter('cancel_topic').value

        self.create_subscription(NavSatFix, goal_topic, self._goal_callback, 10)
        self.create_subscription(Empty, cancel_topic, self._cancel_callback, 10)

        self.create_timer(1.0, self._status_timer)

        self.get_logger().info(
            f'GPS goal bridge ready. Publish NavSatFix to {goal_topic}, '
            f'Nav2 action: {action_name}, fromLL: {self.from_ll_service}'
        )

    @staticmethod
    def _transform_is_valid(transform) -> bool:
        t = transform.transform.translation
        r = transform.transform.rotation
        return all(
            math.isfinite(v)
            for v in (t.x, t.y, t.z, r.x, r.y, r.z, r.w)
        )

    def _update_map_pose(self) -> bool:
        try:
            transform = self._tf_buffer.lookup_transform(
                self.map_frame,
                self.base_link_frame,
                Time(),
                timeout=Duration(seconds=0.2),
            )
        except TransformException:
            return False

        if not self._transform_is_valid(transform):
            if not self._warned_bad_tf:
                self.get_logger().warn(
                    'map→base_link TF contains NaN; waiting for GPS/IMU/EKF to stabilize '
                    '(navsat_transform has a 3 s startup delay)'
                )
                self._warned_bad_tf = True
            self._has_pose = False
            return False

        self._warned_bad_tf = False
        self._current_x = transform.transform.translation.x
        self._current_y = transform.transform.translation.y
        self._current_yaw = quat_to_yaw(transform.transform.rotation)
        self._has_pose = True
        return True

    def _goal_callback(self, msg: NavSatFix) -> None:
        if math.isnan(msg.latitude) or math.isnan(msg.longitude):
            self.get_logger().error('Goal rejected: latitude/longitude is NaN')
            return

        if not self._from_ll_client.wait_for_service(timeout_sec=2.0):
            self.get_logger().error(
                f'Service {self.from_ll_service} unavailable. '
                'Is navsat_transform running?'
            )
            self._publish_status(self.STATE_FAILED)
            return

        request = FromLL.Request()
        request.ll_point.latitude = msg.latitude
        request.ll_point.longitude = msg.longitude
        request.ll_point.altitude = msg.altitude if not math.isnan(msg.altitude) else 0.0

        future = self._from_ll_client.call_async(request)
        future.add_done_callback(
            lambda f: self._on_from_ll(f, msg.latitude, msg.longitude)
        )

    def _on_from_ll(self, future, lat: float, lon: float) -> None:
        try:
            response = future.result()
        except Exception as exc:  # noqa: BLE001
            self.get_logger.error(f'fromLL service call failed: {exc}')
            self._publish_status(self.STATE_FAILED)
            return

        self._goal_x = response.map_point.x
        self._goal_y = response.map_point.y

        self.get_logger().info(
            f'Goal lat={lat:.7f}, lon={lon:.7f} -> '
            f'map x={self._goal_x:.2f}, y={self._goal_y:.2f}'
        )
        self._publish_goal_pose()
        self._send_nav2_goal()

    def _send_nav2_goal(self) -> None:
        if self._goal_x is None or self._goal_y is None:
            return

        if not self._nav_client.wait_for_server(timeout_sec=5.0):
            self.get_logger().error('Nav2 navigate_to_pose action server not available')
            self._publish_status(self.STATE_FAILED)
            return

        if self._goal_handle is not None:
            self.get_logger().info('Cancelling previous Nav2 goal before sending new one')
            self._goal_handle.cancel_goal_async()

        goal_msg = NavigateToPose.Goal()
        goal_msg.pose.header.stamp = self.get_clock().now().to_msg()
        goal_msg.pose.header.frame_id = self.map_frame
        goal_msg.pose.pose.position.x = self._goal_x
        goal_msg.pose.pose.position.y = self._goal_y
        goal_msg.pose.pose.position.z = 0.0

        self._update_map_pose()

        if self._has_pose:
            bearing = bearing_rad(
                self._current_x, self._current_y, self._goal_x, self._goal_y
            )
            goal_msg.pose.pose.orientation = yaw_to_quaternion(bearing)
        else:
            goal_msg.pose.pose.orientation.w = 1.0

        send_future = self._nav_client.send_goal_async(
            goal_msg,
            feedback_callback=self._feedback_callback,
        )
        send_future.add_done_callback(self._goal_response_callback)

    def _goal_response_callback(self, future) -> None:
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().error('Nav2 goal rejected')
            self._state = self.STATE_FAILED
            self._publish_status(self.STATE_FAILED)
            return

        self._goal_handle = goal_handle
        self._state = self.STATE_NAVIGATING
        self.get_logger().info('Nav2 goal accepted')
        result_future = goal_handle.get_result_async()
        result_future.add_done_callback(
            lambda future, handle=goal_handle: self._result_callback(future, handle)
        )

    def _feedback_callback(self, feedback_msg) -> None:
        remaining = feedback_msg.feedback.distance_remaining
        self.distance_pub.publish(Float64(data=remaining))

    def _result_callback(self, future, goal_handle) -> None:
        if goal_handle != self._goal_handle:
            return

        status = future.result().status
        self._goal_handle = None

        if status == GoalStatus.STATUS_SUCCEEDED:
            self._state = self.STATE_ARRIVED
            self.get_logger().info(
                f'Navigation succeeded (within {self.arrival_radius_m:.1f} m tolerance)'
            )
        elif status in (GoalStatus.STATUS_CANCELED, GoalStatus.STATUS_ABORTED):
            self._state = self.STATE_IDLE
            self.get_logger().info(f'Navigation ended with status={status}')
        else:
            self._state = self.STATE_FAILED
            self.get_logger().error(f'Navigation failed with status={status}')

        self._publish_status(self._state)

    def _cancel_callback(self, _msg: Empty) -> None:
        if self._goal_handle is not None:
            self.get_logger().info('Canceling Nav2 navigation goal')
            cancel_future = self._goal_handle.cancel_goal_async()
            cancel_future.add_done_callback(
                lambda _f: self.get_logger().info('Cancel request sent')
            )
        self._goal_x = None
        self._goal_y = None
        self._state = self.STATE_IDLE
        self._publish_status('Navigation cancelled')

    def _status_timer(self) -> None:
        self._update_map_pose()
        if self._state == self.STATE_NAVIGATING and self._has_pose:
            if self._goal_x is not None and self._goal_y is not None:
                dist = math.hypot(
                    self._goal_x - self._current_x,
                    self._goal_y - self._current_y,
                )
                self.distance_pub.publish(Float64(data=dist))
        self._publish_status(self._state)

    def _publish_status(self, text: str) -> None:
        self.status_pub.publish(String(data=text))

    def _publish_goal_pose(self) -> None:
        if self._goal_x is None or self._goal_y is None:
            return
        pose = PoseStamped()
        pose.header.stamp = self.get_clock().now().to_msg()
        pose.header.frame_id = self.map_frame
        pose.pose.position.x = self._goal_x
        pose.pose.position.y = self._goal_y
        pose.pose.orientation.w = 1.0
        self.goal_pose_pub.publish(pose)


def main(args=None) -> None:
    rclpy.init(args=args)
    node = GpsGoalBridgeNode()
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
