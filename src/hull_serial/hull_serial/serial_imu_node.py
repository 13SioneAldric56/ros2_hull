#!/usr/bin/env python3
"""ROS2 bridge: parse ESP32 binary GX frames and publish IMU + TF."""

from __future__ import annotations

import threading
import time

import rclpy
from geometry_msgs.msg import Point, Pose, PoseStamped, Quaternion, TransformStamped, Twist
from nav_msgs.msg import Odometry, Path
from rclpy.node import Node
from sensor_msgs.msg import Imu
from std_msgs.msg import Header
from tf2_ros import TransformBroadcaster

try:
    import serial
    from serial import SerialException
except ImportError as exc:
    raise ImportError('pyserial is required. Install with: pip install pyserial') from exc

from hull_serial.gx_frame_parser import GxImuFrame, GxStreamParser
from hull_serial.imu_frame_adapter import ImuFrameAdapter
from hull_serial.imu_odometry_integrator import ImuOdometryIntegrator


class GxSerialBridgeNode(Node):
    def __init__(self) -> None:
        super().__init__('gx_serial_bridge')

        self.declare_parameter('port', '/dev/ttyUSB0')
        self.declare_parameter('baudrate', 115200)
        self.declare_parameter('read_chunk_size', 256)
        self.declare_parameter('odom_frame_id', 'odom')
        self.declare_parameter('imu_frame_id', 'imu_link')
        self.declare_parameter('publish_tf', True)
        self.declare_parameter('publish_odom', True)
        self.declare_parameter('enable_position_integration', True)
        self.declare_parameter('publish_path', True)
        self.declare_parameter('path_max_poses', 1000)
        self.declare_parameter('gravity', 9.80665)
        self.declare_parameter('gravity_calib_samples', 100)
        self.declare_parameter('velocity_damping', 0.2)
        self.declare_parameter('max_velocity', 2.0)
        self.declare_parameter('bias_learning_rate', 0.03)
        self.declare_parameter('motion_accel_threshold', 0.45)
        self.declare_parameter('path_min_distance', 0.02)
        self.declare_parameter('zupt_accel_threshold', 0.2)
        self.declare_parameter('zupt_gyro_threshold', 0.12)
        self.declare_parameter('orientation_rpy_offset_deg', [0.0, -90.0, 0.0])
        self.declare_parameter('orientation_fix_order', 'post')
        self.declare_parameter('invert_orientation', False)
        self.declare_parameter('acc_remap', [0, 1, 2])
        self.declare_parameter('acc_sign', [1.0, 1.0, 1.0])
        self.declare_parameter('gyro_remap', [0, 1, 2])
        self.declare_parameter('gyro_sign', [1.0, 1.0, 1.0])
        self.declare_parameter('reconnect_interval', 2.0)
        self.declare_parameter('error_backoff', 0.5)

        self.port = self.get_parameter('port').value
        self.baudrate = int(self.get_parameter('baudrate').value)
        self.read_chunk_size = int(self.get_parameter('read_chunk_size').value)
        self.odom_frame_id = self.get_parameter('odom_frame_id').value
        self.imu_frame_id = self.get_parameter('imu_frame_id').value
        self.publish_tf = bool(self.get_parameter('publish_tf').value)
        self.publish_odom = bool(self.get_parameter('publish_odom').value)
        self.enable_position_integration = bool(
            self.get_parameter('enable_position_integration').value
        )
        self.publish_path = bool(self.get_parameter('publish_path').value)
        self.path_max_poses = int(self.get_parameter('path_max_poses').value)
        self.path_min_distance = float(self.get_parameter('path_min_distance').value)
        self.reconnect_interval = float(self.get_parameter('reconnect_interval').value)
        self.error_backoff = float(self.get_parameter('error_backoff').value)

        self.frame_adapter = self._load_frame_adapter()

        self.imu_pub = self.create_publisher(Imu, 'imu/data', 10)
        self.odom_pub = self.create_publisher(Odometry, 'odom', 10)
        self.path_pub = self.create_publisher(Path, 'imu/path', 10)
        self.tf_broadcaster = TransformBroadcaster(self)
        self.odom_integrator = ImuOdometryIntegrator(
            gravity=float(self.get_parameter('gravity').value),
            gravity_calib_samples=int(self.get_parameter('gravity_calib_samples').value),
            velocity_damping=float(self.get_parameter('velocity_damping').value),
            max_velocity=float(self.get_parameter('max_velocity').value),
            bias_learning_rate=float(self.get_parameter('bias_learning_rate').value),
            motion_accel_threshold=float(self.get_parameter('motion_accel_threshold').value),
            zupt_accel_threshold=float(self.get_parameter('zupt_accel_threshold').value),
            zupt_gyro_threshold=float(self.get_parameter('zupt_gyro_threshold').value),
        )
        self._path_msg = Path()
        self._path_msg.header.frame_id = self.odom_frame_id
        self._last_path_position = Point(x=0.0, y=0.0, z=0.0)
        self._has_path_position = False

        self.parser = GxStreamParser()
        self.serial_port: serial.Serial | None = None
        self._running = True
        self._bytes_read = 0
        self._frames_published = 0
        self._last_frame_monotonic = 0.0
        self._thread = threading.Thread(target=self._read_loop, daemon=True)
        self._thread.start()
        self.create_timer(5.0, self._report_health)

        self.get_logger().info(
            f'GX bridge on {self.port} @ {self.baudrate}, '
            f'imu_frame={self.imu_frame_id}, '
            f'publish_tf={self.publish_tf}, publish_odom={self.publish_odom}, '
            f'frame offset deg={self.frame_adapter.orientation_rpy_offset_deg} '
            f'order={self.frame_adapter.orientation_fix_order}'
        )

    def _load_frame_adapter(self) -> ImuFrameAdapter:
        offset = self.get_parameter('orientation_rpy_offset_deg').value
        fix_order = str(self.get_parameter('orientation_fix_order').value)
        if fix_order not in ('pre', 'post'):
            self.get_logger().warn(
                f'Invalid orientation_fix_order={fix_order!r}, using post'
            )
            fix_order = 'post'

        return ImuFrameAdapter(
            orientation_rpy_offset_deg=(
                float(offset[0]),
                float(offset[1]),
                float(offset[2]),
            ),
            orientation_fix_order=fix_order,  # type: ignore[arg-type]
            invert_orientation=bool(self.get_parameter('invert_orientation').value),
            acc_remap=tuple(int(v) for v in self.get_parameter('acc_remap').value),
            acc_sign=tuple(float(v) for v in self.get_parameter('acc_sign').value),
            gyro_remap=tuple(int(v) for v in self.get_parameter('gyro_remap').value),
            gyro_sign=tuple(float(v) for v in self.get_parameter('gyro_sign').value),
        )

    def _adapt_frame(self, frame: GxImuFrame) -> tuple[
        tuple[float, float, float, float],
        tuple[float, float, float],
        tuple[float, float, float],
    ]:
        orientation = self.frame_adapter.adapt_orientation(
            frame.qx,
            frame.qy,
            frame.qz,
            frame.qw,
        )
        acc = self.frame_adapter.adapt_linear_acceleration(
            frame.acc_x,
            frame.acc_y,
            frame.acc_z,
        )
        gyro = self.frame_adapter.adapt_angular_velocity(
            frame.gyro_x,
            frame.gyro_y,
            frame.gyro_z,
        )
        return orientation, acc, gyro

    def _open_serial(self) -> bool:
        if self.serial_port is not None and self.serial_port.is_open:
            return True

        try:
            self.serial_port = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=0,
            )
            self.serial_port.reset_input_buffer()
            self.get_logger().info(f'Opened serial port {self.port}')
            return True
        except (SerialException, OSError) as exc:
            self.get_logger().warn(f'Cannot open {self.port}: {exc}')
            self.serial_port = None
            return False

    def _read_loop(self) -> None:
        while self._running:
            if not self._open_serial():
                time.sleep(self.reconnect_interval)
                continue

            try:
                waiting = self.serial_port.in_waiting
                chunk = self.serial_port.read(waiting or 1)
            except (SerialException, OSError, TypeError, ValueError) as exc:
                if self._running:
                    self.get_logger().warn(f'Serial read error: {exc}')
                self._close_serial()
                time.sleep(self.error_backoff)
                continue

            if not chunk:
                time.sleep(0.001)
                continue

            self._bytes_read += len(chunk)
            for frame in self.parser.feed(chunk):
                if self._running:
                    self._publish_frame(frame)

    def _report_health(self) -> None:
        if self._frames_published > 0:
            age = time.monotonic() - self._last_frame_monotonic
            if age > 2.0:
                self.get_logger().warn(
                    f'No GX frames for {age:.1f}s on {self.port} '
                    f'(total frames={self._frames_published})'
                )
            return

        self.get_logger().warn(
            f'No /imu/data yet on {self.port}: bytes_read={self._bytes_read}. '
            'Check ESP32 power, USB cable, and that GX binary frames are being sent.'
        )

    def _close_serial(self) -> None:
        port = self.serial_port
        self.serial_port = None
        if port is not None:
            try:
                if port.is_open:
                    port.close()
            except (SerialException, OSError):
                pass

    def _publish_frame(self, frame: GxImuFrame) -> None:
        stamp = self.get_clock().now().to_msg()
        (qx, qy, qz, qw), (acc_x, acc_y, acc_z), (gyro_x, gyro_y, gyro_z) = (
            self._adapt_frame(frame)
        )
        orientation = Quaternion(x=qx, y=qy, z=qz, w=qw)

        imu_msg = Imu()
        imu_msg.header = Header(stamp=stamp, frame_id=self.imu_frame_id)
        imu_msg.orientation = orientation
        imu_msg.orientation_covariance[0] = 0.01
        imu_msg.orientation_covariance[4] = 0.01
        imu_msg.orientation_covariance[8] = 0.01
        imu_msg.angular_velocity.x = gyro_x
        imu_msg.angular_velocity.y = gyro_y
        imu_msg.angular_velocity.z = gyro_z
        imu_msg.linear_acceleration.x = acc_x
        imu_msg.linear_acceleration.y = acc_y
        imu_msg.linear_acceleration.z = acc_z
        self.imu_pub.publish(imu_msg)
        self._frames_published += 1
        self._last_frame_monotonic = time.monotonic()

        position = Point(x=0.0, y=0.0, z=0.0)
        twist = Twist()
        if self.enable_position_integration:
            sample = self.odom_integrator.update(
                timestamp_us=frame.timestamp_us,
                qx=qx,
                qy=qy,
                qz=qz,
                qw=qw,
                acc_x=acc_x,
                acc_y=acc_y,
                acc_z=acc_z,
                gyro_x=gyro_x,
                gyro_y=gyro_y,
                gyro_z=gyro_z,
            )
            if sample is not None:
                position.x = sample.position_x
                position.y = sample.position_y
                position.z = sample.position_z
                twist.linear.x = sample.velocity_x
                twist.linear.y = sample.velocity_y
                twist.linear.z = sample.velocity_z
                twist.angular.x = gyro_x
                twist.angular.y = gyro_y
                twist.angular.z = gyro_z

        if self.publish_odom:
            odom_msg = Odometry()
            odom_msg.header = Header(stamp=stamp, frame_id=self.odom_frame_id)
            odom_msg.child_frame_id = self.imu_frame_id
            odom_msg.pose.pose = Pose(position=position, orientation=orientation)
            odom_msg.twist.twist = twist
            self.odom_pub.publish(odom_msg)

        if self.publish_path and self.enable_position_integration:
            dx = position.x - self._last_path_position.x
            dy = position.y - self._last_path_position.y
            dz = position.z - self._last_path_position.z
            moved = (dx * dx + dy * dy + dz * dz) ** 0.5
            if (
                not self._has_path_position
                or moved >= self.path_min_distance
            ):
                pose_stamped = PoseStamped()
                pose_stamped.header = Header(stamp=stamp, frame_id=self.odom_frame_id)
                pose_stamped.pose = Pose(position=position, orientation=orientation)
                self._path_msg.poses.append(pose_stamped)
                if len(self._path_msg.poses) > self.path_max_poses:
                    self._path_msg.poses = self._path_msg.poses[-self.path_max_poses:]
                self._path_msg.header.stamp = stamp
                self.path_pub.publish(self._path_msg)
                self._last_path_position = Point(
                    x=position.x,
                    y=position.y,
                    z=position.z,
                )
                self._has_path_position = True

        if self.publish_tf:
            transform = TransformStamped()
            transform.header.stamp = stamp
            transform.header.frame_id = self.odom_frame_id
            transform.child_frame_id = self.imu_frame_id
            transform.transform.translation.x = position.x
            transform.transform.translation.y = position.y
            transform.transform.translation.z = position.z
            transform.transform.rotation = orientation
            self.tf_broadcaster.sendTransform(transform)

    def destroy_node(self) -> bool:
        self._running = False
        self._close_serial()
        if self._thread.is_alive():
            self._thread.join(timeout=2.0)
        return super().destroy_node()


def main(args=None) -> None:
    rclpy.init(args=args)
    node = GxSerialBridgeNode()
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
