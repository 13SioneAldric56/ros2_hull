#!/usr/bin/env python3
"""Serve offline Bing tiles stored as {z}/{y}/{x}.jpg for Mapviz WMTS requests."""

from __future__ import annotations

import argparse
import re
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


class BingTileHandler(BaseHTTPRequestHandler):
    tile_root: Path = Path(".")
    blank_tile: bytes = b""

    def do_GET(self) -> None:
        match = re.match(r"/(\d+)/(\d+)/(\d+)\.(jpg|jpeg|png)", self.path, re.IGNORECASE)
        if match is None:
            self.send_error(404, "Not Found")
            return

        level, req_x, req_y, ext = match.groups()
        tile_path = self.tile_root / level / req_y / f"{req_x}.{ext.lower()}"

        if tile_path.is_file():
            data = tile_path.read_bytes()
        elif self.blank_tile:
            data = self.blank_tile
        else:
            self.send_error(404, "Not Found")
            return

        content_type = "image/jpeg" if ext.lower() in {"jpg", "jpeg"} else "image/png"
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, format: str, *args) -> None:
        return


def main() -> None:
    parser = argparse.ArgumentParser(description="Offline Bing tile server for Mapviz")
    parser.add_argument(
        "--root",
        default="/home/sione/ros2_hull/maps/bing_tiles",
        help="Root directory of downloaded Bing tiles",
    )
    parser.add_argument(
        "--blank-tile",
        default="",
        help="Placeholder JPEG returned for missing tiles",
    )
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8080)
    args = parser.parse_args()

    tile_root = Path(args.root).resolve()
    if not tile_root.is_dir():
        raise SystemExit(f"Tile root does not exist: {tile_root}")

    blank_tile_path = Path(args.blank_tile).resolve() if args.blank_tile else None
    if blank_tile_path is None or not blank_tile_path.is_file():
        # Fallback next to this script's installed share config path is handled by launch.
        candidate = Path(__file__).resolve().parent.parent / "share" / "wheeltec_gps_path" / "config" / "blank_tile.jpg"
        blank_tile_path = candidate if candidate.is_file() else None

    BingTileHandler.tile_root = tile_root
    if blank_tile_path and blank_tile_path.is_file():
        BingTileHandler.blank_tile = blank_tile_path.read_bytes()
        print(f"Using blank tile: {blank_tile_path}")
    else:
        print("Warning: blank tile not found; missing tiles return 404")

    server = ThreadingHTTPServer((args.host, args.port), BingTileHandler)
    print(f"Serving Bing tiles from {tile_root} at http://{args.host}:{args.port}/")
    server.serve_forever()


if __name__ == "__main__":
    main()
