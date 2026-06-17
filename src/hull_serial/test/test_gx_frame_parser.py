from hull_serial.gx_frame_parser import (
    GX_FRAME_SIZE,
    GxStreamParser,
    build_gx_frame,
    gx_frame_checksum,
    parse_gx_frame,
)


def _sample_frame(seq: int = 42) -> bytes:
    return build_gx_frame(
        seq=seq,
        timestamp_us=1_234_567,
        qx=0.1,
        qy=0.2,
        qz=0.3,
        qw=0.9,
        gyro_x=0.01,
        gyro_y=0.02,
        gyro_z=0.03,
        acc_x=0.1,
        acc_y=0.2,
        acc_z=9.8,
    )


def test_build_and_parse_roundtrip():
    raw = _sample_frame()
    assert len(raw) == GX_FRAME_SIZE
    assert raw[0] == 0x47
    assert raw[1] == 0x58

    frame = parse_gx_frame(raw)
    assert frame is not None
    assert frame.seq == 42
    assert frame.timestamp_us == 1_234_567
    assert abs(frame.qx - 0.1) < 1e-6
    assert abs(frame.acc_z - 9.8) < 1e-6


def test_checksum_matches_esp32_rule():
    raw = bytearray(_sample_frame())
    raw[56] = 0
    assert gx_frame_checksum(raw) == _sample_frame()[56]


def test_stream_parser_resyncs_after_garbage():
    parser = GxStreamParser()
    payload = b'\xff\xfe' + _sample_frame(1) + b'\x00\x11' + _sample_frame(2)

    frames = parser.feed(payload)
    assert len(frames) == 2
    assert frames[0].seq == 1
    assert frames[1].seq == 2


def test_invalid_checksum_rejected():
    raw = bytearray(_sample_frame())
    raw[56] ^= 0xFF
    assert parse_gx_frame(bytes(raw)) is None
