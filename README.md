# ROS2 Hull Workspace

基于 ROS2 Humble 的船体 **GPS + IMU 定位与导航**工作区：串口采集 GPS/IMU，融合位姿，Mapviz 本地地图可视化，支持经纬度目标导航与 `/cmd_vel` 输出。

## 硬件连接

| 设备 | 串口 | 波特率 | 协议 |
|------|------|--------|------|
| GPS 卫星定位模块 | `/dev/ttyACM0` | 9600 | NMEA |
| ESP32（DDM360B 九轴） | `/dev/ttyUSB0` | 115200 | GX 57 字节二进制帧 |

```
GPS ──► ttyACM0 ──► nmea_navsat_driver ──► /fix
ESP32 ──► ttyUSB0 ──► gx_serial_bridge ──► /imu/data
```

首次使用需串口权限：

```bash
sudo usermod -aG dialout $USER   # 需重新登录
```

## 项目结构

```
ros2_hull/
├── src/
│   ├── hull_serial/          # ESP32 GX 帧桥接 → /imu/data
│   ├── hull_navigation/      # 融合、导航、Nav2、cmd_vel 占位
│   ├── nmea_navsat_driver/   # GPS NMEA 驱动 → /fix, /vel
│   ├── nmea_msgs/
│   └── wheeltec_gps_path/    # GPS 轨迹 + Mapviz 瓦片
├── maps/bing_tiles/          # 离线卫星瓦片（可选）
└── scripts/udev/             # 可选 udev 规则
```

## 系统架构

### 默认模式（`gps_navigator`，轻量导航）

```
/fix (GPS 位置)  ──┐
                   ├──► gps_imu_fusion_node ──► /odometry/global
/imu/data (姿态) ──┘         TF map→base_link
                              │
/navigation/goal (目标经纬度) ─┴──► gps_navigator_node ──► /cmd_vel
                                        │
                                        ├── /navigation/distance_remaining
                                        ├── /navigation/bearing_deg
                                        ├── /navigation/heading_error_deg
                                        └── /navigation/current_heading_deg
                                              │
                                              ▼
                                    cmd_vel_stub_node（看门狗 + 日志）
```

融合方式：**松耦合直接拼接**（GPS 提供位置，IMU 四元数提供航向），非卡尔曼滤波。

### 可选模式（`use_nav2:=true`，开阔水域 Nav2）

```
双 EKF + navsat_transform + gps_velocity_adapter
    → /odometry/global
gps_goal_bridge（/navigation/goal → Nav2 navigate_to_pose）
    → Nav2 规划/控制 → /cmd_vel
```

需安装 `robot_localization` 与 Nav2 相关包。

## 依赖

```bash
# ROS2 基础
sudo apt install ros-humble-sensor-msgs ros-humble-nav-msgs ros-humble-tf2-ros \
  ros-humble-mapviz ros-humble-swri-transform-util

# 导航栈（默认模式）
pip3 install pyserial

# Nav2 模式（可选）
sudo apt install ros-humble-robot-localization \
  ros-humble-nav2-bringup ros-humble-nav2-regulated-pure-pursuit-controller \
  ros-humble-nav2-navfn-planner
```

## 构建

```bash
cd ~/ros2_hull
source /opt/ros/humble/setup.bash
colcon build --symlink-install
source install/setup.bash
```

## 快速开始

### 终端 1：启动完整栈（GPS + IMU + 融合 + Mapviz + 导航）

```bash
cd ~/ros2_hull
source install/setup.bash

# 若 ros2 topic echo 无输出，可设置（避免 FastDDS SHM 问题）
export FASTDDS_BUILTIN_TRANSPORTS=UDPv4

ros2 launch hull_navigation navigation.launch.py
```

默认启动：GPS 驱动、IMU 桥接、融合、Mapviz、`gps_navigator`、`cmd_vel_stub`。

等待日志出现 `GPS origin` 与 `IMU orientation available` 后再发目标。

### 终端 2：发送目标经纬度

