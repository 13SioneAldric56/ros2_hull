"""
递归扫描目录下所有 .png：若文件头为 JPEG，则写成同名 .jpg（保留原始 JPEG 字节流）
并删除原 .png。真实 PNG 不修改。

用法（在含图片的目录下执行，或传入根目录）：
  python demo_2.py              # 仅预览
  python demo_2.py --apply      # 真正转换
  python demo_2.py --apply --overwrite   # 覆盖已存在的同名 .jpg
"""

from __future__ import annotations

import argparse
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Iterable, Optional

from demo import detect_image_format


def iter_png_files(root: Path) -> Iterable[Path]:
    yield from root.rglob("*.png")
    yield from root.rglob("*.PNG")


def convert_mislabeled_png_jpeg_to_jpg(
    root: Path,
    *,
    apply: bool,
    overwrite: bool,
) -> None:
    root = root.resolve()
    planned: list[tuple[Path, Path]] = []
    skipped: list[tuple[Path, str]] = []

    seen: set[Path] = set()
    for png in sorted(iter_png_files(root), key=lambda p: str(p).lower()):
        png = png.resolve()
        if png in seen:
            continue
        seen.add(png)

        if not png.is_file():
            continue
        head = png.read_bytes()[:64]
        detected = detect_image_format(head)
        if detected != "jpeg":
            reason = detected or "unknown"
            skipped.append((png, f"实际不是 JPEG（{reason}），跳过"))
            continue
        jpg = png.with_suffix(".jpg")
        if jpg.exists() and not overwrite:
            skipped.append((png, f"目标已存在 {jpg.name}，跳过（使用 --overwrite 可覆盖）"))
            continue
        planned.append((png, jpg))

    for png, msg in skipped:
        try:
            rel = png.relative_to(root)
        except ValueError:
            rel = png
        print(f"[跳过] {rel} — {msg}")

    if not planned:
        print("没有需要转换的「假 PNG / 真 JPEG」文件。")
        return

    mode = "执行" if apply else "预览（未写入，请加 --apply）"
    print(f"\n{mode}，共 {len(planned)} 个文件：")
    for png, jpg in planned:
        try:
            rel = png.relative_to(root)
        except ValueError:
            rel = png
        print(f"  {rel} -> {jpg.name}")

    if not apply:
        return

    for png, jpg in planned:
        tmp: Optional[Path] = None
        try:
            fd, tmp_name = tempfile.mkstemp(
                suffix=".jpg", dir=jpg.parent, text=False
            )
            tmp = Path(tmp_name)
            with open(fd, "wb", closefd=True) as f:
                shutil.copyfileobj(png.open("rb"), f)
            if jpg.exists() and overwrite:
                jpg.unlink()
            tmp.replace(jpg)
            png.unlink()
            print(f"[完成] {png.name} -> {jpg.name}")
        except OSError as e:
            print(f"[失败] {png}: {e}", file=sys.stderr)
            if tmp is not None and tmp.exists():
                try:
                    tmp.unlink()
                except OSError:
                    pass


def main() -> None:
    p = argparse.ArgumentParser(
        description="将扩展名为 .png、实际为 JPEG 的文件改为标准 .jpg 文件名与内容。"
    )
    p.add_argument(
        "root",
        type=Path,
        nargs="?",
        default=None,
        help="扫描根目录（默认：本脚本所在目录）",
    )
    p.add_argument(
        "--apply",
        action="store_true",
        help="写入 .jpg 并删除原 .png（默认仅列出将要执行的操作）",
    )
    p.add_argument(
        "--overwrite",
        action="store_true",
        help="若同名 .jpg 已存在则覆盖",
    )
    args = p.parse_args()
    root = (args.root or Path(__file__).resolve().parent).resolve()
    convert_mislabeled_png_jpeg_to_jpg(
        root, apply=args.apply, overwrite=args.overwrite
    )


if __name__ == "__main__":
    main()
