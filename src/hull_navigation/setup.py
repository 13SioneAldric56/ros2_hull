from setuptools import find_packages, setup

package_name = 'hull_navigation'

setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', ['launch/navigation.launch.py']),
        ('share/' + package_name + '/config', ['config/navigation.yaml', 'config/hardware_ports.yaml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='user',
    maintainer_email='user@todo.todo',
    description='GPS + IMU fusion for hull navigation',
    license='MIT',
    entry_points={
        'console_scripts': [
            'gps_imu_fusion_node = hull_navigation.gps_imu_fusion_node:main',
            'gps_navigator_node = hull_navigation.gps_navigator_node:main',
            'send_nav_goal = hull_navigation.send_nav_goal:main',
        ],
    },
)