```bash
source ~/ros2_hull/install/setup.bash
export FASTDDS_BUILTIN_TRANSPORTS=UDPv4

# 方式 A：命令行工具
ros2 run hull_navigation send_nav_goal 22.405100 113.536800

# 方式 B：脚本（自动 source 工作区）
bash ~/ros2_hull/src/hull_navigation/scripts/send_goal.sh 22.405100 113.536800

# 方式 C：直接发布话题
ros2 topic pub --once /navigation/goal sensor_msgs/NavSatFix \
  "{latitude: 22.405100, longitude: 113.536800, altitude: 0.0}"

# 取消导航
ros2 topic pub --once /navigation/cancel std_msgs/msg/Empty "{}"
```

### 终端 3：查看距离与航向

```bash
source ~/ros2_hull/install/setup.bash
export FASTDDS_BUILTIN_TRANSPORTS=UDPv4

ros2 topic echo /navigation/distance_remaining   # 剩余距离 (m)
ros2 topic echo /navigation/bearing_deg          # 目标方位角 (°)
ros2 topic echo /navigation/heading_error_deg    # 航向偏差 (°)
ros2 topic echo /navigation/current_heading_deg  # 当前船头航向 (°)
ros2 topic echo /navigation/status               # 综合状态
ros2 topic echo /cmd_vel                         # 速度指令
```

状态示例：`NAVIGATING dist=187.0m bearing=107° heading_err=15°`

- **bearing**：当前位置指向目标的方向
- **heading_err**：还需转多少度对准目标（`≈ bearing - current_heading`）
- **current_heading**：来自 IMU 四元数（`/imu/data`），非 GPS 航向

### 验证传感器

```bash
ros2 topic hz /fix              # ~1 Hz
ros2 topic hz /imu/data         # ~100 Hz（必须为 0 则航向卡在 0°）
ros2 topic hz /odometry/global  # 融合位姿
ros2 run tf2_tools view_frames  # 期望 map → base_link → imu_link
```

## Launch 参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `gps_port` | `/dev/ttyACM0` | GPS 串口 |
| `imu_port` | `/dev/ttyUSB0` | ESP32 串口 |
| `stern_offset_m` | `-2.0` | IMU/GPS 相对 `base_link` 的船尾偏移 (m) |
| `use_mapviz` | `true` | 启动 Mapviz 本地地图 |
| `use_gps_path_viz` | `true` | 发布 `/gps_path` |
| `use_nav2` | `false` | `true` 时改用 Nav2 + `gps_goal_bridge` |

```bash
ros2 launch hull_navigation navigation.launch.py \
  gps_port:=/dev/ttyACM0 \
  imu_port:=/dev/ttyUSB0 \
  use_mapviz:=true
```

## Mapviz 图层

| 图层 | 话题 | 说明 |
|------|------|------|
| GPS Fix | `/fix` | 绿色点 |
| GPS Path | `/gps_path` | 红色轨迹 |
| Fused Path | `/fused_path` | 蓝色融合轨迹 |
| Nav Plan | `/plan` | 黄色导航计划线 |
| Nav Goal | `/navigation/goal_pose` | 紫色目标点 |

瓦片目录 `~/ros2_hull/maps/bing_tiles/` 为空时底图为灰色占位，不影响定位导航。

## 主要话题

### 传感器

| 话题 | 类型 | 说明 |
|------|------|------|
| `/fix` | `sensor_msgs/NavSatFix` | GPS 经纬度 |
| `/vel` | `geometry_msgs/TwistStamped` | GPS 地速/航迹向 |
| `/imu/data` | `sensor_msgs/Imu` | IMU 姿态 + 角速度 + 加速度 |

### 定位

| 话题 | 类型 | 说明 |
|------|------|------|
| `/odometry/global` | `nav_msgs/Odometry` | 融合位姿（默认模式） |
| `/fused_path` | `nav_msgs/Path` | 融合历史轨迹 |
| TF | `map → base_link → imu_link` | 位姿变换 |

### 导航

