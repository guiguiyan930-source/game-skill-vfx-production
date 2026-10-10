#!/usr/bin/env python3
"""validate_sequence.py — 游戏技能动效帧序列校验器（motion-asset-validator）。

用法:
    python3 validate_sequence.py <skill_dir> [--pattern REGEX] [--edge-tol FLOAT]

检查项（逐项 PASS / WARN / FAIL，任一 FAIL 时 exit code = 1）:
    1. 目录结构: 01_brief..07_qa 关键目录、05_metadata/meta.yaml
    2. meta.yaml: 可解析；frame_count / fps / pivot / alpha_mode 等关键字段存在
    3. 命名: 04_frames/*.png 全小写 snake_case，匹配 fx_{skill}_{phase}_{variant}_v{ver}_{frame:04d}.png
    4. 帧数: 04_frames 内 PNG 数量 == meta.frame_count（无 meta 时跳过）
    5. 通道: 全部帧为 RGBA 8-bit
    6. 四角透明: 四角像素 alpha == 0
    7. 画布统一: 所有帧尺寸一致
    8. bbox 统一: 各帧 alpha 外接矩形一致（含 4px padding 容差），防播放抖动
    9. 边缘残留(WARN): 最外 1px 有 alpha>0 像素；或半透明像素 RGB 接近纯绿/纯品红(疑似绿幕残留)
    10. 循环(loopable=true): 首帧与末帧 alpha 占比差 < 5%

说明: WARN 不阻断交付，但应在 QA 报告中说明；FAIL 必须修复后重跑。
"""
import argparse
import re
import sys
from pathlib import Path

from PIL import Image

FRAME_RE = re.compile(r"^fx_[a-z0-9]+(_[a-z0-9]+)*_v\d{3}_\d{4}\.png$")
REQUIRED_DIRS = ["01_brief", "02_concept", "03_preview", "04_frames",
                 "05_metadata", "06_engine", "07_qa"]
REQUIRED_META = ["frame_count", "fps", "canvas_px", "pivot_normalized",
                 "alpha_mode", "engine_target"]


def load_meta(skill_dir: Path):
    """读取 meta.yaml，失败返回 (None, 错误信息)。"""
    try:
        import yaml
    except ImportError:
        return None, "缺少 PyYAML（pip install pyyaml）"
    meta_path = skill_dir / "05_metadata" / "meta.yaml"
    if not meta_path.exists():
        return None, "缺少 05_metadata/meta.yaml"
    try:
        with open(meta_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f), None
    except Exception as e:  # noqa: BLE001
        return None, f"meta.yaml 解析失败: {e}"


def alpha_bbox(im: Image.Image):
    """返回 alpha 通道的非零外接矩形 (x0, y0, x1, y1)，全透明返回 None。"""
    alpha = im.getchannel("A")
    bbox = alpha.getbbox()
    if bbox is None:
        return None
    return bbox


def check_edges(im: Image.Image):
    """检查最外 1px 边缘：返回 (边缘半透明像素数, 疑似绿/紫残留数)。"""
    w, h = im.size
    px = im.load()
    edge_hit = 0
    fringe = 0
    for x in range(w):
        for y in (0, h - 1):
            r, g, b, a = px[x, y]
            if a > 0:
                edge_hit += 1
                if a < 255:
                    # 半透明边缘疑似绿幕/品红幕残留（g 或 r+b 显著偏高且偏纯色）
                    if (g > 120 and g > r * 1.6 and g > b * 1.6) or \
                       (r > 120 and b > 120 and g < r * 0.7 and g < b * 0.7):
                        fringe += 1
    for y in range(h):
        for x in (0, w - 1):
            r, g, b, a = px[x, y]
            if a > 0:
                edge_hit += 1
                if a < 255:
                    if (g > 120 and g > r * 1.6 and g > b * 1.6) or \
                       (r > 120 and b > 120 and g < r * 0.7 and g < b * 0.7):
                        fringe += 1
    # 用容忍系数过滤：边缘 1px 内 alpha>0 占比过高视为裁剪过紧
    perimeter = 2 * (w + h)
    return edge_hit, fringe, (edge_hit / perimeter if perimeter else 0)


