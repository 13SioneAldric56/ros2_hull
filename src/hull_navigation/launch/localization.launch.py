from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition, UnlessCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os


def generate_launch_description():
    hull_nav_share = get_package_share_directory('hull_navigation')
    ekf_config = os.path.join(hull_nav_share, 'config', 'ekf.yaml')
    nav_config = os.path.join(hull_nav_share, 'config', 'navigation.yaml')

    stern_offset = LaunchConfiguration('stern_offset_m')
    use_nav2 = LaunchConfiguration('use_nav2')

    return LaunchDescription([
        DeclareLaunchArgument(
            'stern_offset_m',
            default_value='-2.0',
            description='IMU/GPS offset from base_link center along +X (m). Stern = negative.',
        ),
        DeclareLaunchArgument(
            'use_nav2',
            default_value='false',
            description='Use dual EKF + navsat (Nav2). Otherwise gps_imu_fusion_node.',
        ),
        # Lightweight fusion for gps_navigator (no dual EKF / navsat).
        Node(
            package='hull_navigation',
            executable='gps_imu_fusion_node',
            name='gps_imu_fusion',
            output='screen',
            parameters=[nav_config],
            condition=UnlessCondition(use_nav2),
        ),
        # Full robot_localization stack for Nav2.
        Node(
            package='robot_localization',
            executable='ekf_node',
            name='ekf_filter_node_odom',
            output='screen',
            parameters=[ekf_config],
            remappings=[('odometry/filtered', '/odometry/local')],
            condition=IfCondition(use_nav2),
        ),
        Node(
            package='robot_localization',
            executable='ekf_node',
            name='ekf_filter_node_map',
            output='screen',
            parameters=[ekf_config],
            remappings=[('odometry/filtered', '/odometry/global')],
            condition=IfCondition(use_nav2),
        ),
        Node(
            package='robot_localization',
            executable='navsat_transform_node',
            name='navsat_transform',
            output='screen',
            parameters=[ekf_config],
            remappings=[
                ('imu', '/imu/data'),
                ('gps/fix', '/fix'),
                ('odometry/filtered', '/odometry/global'),
                ('odometry/gps', '/odometry/gps'),
            ],
            condition=IfCondition(use_nav2),
        ),
        Node(
            package='hull_navigation',
            executable='gps_velocity_adapter_node',
            name='gps_velocity_adapter',
            output='screen',
            parameters=[nav_config],
            condition=IfCondition(use_nav2),
        ),
        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            name='base_link_to_imu_link',
            arguments=[
                stern_offset, '0', '0',
                '0', '0', '0',
                'base_link', 'imu_link',
            ],
        ),
        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            name='base_link_to_gps',
            arguments=[
                stern_offset, '0', '0',
                '0', '0', '0',
                'base_link', 'gps',
            ],
        ),
    ])