| 话题 | 类型 | 方向 | 说明 |
|------|------|------|------|
| `/navigation/goal` | `sensor_msgs/NavSatFix` | 输入 | 目标经纬度 |
| `/navigation/cancel` | `std_msgs/Empty` | 输入 | 取消导航 |
| `/navigation/status` | `std_msgs/String` | 输出 | IDLE / NAVIGATING / ARRIVED |
| `/navigation/distance_remaining` | `std_msgs/Float64` | 输出 | 剩余距离 (m) |
| `/navigation/bearing_deg` | `std_msgs/Float64` | 输出 | 目标方位 (°) |
| `/navigation/heading_error_deg` | `std_msgs/Float64` | 输出 | 航向偏差 (°) |
| `/navigation/current_heading_deg` | `std_msgs/Float64` | 输出 | 当前航向 (°) |
| `/cmd_vel` | `geometry_msgs/Twist` | 输出 | 线速度 + 角速度指令 |

## 关键配置（`config/navigation.yaml`）

| 节点 | 参数 | 默认 |
|------|------|------|
| `gps_navigator` | `publish_cmd_vel` | `true` |
| `gps_navigator` | `max_linear_speed` | 0.5 m/s |
| `gps_navigator` | `max_angular_speed` | 1.0 rad/s |
| `gps_navigator` | `arrival_radius_m` | 2.0 m |
| `cmd_vel_stub` | `watchdog_timeout_s` | 0.5 s |

## 可选：Nav2 开阔水域导航

```bash
ros2 launch hull_navigation navigation.launch.py use_nav2:=true
```

此模式使用双 EKF + `navsat_transform` 融合，由 `gps_goal_bridge` 将 `/navigation/goal` 转为 Nav2 `navigate_to_pose`。

## 仅 IMU 桥接（调试）

不启动 GPS/导航，只读 ESP32 GX 帧：

```bash
ros2 launch hull_serial serial_imu.launch.py port:=/dev/ttyUSB0
```

| 话题 | 类型 | 说明 |
|------|------|------|
| `/imu/data` | `sensor_msgs/Imu` | `frame_id: imu_link` |
| `/odom` | `nav_msgs/Odometry` | 仅 standalone 配置启用 |
| TF | `odom → imu_link` | 仅 standalone 配置启用 |

导航模式下 `serial_imu_nav.yaml` 关闭 IMU 自身里程计，避免与融合冲突。

## GX 帧格式（57 字节，小端）

| 偏移 | 长度 | 字段 |
|------|------|------|
| 0–1 | 2 | 魔数 `GX` (`0x47 0x58`) |
| 2 | 1 | 版本 `0x01` |
| 3 | 1 | 类型 `0x01` (IMU+TF) |
| 4 | 4 | 序号 `uint32` |
| 8 | 8 | 时间戳 `uint64` (ESP32 µs) |
| 16 | 16 | 四元数 x,y,z,w `float32` |
| 32 | 12 | 角速度 rad/s `float32×3` |
| 44 | 12 | 线加速度 m/s² `float32×3` |
| 56 | 1 | 校验：byte[2..55] 异或 |

ESP32 日志中的 `9-axis #... roll=...` 是调试文本；串口线上为 **GX 二进制帧**，PC 端用字节流解析（非 `readline`）。

## 常见问题

| 现象 | 原因 | 处理 |
|------|------|------|
| `heading_err ≈ bearing` 且转动不变 | `/imu/data` 无数据，航向恒为 0° | `ros2 topic hz /imu/data` 确认 ~100 Hz |
| `ros2 topic echo` 无输出 | 未 source 工作区或 FastDDS SHM | `source install/setup.bash`，设置 `FASTDDS_BUILTIN_TRANSPORTS=UDPv4` |
| 发目标后无反应 | GPS 原点未建立 | 等 launch 出现 `GPS origin` 后再发 |
| Mapviz 灰底图 | 无离线瓦片 | 下载 Bing 瓦片到 `maps/bing_tiles/{z}/{y}/{x}.jpg` |
