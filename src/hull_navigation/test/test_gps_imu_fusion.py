from hull_navigation.geo_utils import lla_to_local_m


def test_lla_to_local_origin_is_zero():
    x, y, z = lla_to_local_m(22.4, 113.5, 10.0, 22.4, 113.5, 10.0)
    assert abs(x) < 1e-6
    assert abs(y) < 1e-6
    assert abs(z) < 1e-6


def test_lla_to_local_moves_north_and_east():
    x1, y1, _ = lla_to_local_m(22.0, 113.0, 0.0, 22.001, 113.0, 0.0)
    x2, y2, _ = lla_to_local_m(22.0, 113.0, 0.0, 22.0, 113.001, 0.0)
    assert abs(x1) > 50.0
    assert abs(y2) > 50.0
