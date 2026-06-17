import struct
from pathlib import Path
from typing import Optional, Tuple

# 魔数： (偏移, 字节序列) 或 特殊处理在函数里
MAGIC = {
    "jpeg": [(0, b"\xff\xd8\xff")],
    "png": [(0, b"\x89PNG\r\n\x1a\n")],
    "gif": [(0, b"GIF87a"), (0, b"GIF89a")],
    "bmp": [(0, b"BM")],
    "webp": [(0, b"RIFF")],  # 需额外检查 WEBP 子标识，见下方
    "tiff_le": [(0, b"II*\x00")],
    "tiff_be": [(0, b"MM\x00*")],
}

EXT_TO_CANON = {
    ".jpg": "jpeg", ".jpeg": "jpeg",
    ".png": "png",
    ".gif": "gif",
    ".bmp": "bmp",
    ".webp": "webp",
    ".tif": "tiff", ".tiff": "tiff",
}


def detect_image_format(data: bytes) -> Optional[str]:
    if len(data) < 12:
        return None
    for name, rules in MAGIC.items():
        if name == "webp":
            # RIFF....WEBP
            if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
                return "webp"
            continue
        for offset, sig in rules:
            if data[offset : offset + len(sig)] == sig:
                if name in ("tiff_le", "tiff_be"):
                    return "tiff"
                return name
    return None


def extension_matches_content(path: str | Path) -> Tuple[bool, str, Optional[str]]:
    """
    返回: (是否匹配, 扩展名推断的格式, 魔数检测出的格式)
    无扩展名或未知扩展名时，claimed 为 None，只报告 detected。
    """
    p = Path(path)
    ext = p.suffix.lower()
    claimed = EXT_TO_CANON.get(ext)

    head = p.read_bytes()[:64]
    detected = detect_image_format(head)

    if claimed is None:
        return (True, "", detected)  # 无法对比时你可自行定义语义
    match = detected == claimed
    return (match, claimed, detected)


if __name__ == "__main__":
    ok, claimed, real = extension_matches_content("1.png")
    print("匹配:", ok, "声称:", claimed, "实际:", real)