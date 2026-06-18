from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, TimerAction
from launch.conditions import IfCondition, UnlessCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os


def generate_launch_description():
    hull_nav_share = get_package_share_directory('hull_navigation')
    hull_serial_share = get_package_share_directory('hull_serial')
    nmea_share = get_package_share_directory('nmea_navsat_driver')
    gps_path_share = get_package_share_directory('wheeltec_gps_path')

    nav_config = os.path.join(hull_nav_share, 'config', 'navigation.yaml')
    imu_nav_config = os.path.join(hull_serial_share, 'config', 'serial_imu_nav.yaml')
    nmea_config = os.path.join(nmea_share, 'config', 'nmea_serial_driver.yaml')

    return LaunchDescription([
        DeclareLaunchArgument(
            'gps_port',
            default_value='/dev/ttyACM0',
            description='GPS NMEA serial port (9600)',
        ),
        DeclareLaunchArgument(
            'imu_port',
            default_value='/dev/ttyUSB0',
            description='ESP32 serial port for GX binary IMU frames (115200)',
        ),
        DeclareLaunchArgument(
            'stern_offset_m',
            default_value='-2.0',
            description='IMU/GPS stern offset from base_link center along +X (m)',
        ),
        DeclareLaunchArgument(
            'use_gps_path_viz',
            default_value='true',
            description='Publish /gps_path from raw GPS for map comparison',
        ),
        DeclareLaunchArgument(
            'use_nav2',
            default_value='false',
            description='Use Nav2 + gps_goal_bridge for /cmd_vel (default: gps_navigator_node)',
        ),
        DeclareLaunchArgument(
            'use_mapviz',
            default_value='true',
            description='Launch Mapviz with offline satellite tiles on local map',
        ),
        DeclareLaunchArgument(
            'tile_root',
            default_value='/home/sione/ros2_hull/maps/bing_tiles',
            description='Root directory of offline Bing map tiles',
        ),
        Node(
            package='nmea_navsat_driver',
            executable='nmea_serial_driver',
            name='nmea_navsat_driver',
            output='screen',
            parameters=[
                nmea_config,
                {
                    'port': LaunchConfiguration('gps_port'),
                    # Use GGA for /fix (includes altitude; required by navsat_transform).
                    # RMC sentences still publish /vel (SOG/COG) when VTG is unavailable.
                    'useRMC': False,
                },
            ],
        ),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(hull_serial_share, 'launch', 'serial_imu.launch.py')
            ),
            launch_arguments={
                'config_file': imu_nav_config,
                'port': LaunchConfiguration('imu_port'),
                'use_rviz': 'false',
            }.items(),
        ),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(hull_nav_share, 'launch', 'localization.launch.py')
            ),
            launch_arguments={
                'stern_offset_m': LaunchConfiguration('stern_offset_m'),
                'use_nav2': LaunchConfiguration('use_nav2'),
            }.items(),
        ),
        TimerAction(
            period=8.0,
            actions=[
                IncludeLaunchDescription(
                    PythonLaunchDescriptionSource(
                        os.path.join(hull_nav_share, 'launch', 'nav2_open_water.launch.py')
                    ),
                ),
            ],
            condition=IfCondition(LaunchConfiguration('use_nav2')),
        ),
        Node(
            package='hull_navigation',
            executable='gps_goal_bridge_node',
            name='gps_goal_bridge',
            output='screen',
            parameters=[nav_config],
            condition=IfCondition(LaunchConfiguration('use_nav2')),
        ),
        Node(
            package='hull_navigation',
            executable='gps_navigator_node',
            name='gps_navigator',
            output='screen',
            parameters=[nav_config],
            condition=UnlessCondition(LaunchConfiguration('use_nav2')),
        ),
        Node(
            package='hull_navigation',
            executable='cmd_vel_stub_node',
            name='cmd_vel_stub',
            output='screen',
            parameters=[nav_config],
        ),
        Node(
            package='wheeltec_gps_path',
            executable='gps_path',
            name='GpsPath',
            output='screen',
            remappings=[('/gps_topic', '/fix')],
            condition=IfCondition(LaunchConfiguration('use_gps_path_viz')),
        ),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(gps_path_share, 'launch', 'mapviz_path.launch.py')
            ),
            launch_arguments={
                'tile_root': LaunchConfiguration('tile_root'),
            }.items(),
            condition=IfCondition(LaunchConfiguration('use_mapviz')),
        ),
    ])
