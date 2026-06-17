import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess
from launch.substitutions import LaunchConfiguration
import launch_ros.actions


def generate_launch_description():
    pkg_share = get_package_share_directory('wheeltec_gps_path')
    config_file = os.path.join(pkg_share, 'config', 'mapviz_local.mvc')
    blank_tile = os.path.join(pkg_share, 'config', 'blank_tile.jpg')
    tile_server_script = os.path.normpath(
        os.path.join(pkg_share, '..', '..', 'lib', 'wheeltec_gps_path', 'bing_tile_server.py')
    )

    default_tile_root = '/home/sione/ros2_hull/maps/bing_tiles'

    return LaunchDescription([
        DeclareLaunchArgument(
            'tile_root',
            default_value=default_tile_root,
            description='Root directory of offline Bing tiles',
        ),
        DeclareLaunchArgument(
            'tile_port',
            default_value='8080',
            description='Port for the local Bing tile server',
        ),
        ExecuteProcess(
            cmd=[
                'python3',
                tile_server_script,
                '--root', LaunchConfiguration('tile_root'),
                '--blank-tile', blank_tile,
                '--port', LaunchConfiguration('tile_port'),
            ],
            output='screen',
        ),
        launch_ros.actions.Node(
            package='mapviz',
            executable='mapviz',
            name='mapviz',
            parameters=[{'config': config_file}],
        ),
        launch_ros.actions.Node(
            package='swri_transform_util',
            executable='initialize_origin.py',
            name='initialize_origin',
            parameters=[
                {'local_xy_frame': 'map'},
                {'local_xy_origin': 'auto'},
                {'local_xy_navsatfix_topic': 'fix'},
            ],
            remappings=[('fix', '/fix')],
        ),
        launch_ros.actions.Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            name='swri_transform',
            arguments=['0', '0', '0', '0', '0', '0', 'map', 'origin'],
        ),
    ])
