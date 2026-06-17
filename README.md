# ROS2 Hull Workspace

基于 ROS2 Humble 的 **GX 串口桥接**工作区：从 ESP32 接收二进制 GX 帧，解析后发布 ROS2 IMU 与 TF。

## 架构

```
ESP32 (gx_output.c)                PC (hull_serial)
┌─────────────────┐   二进制 GX帧   ┌──────────────────┐
│ DDM360B 九轴罗盘 │ ──────────────> │ gx_serial_bridge │
│ UART2 GPIO47    │   /dev/ttyUSB0  │                  │
└─────────────────┘   115200 8N1    └────────┬─────────┘
                                             │
                         /imu/data (Imu)     │
                         /odom (Odometry)    │
                         TF odom→imu_link    ▼
```

ESP32 通过 USB 串口发送 **57 字节二进制 GX 帧**（非文本日志、非 ROS2 原生消息）。  
PC 端 `gx_serial_bridge` 负责帧同步、校验、解析，再发布标准 ROS2 话题。

## 项目结构

```
ros2_hull/
├── src/hull_serial/
│   ├── hull_serial/
│   │   ├── gx_frame_parser.py    # GX 二进制帧解析（与 ESP32 对齐）
│   │   └── serial_imu_node.py    # ROS2 桥接节点
│   ├── config/serial_imu.yaml
│   └── launch/serial_imu.launch.py
```

## GX 帧格式（57 字节，小端）

| 偏移 | 长度 | 字段 |
|------|------|------|
| 0 | 1 | 魔数 `0x47` ('G') |
| 1 | 1 | 魔数 `0x58` ('X') |
| 2 | 1 | 版本 `0x01` |
| 3 | 1 | 类型 `0x01` (IMU+TF) |
| 4 | 4 | 序号 `uint32` |
| 8 | 8 | 时间戳 `uint64` (ESP32 us) |
| 16 | 16 | 四元数 x,y,z,w `float32` |
| 32 | 12 | 角速度 rad/s `float32×3` |
| 44 | 12 | 线加速度 m/s² `float32×3` |
| 56 | 1 | 校验：byte[2..55] 异或 |

坐标系与 ESP32 固件一致：`odom` → `imu_link`。

## 依赖

```bash
sudo apt install ros-humble-sensor-msgs ros-humble-nav-msgs ros-humble-tf2-ros
pip3 install pyserial
```

## 构建

```bash
cd ~/ros2_hull
source /opt/ros/humble/setup.bash
colcon build --symlink-install
source install/setup.bash
```

## 运行

```bash
# 确保串口权限
sudo usermod -aG dialout $USER   # 需重新登录

ros2 launch hull_serial serial_imu.launch.py
```

指定串口：

```bash
ros2 launch hull_serial serial_imu.launch.py port:=/dev/ttyUSB0
```

## 发布话题

| 话题 | 类型 | 说明 |
|------|------|------|
| `/imu/data` | `sensor_msgs/Imu` | `frame_id: imu_link` |
| `/odom` | `nav_msgs/Odometry` | `odom` → `imu_link`，仅姿态 |
| TF | `odom` → `imu_link` | 与 ESP32 GX 帧同步 @ 100Hz |

## 查看数据

```bash
ros2 topic echo /imu/data
ros2 topic hz /imu/data
ros2 run tf2_tools view_frames
```

## 说明

- ESP32 日志中的 `9-axis #... roll=...` 是 **调试文本**，仅 idf monitor 可见；串口线上实际是 **GX 二进制帧**。
- 桥接节点使用 **字节流读取**（非 `readline`），避免把二进制数据当文本解析导致读错误。

# 终端 1：主栈（保持运行）
cd ~/ros2_hull && source install/setup.bash
ros2 launch hull_navigation navigation.launch.py

# 终端 2：发目标
source ~/ros2_hull/install/setup.bash
ros2 run hull_navigation send_nav_goal 22.405100 113.536800

# 终端 3：看距离和航向差
source ~/ros2_hull/install/setup.bash
ros2 topic echo /navigation/distance_remaining
ros2 topic echo /navigation/heading_error_deg