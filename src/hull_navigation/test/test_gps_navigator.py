from hull_navigation.geo_utils import bearing_rad, distance_m, normalize_angle, quat_to_yaw
from geometry_msgs.msg import Quaternion


def test_distance_and_bearing():
    dist = distance_m(0.0, 0.0, 3.0, 4.0)
    assert abs(dist - 5.0) < 1e-6
    bearing = bearing_rad(0.0, 0.0, 1.0, 0.0)
    assert abs(bearing) < 1e-6


def test_normalize_angle():
    import math
    assert abs(normalize_angle(3.0 * math.pi) - math.pi) < 1e-6


def test_quat_to_yaw():
    q = Quaternion(x=0.0, y=0.0, z=0.7071068, w=0.7071068)
    import math
    yaw = quat_to_yaw(q)
    assert abs(yaw - math.pi / 2.0) < 0.01
