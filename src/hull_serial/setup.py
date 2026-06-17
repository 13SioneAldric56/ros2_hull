from setuptools import find_packages, setup

package_name = 'hull_serial'

setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', ['launch/serial_imu.launch.py']),
        ('share/' + package_name + '/config', ['config/serial_imu.yaml', 'config/serial_imu.rviz', 'config/serial_imu_nav.yaml']),
    ],
    install_requires=['setuptools', 'pyserial'],
    zip_safe=True,
    maintainer='user',
    maintainer_email='user@todo.todo',
    description='Serial driver for 9-axis IMU and odometry',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'serial_imu_node = hull_serial.serial_imu_node:main',
        ],
    },
)
