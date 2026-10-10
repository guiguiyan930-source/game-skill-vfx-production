#!/usr/bin/env python3
"""build_sheet.py — PNG 帧序列 → Sprite Sheet（横向 / 网格）+ TexturePacker 兼容 JSON。

用法:
    python3 build_sheet.py <frames_dir> --out <sheet.png> [--grid N | --horizontal]
            [--crop-bbox] [--padding PX] [--fps F] [--json path]

说明:
    - 帧按文件名中的 4 位帧号排序（fx_fireball_impact_a_v001_0001.png → 1）。
    - 单格尺寸 = 所有帧的宽高最大值（--crop-bbox 时先按全帧 alpha 并集 + padding 裁剪，
      再取并集尺寸），保证帧间不抖动。
    - --grid N: N 列网格；--horizontal: 单行横向（帧数 ≤ 8 的小特效建议）。
    - 默认在 --out 同目录生成同名 .json（TexturePacker 兼容：meta.size / frames.frame.duration）。
"""
import argparse
import json
import re
import sys
from pathlib import Path

from PIL import Image

FRAME_NO = re.compile(r"_(\d{4})\.png$")


def frame_number(name: str):
    m = FRAME_NO.search(name)
    return int(m.group(1)) if m else 0


def load_frames(frames_dir: Path):
    frames = sorted(frames_dir.glob("*.png"), key=lambda p: frame_number(p.name))
    if not frames:
        raise SystemExit(f"错误: {frames_dir} 内没有 PNG 帧")
    imgs = []
    for p in frames:
        im = Image.open(p)
        if im.mode != "RGBA":
            im = im.convert("RGBA")
        imgs.append((p.name, im))
    return imgs


def unified_bbox(imgs, padding: int):
    """全帧 alpha 并集最小外接矩形 + padding，返回 (x0, y0, x1, y1)。"""
    x0 = y0 = 10 ** 9
    x1 = y1 = -1
    for _, im in imgs:
        b = im.getchannel("A").getbbox()
        if b is None:
            continue
        x0 = min(x0, b[0]); y0 = min(y0, b[1])
        x1 = max(x1, b[2]); y1 = max(y1, b[3])
    if x1 < 0:
        return None
    return max(0, x0 - padding), max(0, y0 - padding), x1 + padding, y1 + padding


def main():
    ap = argparse.ArgumentParser(description="PNG 序列 → Sprite Sheet + JSON")
    ap.add_argument("frames_dir", type=Path, help="帧序列目录（04_frames）")
    ap.add_argument("--out", type=Path, required=True, help="输出 sheet PNG 路径")
    mode = ap.add_mutually_exclusive_group()
    mode.add_argument("--grid", type=int, default=0, help="网格列数（如 4 = 4×N）")
    mode.add_argument("--horizontal", action="store_true", help="横向单行（帧数 ≤ 8）")
    ap.add_argument("--crop-bbox", action="store_true",
                    help="按全帧 alpha 并集统一裁剪 + padding，防帧间抖动")
    ap.add_argument("--padding", type=int, default=4, help="bbox 裁剪 padding（默认 4px）")
    ap.add_argument("--fps", type=int, default=24, help="帧率，用于 JSON duration（默认 24）")
    ap.add_argument("--json", type=Path, default=None, help="JSON 输出路径（默认 --out 同名 .json）")
    args = ap.parse_args()

    imgs = load_frames(args.frames_dir)
    n = len(imgs)

    if args.crop_bbox:
        bbox = unified_bbox(imgs, args.padding)
        if bbox is None:
            raise SystemExit("错误: 所有帧全透明，无法裁剪")
        imgs = [(name, im.crop(bbox)) for name, im in imgs]

    cell_w = max(im.width for _, im in imgs)
    cell_h = max(im.height for _, im in imgs)

    if args.horizontal:
        cols, rows = n, 1
    elif args.grid and args.grid > 0:
        cols = args.grid
        rows = (n + cols - 1) // cols
    else:
        cols = int(n ** 0.5)
        rows = (n + cols - 1) // cols
        # 更接近方形的排列：优先列数向上取整
        alt_cols = cols + 1
        alt_rows = (n + alt_cols - 1) // alt_cols
        if alt_rows * alt_cols < rows * cols:
            cols, rows = alt_cols, alt_rows

    sheet = Image.new("RGBA", (cols * cell_w, rows * cell_h), (0, 0, 0, 0))
    frames_meta = {}
    for idx, (name, im) in enumerate(imgs):
        r, c = divmod(idx, cols)
        x, y = c * cell_w, r * cell_h
        sheet.paste(im, (x, y), im)
        frames_meta[name] = {
            "frame": {"x": x, "y": y, "w": im.width, "h": im.height},
            "duration": 1000.0 / args.fps,
        }

    args.out.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(args.out)
    print(f"sheet: {args.out}  {sheet.width}x{sheet.height}  {cols}x{rows} 帧格 {cell_w}x{cell_h}")

    json_path = args.json or args.out.with_suffix(".json")
    payload = {
        "meta": {
            "image": args.out.name,
            "size": {"w": sheet.width, "h": sheet.height},
            "scale": "1",
            "fps": args.fps,
            "frame_size": {"w": cell_w, "h": cell_h},
            "grid": {"cols": cols, "rows": rows},
        },
        "frames": frames_meta,
    }
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"json:  {json_path}  ({len(frames_meta)} 帧)")


if __name__ == "__main__":
    sys.exit(main())
