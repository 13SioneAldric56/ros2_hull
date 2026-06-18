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
export FASTDDS_BUILTIN_TRANSPORTS=UDPv4   # 避免 SHM 导致 ros2 topic echo 读不到
ros2 launch hull_navigation navigation.launch.py

# 终端 2：发目标（需先 source 工作区）
source ~/ros2_hull/install/setup.bash
export FASTDDS_BUILTIN_TRANSPORTS=UDPv4
ros2 run hull_navigation send_nav_goal 22.405100 113.536800

# 或使用自带环境脚本（无需手动 source）：
bash ~/ros2_hull/src/hull_navigation/scripts/send_goal.sh 22.405100 113.536800

# 取消导航
ros2 topic pub --once /navigation/cancel std_msgs/msg/Empty "{}"

# 终端 3：看距离和状态
source ~/ros2_hull/install/setup.bash
export FASTDDS_BUILTIN_TRANSPORTS=UDPv4
ros2 topic echo /navigation/distance_remaining
ros2 topic echo /navigation/status
ros2 topic echo /cmd_vel
```

## GPS 导航（默认：gps_navigator_node）

默认使用轻量 **gps_navigator_node** 直接输出 `/cmd_vel`（线速度 `linear.x` + 角速度 `angular.z`），不依赖 Nav2 控制器。

### 架构（默认 gps_navigator）

```
/fix + /imu/data → gps_imu_fusion_node → /odometry/global + TF map→base_link
    → gps_navigator_node → /cmd_vel → cmd_vel_stub
/navigation/goal (NavSatFix) → gps_navigator_node
```

Nav2 模式（`use_nav2:=true`）仍使用双 EKF + navsat_transform。

### 关键参数（`config/navigation.yaml`）

| 节点 | 参数 | 默认 |
|------|------|------|
| `gps_navigator` | `publish_cmd_vel` | `true` |
| `gps_navigator` | `max_linear_speed` | 0.5 m/s |
| `gps_navigator` | `max_angular_speed` | 1.0 rad/s |
| `gps_navigator` | `arrival_radius_m` | 2.0 m |
| `cmd_vel_stub` | `watchdog_timeout_s` | 0.5 s |

### 可选：Nav2 开阔水域导航

若需 Nav2 规划/跟踪，启动时加 `use_nav2:=true`（需安装 Nav2 依赖）：

```bash
ros2 launch hull_navigation navigation.launch.py use_nav2:=true
```