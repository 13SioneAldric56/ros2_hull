from setuptools import find_packages, setup
import os
from glob import glob

package_name = 'hull_navigation'

setup(
    name=package_name,
    version='0.2.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (
            'share/' + package_name + '/launch',
            glob('launch/*.launch.py'),
        ),
        (
            'share/' + package_name + '/config',
            glob('config/*.yaml'),
        ),
        (
            'share/' + package_name + '/scripts',
            glob('scripts/*.sh'),
        ),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='user',
    maintainer_email='user@todo.todo',
    description='GPS + IMU localization and Nav2 open-water navigation for hull',
    license='MIT',
    entry_points={
        'console_scripts': [
            'gps_imu_fusion_node = hull_navigation.gps_imu_fusion_node:main',
            'gps_navigator_node = hull_navigation.gps_navigator_node:main',
            'gps_velocity_adapter_node = hull_navigation.gps_velocity_adapter_node:main',
            'gps_goal_bridge_node = hull_navigation.gps_goal_bridge_node:main',
            'cmd_vel_stub_node = hull_navigation.cmd_vel_stub_node:main',
            'send_nav_goal = hull_navigation.send_nav_goal:main',
        ],
    },
)
