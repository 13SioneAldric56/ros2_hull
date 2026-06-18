from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os


def generate_launch_description():
    pkg_share = get_package_share_directory('hull_serial')
    default_config = os.path.join(pkg_share, 'config', 'serial_imu.yaml')
    default_rviz_config = os.path.join(pkg_share, 'config', 'serial_imu.rviz')

    return LaunchDescription([
        DeclareLaunchArgument(
            'config_file',
            default_value=default_config,
            description='Path to serial IMU parameter file',
        ),
        DeclareLaunchArgument(
            'port',
            default_value='/dev/ttyUSB0',
            description='ESP32 serial port for GX binary IMU frames',
        ),
        DeclareLaunchArgument(
            'use_rviz',
            default_value='false',
            description='Launch RViz2 with IMU attitude visualization',
        ),
        DeclareLaunchArgument(
            'rviz_config',
            default_value=default_rviz_config,
            description='Path to RViz2 config file',
        ),
        Node(
            package='hull_serial',
            executable='serial_imu_node',
            name='gx_serial_bridge',
            output='screen',
            parameters=[
                LaunchConfiguration('config_file'),
                {'port': LaunchConfiguration('port')},
            ],
        ),
        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            output='screen',
            arguments=['-d', LaunchConfiguration('rviz_config')],
            condition=IfCondition(LaunchConfiguration('use_rviz')),
        ),
    ])
