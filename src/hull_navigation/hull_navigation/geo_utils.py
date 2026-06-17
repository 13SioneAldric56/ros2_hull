"""Shared geodetic and heading utilities for hull navigation."""

from __future__ import annotations

import math

from geometry_msgs.msg import Quaternion

EARTH_RADIUS_KM = 6378.137


def rad(deg: float) -> float:
    return deg * math.pi / 180.0


def deg(rad_val: float) -> float:
    return rad_val * 180.0 / math.pi


def lla_to_local_m(
    origin_lat: float,
    origin_lon: float,
    origin_alt: float,
    lat: float,
    lon: float,
    alt: float,
) -> tuple[float, float, float]:
    """Same local projection as wheeltec_gps_path/src/gps_path.cpp."""
    rad_lat1 = rad(origin_lat)
    rad_lon1 = rad(origin_lon)
    rad_lat2 = rad(lat)
    rad_lon2 = rad(lon)

    delta_lat = rad_lat2 - rad_lat1
    if delta_lat > 0.0:
        x = -2.0 * math.asin(
            math.sqrt(
                math.sin(delta_lat / 2.0) ** 2
                + math.cos(rad_lat1) * math.cos(rad_lat2) * math.sin(0.0) ** 2
            )
        )
    else:
        x = 2.0 * math.asin(
            math.sqrt(
                math.sin(delta_lat / 2.0) ** 2
                + math.cos(rad_lat1) * math.cos(rad_lat2) * math.sin(0.0) ** 2
            )
        )
    x *= EARTH_RADIUS_KM * 1000.0

    delta_long = rad_lon2 - rad_lon1
    if delta_long > 0.0:
        y = 2.0 * math.asin(
            math.sqrt(
                math.sin(0.0) ** 2
                + math.cos(rad_lat2) * math.cos(rad_lat2) * math.sin(delta_long / 2.0) ** 2
            )
        )
    else:
        y = -2.0 * math.asin(
            math.sqrt(
                math.sin(0.0) ** 2
                + math.cos(rad_lat2) * math.cos(rad_lat2) * math.sin(delta_long / 2.0) ** 2
            )
        )
    y *= EARTH_RADIUS_KM * 1000.0

    z = alt - origin_alt
    return x, y, z


def quat_to_yaw(q: Quaternion) -> float:
    siny_cosp = 2.0 * (q.w * q.z + q.x * q.y)
    cosy_cosp = 1.0 - 2.0 * (q.y * q.y + q.z * q.z)
    return math.atan2(siny_cosp, cosy_cosp)


def normalize_angle(angle: float) -> float:
    while angle > math.pi:
        angle -= 2.0 * math.pi
    while angle < -math.pi:
        angle += 2.0 * math.pi
    return angle


def bearing_rad(from_x: float, from_y: float, to_x: float, to_y: float) -> float:
    return math.atan2(to_y - from_y, to_x - from_x)


def distance_m(x1: float, y1: float, x2: float, y2: float) -> float:
    dx = x2 - x1
    dy = y2 - y1
    return math.hypot(dx, dy)