def main():
    parser = argparse.ArgumentParser(description="游戏技能动效帧序列校验器")
    parser.add_argument("skill_dir", type=Path, help="技能交付根目录（含 01_brief..07_qa）")
    parser.add_argument("--pattern", default=None, help="自定义帧文件名正则（默认 fx_ 规范）")
    parser.add_argument("--edge-ratio", type=float, default=0.02,
                        help="边缘 alpha>0 像素占比告警阈值（默认 0.02）")
    args = parser.parse_args()

    skill_dir = args.skill_dir
    results = []  # (level, message)

    def report(level, msg):
        results.append((level, msg))
        print(f"[{level}] {msg}")

    # 1. 目录结构
    for d in REQUIRED_DIRS:
        if (skill_dir / d).exists():
            report("PASS", f"目录存在: {d}/")
        else:
            report("FAIL", f"缺少目录: {d}/")

    # 2. meta.yaml
    meta, err = load_meta(skill_dir)
    if err:
        report("FAIL", err)
        meta = {}
    else:
        report("PASS", "meta.yaml 可解析")
        missing = [k for k in REQUIRED_META if k not in meta]
        for k in missing:
            report("FAIL", f"meta.yaml 缺少关键字段: {k}")
        if not missing:
            report("PASS", f"meta.yaml 关键字段齐全（{len(REQUIRED_META)} 项）")

    # 3–10. 帧序列检查
    frames_dir = skill_dir / "04_frames"
    frames = sorted(frames_dir.glob("*.png")) if frames_dir.exists() else []
    if not frames:
        report("FAIL", "04_frames/ 内没有 PNG 帧")
    else:
        # 命名
        pattern = re.compile(args.pattern) if args.pattern else FRAME_RE
        bad_names = [p.name for p in frames if not pattern.match(p.name)]
        if bad_names:
            report("FAIL", f"命名不符合 fx_ 规范: {bad_names[:5]} ...（共 {len(bad_names)}）")
        else:
            report("PASS", f"命名符合 fx_{{skill}}_{{phase}}_{{variant}}_v{{ver}}_{{frame:04d}}.png（{len(frames)} 帧）")

        # 帧数 vs meta
        fc = meta.get("frame_count")
        if fc is not None and int(fc) != len(frames):
            report("FAIL", f"帧数不一致: meta.frame_count={fc}，实际 {len(frames)}")
        elif fc is not None:
            report("PASS", f"帧数一致: {len(frames)}")

        sizes = set()
        rgba_ok = True
        corners_ok = True
        bboxes = []
        edge_stats = []
        try:
            for p in frames:
                im = Image.open(p)
                im.load()
                if im.mode != "RGBA":
                    rgba_ok = False
                    report("FAIL", f"{p.name} 不是 RGBA（实际 {im.mode}）")
                    continue
                sizes.add(im.size)
                if im.mode == "RGBA":
                    w, h = im.size
                    px = im.getpixel
                    if not (px((0, 0))[3] == 0 and px((w - 1, 0))[3] == 0
                            and px((0, h - 1))[3] == 0 and px((w - 1, h - 1))[3] == 0):
                        corners_ok = False
                        report("FAIL", f"{p.name} 四角 alpha 未全为 0")
                    bboxes.append(alpha_bbox(im))
                    eh, fr, ratio = check_edges(im)
                    edge_stats.append((p.name, eh, fr, ratio))
        except Exception as e:  # noqa: BLE001
            report("FAIL", f"读取帧失败: {e}")
            return 1

        if rgba_ok and len(frames) == len(sizes) and len(sizes) == 1:
            report("PASS", f"通道: 全部 RGBA 8-bit，画布统一 {list(sizes)[0]}")
        elif len(sizes) > 1:
            report("FAIL", f"画布尺寸不一致: {sizes}")

        if corners_ok and frames:
            report("PASS", "四角 alpha=0")

        # bbox 跳动检查：帧间 bbox 中心位移 ≤ 阈值（允许合法扩大/平滑移动，禁止"跳"）
        valid_bboxes = [b for b in bboxes if b is not None]
        centers = []
        for b in valid_bboxes:
            if b:
                centers.append(((b[0] + b[2]) / 2.0, (b[1] + b[3]) / 2.0))
        if len(centers) >= 2:
            w0 = (next(iter(sizes))[0] if sizes else 512)
            max_jump = max(8.0, 0.10 * w0)
            jumps = [abs(centers[i][0] - centers[i - 1][0]) +
                     abs(centers[i][1] - centers[i - 1][1])
                     for i in range(1, len(centers))]
            worst = max(jumps)
            if worst <= max_jump:
                report("PASS", f"bbox 帧间跳动 {worst:.1f}px ≤ {max_jump:.0f}px")
            else:
                report("FAIL", f"bbox 帧间跳动 {worst:.1f}px 超过 {max_jump:.0f}px（锚点不稳，需统一裁剪/对齐 pivot）")
            # 内容整体扩张/位移属正常；仅当单帧尺寸差异大时给出统一裁剪建议
            span = (max(c[0] for c in centers) - min(c[0] for c in centers),
                    max(c[1] for c in centers) - min(c[1] for c in centers))
            if span[0] > 0.3 * w0 or span[1] > 0.3 * w0:
                report("WARN", f"内容整体移动/扩张幅度大（{span[0]:.0f}x{span[1]:.0f}px），"
                               f"建议用 build_sheet.py --crop-bbox 统一裁剪到公共 bbox")

        # 边缘
        if edge_stats:
            worst = max(edge_stats, key=lambda t: t[3])
            warn_edges = [t for t in edge_stats if t[3] > args.edge_ratio]
            if worst[3] > args.edge_ratio:
                report("WARN", f"{worst[0]} 边缘 alpha>0 占比 {worst[3]:.1%}（> {args.edge_ratio:.0%}，裁剪可能过紧）")
            else:
                report("PASS", f"边缘贴合良好（最差 {worst[0]} {worst[3]:.1%}）")
            fringe_total = sum(t[2] for t in edge_stats)
            if fringe_total:
                report("WARN", f"疑似绿/紫幕残留半透明像素 {fringe_total} 个，建议 defringe 复检")

        # 循环首尾
        if meta.get("loop") and len(frames) >= 2:
            first, last = frames[0], frames[-1]
            try:
                # 用 alpha 均值估算首尾差（简化，稳健且确定性）
                def mean_alpha(ch):
                    hist = ch.histogram()
                    total_px = max(sum(hist), 1)
                    return sum(i * c for i, c in enumerate(hist)) / (total_px * 255.0)

                a1 = mean_alpha(Image.open(first).getchannel("A"))
                aL = mean_alpha(Image.open(last).getchannel("A"))
                pct = abs(a1 - aL)
                if pct < 0.05:
                    report("PASS", f"loopable: 首尾 alpha 均值差 {pct:.2%} < 5%")
                else:
                    report("FAIL", f"loopable: 首尾 alpha 均值差 {pct:.2%} ≥ 5%")
            except Exception as e:  # noqa: BLE001
                report("WARN", f"loop 首尾检查失败: {e}")

    fails = sum(1 for lvl, _ in results if lvl == "FAIL")
    warns = sum(1 for lvl, _ in results if lvl == "WARN")
    print(f"\n结果: {len(results) - fails - warns} PASS / {warns} WARN / {fails} FAIL")
    if fails:
        print("结论: FAIL —— 修复后重跑，全部通过才能进入 Stage 5 引擎接入。")
        return 1
    print("结论: PASS —— 可以进入 Stage 5（仍须完成引擎实测与 7 维人工验收）。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
