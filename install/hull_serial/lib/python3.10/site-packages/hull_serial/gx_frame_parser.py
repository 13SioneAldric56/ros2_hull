"""Parse binary GX frames from ESP32 gx_output (57-byte IMU+TF packets)."""

from __future__ import annotations

import struct
from dataclasses import dataclass
from typing import Optional

GX_FRAME_MAGIC_0 = 0x47
GX_FRAME_MAGIC_1 = 0x58
GX_FRAME_VERSION = 0x01
GX_FRAME_TYPE_IMU_TF = 0x01
GX_FRAME_SIZE = 57

_FRAME_HEADER = struct.Struct('<2sBBIQ4f3f3f')


@dataclass
class GxImuFrame:
    seq: int
    timestamp_us: int
    qx: float
    qy: float
    qz: float
    qw: float
    gyro_x: float
    gyro_y: float
    gyro_z: float
    acc_x: float
    acc_y: float
    acc_z: float


def gx_frame_checksum(frame: bytes) -> int:
    checksum = 0
    for value in frame[2:GX_FRAME_SIZE - 1]:
        checksum ^= value
    return checksum


def build_gx_frame(
    seq: int,
    timestamp_us: int,
    qx: float,
    qy: float,
    qz: float,
    qw: float,
    gyro_x: float,
    gyro_y: float,
    gyro_z: float,
    acc_x: float,
    acc_y: float,
    acc_z: float,
) -> bytes:
    """Build a GX frame byte-for-byte compatible with ESP32 gx_output.c."""
    frame = bytearray(GX_FRAME_SIZE)
    frame[0] = GX_FRAME_MAGIC_0
    frame[1] = GX_FRAME_MAGIC_1
    frame[2] = GX_FRAME_VERSION
    frame[3] = GX_FRAME_TYPE_IMU_TF

    payload = struct.pack(
        '<IQ4f3f3f',
        seq,
        timestamp_us,
        qx,
        qy,
        qz,
        qw,
        gyro_x,
        gyro_y,
        gyro_z,
        acc_x,
        acc_y,
        acc_z,
    )
    frame[4:56] = payload
    frame[56] = gx_frame_checksum(frame)
    return bytes(frame)


def parse_gx_frame(frame: bytes) -> Optional[GxImuFrame]:
    if len(frame) != GX_FRAME_SIZE:
        return None
    if frame[0] != GX_FRAME_MAGIC_0 or frame[1] != GX_FRAME_MAGIC_1:
        return None
    if frame[2] != GX_FRAME_VERSION or frame[3] != GX_FRAME_TYPE_IMU_TF:
        return None
    if gx_frame_checksum(frame) != frame[56]:
        return None

    (
        _magic,
        version,
        frame_type,
        seq,
        timestamp_us,
        qx,
        qy,
        qz,
        qw,
        gyro_x,
        gyro_y,
        gyro_z,
        acc_x,
        acc_y,
        acc_z,
    ) = _FRAME_HEADER.unpack(frame[:56])

    if version != GX_FRAME_VERSION or frame_type != GX_FRAME_TYPE_IMU_TF:
        return None

    return GxImuFrame(
        seq=seq,
        timestamp_us=timestamp_us,
        qx=qx,
        qy=qy,
        qz=qz,
        qw=qw,
        gyro_x=gyro_x,
        gyro_y=gyro_y,
        gyro_z=gyro_z,
        acc_x=acc_x,
        acc_y=acc_y,
        acc_z=acc_z,
    )


class GxStreamParser:
    """Incremental parser that resyncs on GX magic bytes."""

    def __init__(self, max_buffer: int = 4096) -> None:
        self._buf = bytearray()
        self._max_buffer = max_buffer

    def feed(self, data: bytes) -> list[GxImuFrame]:
        if not data:
            return []

        self._buf.extend(data)
        if len(self._buf) > self._max_buffer:
            self._buf = self._buf[-self._max_buffer:]

        frames: list[GxImuFrame] = []
        while True:
            parsed = self._try_extract_one()
            if parsed is None:
                break
            frames.append(parsed)
        return frames

    def _try_extract_one(self) -> Optional[GxImuFrame]:
        while len(self._buf) >= 2:
            start = 0
            while start < len(self._buf) - 1:
                if self._buf[start] == GX_FRAME_MAGIC_0 and self._buf[start + 1] == GX_FRAME_MAGIC_1:
                    break
                start += 1

            if start > 0:
                del self._buf[:start]

            if len(self._buf) < GX_FRAME_SIZE:
                return None

            candidate = bytes(self._buf[:GX_FRAME_SIZE])
            frame = parse_gx_frame(candidate)
            if frame is not None:
                del self._buf[:GX_FRAME_SIZE]
                return frame

            del self._buf[0]

        return None
