---
name: game-skill-vfx-production
description: |
  游戏技能动效全流程制作 Skill。把一次"技能特效需求"按六段管线落地为可直接进引擎的资产：
  Brief 需求锁定 → 概念图 → F1–F6 关键帧 → 动态预览 → Alpha 透明帧序列+元数据 → 引擎接入验收。
  内置 E1–E8 表现单元库（聚气/爆发/发射/旋转/散开/击中/持续/消散，可组合非互斥）与组合模板
  （火球术 E1→E3→E6+E2→E8 等）；F1–F6 生命周期模板（F4=命中/峰值，含非命中变体）；
  交付目录规范 01_brief…07_qa、命名 fx_{skill}_{phase}_{variant}_v{ver}_{frame}.png、
  meta.yaml 元数据 schema、7 维验收清单，附序列校验与拼 Sprite Sheet 脚本。
  触发词：技能特效、技能动效、帧序列、Sprite Sheet、粒子特效、爆炸、发射、聚气、击中、光环、
  持续伤害、消散、透明背景、抠图、Godot 特效、Unity 特效、Cocos 特效、Unreal 特效、技能图、
  六帧分镜、F1-F6、E1-E8、fx_ 命名。
  不用于：3D 骨骼/蒙皮绑定、Shader 编码、音效制作、与游戏引擎落地无关的插画/宣传海报。
---

# 游戏技能动效制作 SOP v2

## 0. 模块边界（先读）

- 本 Skill 只做「战斗技能特效」的资产生产闭环：概念图 → 关键帧 → 动态预览 → 透明帧序列 → 引擎接入。
- 以下需求**不属于**本 Skill，不假装实现；明确告知边界，只承接其中与技能特效直接相关的部分：
  - UI 交互动效（按钮/面板/页签/数值）→ 独立模块 `ui-motion-design`
  - 角色动作/事件同步、镜头反馈、音效 → 独立模块 `combat-motion-sync`
  - 场景环境动效、运营/抽卡展示 → 独立模块
- 需求横跨多模块时，只在本 Skill 范围内交付，其余标注「待其他模块」。

## 1. 环境工具链

| 环节 | 工具 |
|---|---|
| 概念图 / 关键帧 | `image_gen`（seedream；固定 seed、统一宽高比保连续性） |
| 动态预览 | `text_to_video` / `image_to_video`（seedance；以 F1–F6 为关键帧插值） |
| 抽帧 / 去背 / Alpha 检查 | `byted-mediakit-video`；ffmpeg 兜底 |
| 序列校验 / 拼 sheet | 本 Skill 自带 `scripts/validate_sequence.py`、`scripts/build_sheet.py` |

## 2. 开工输入（Stage 0 · Brief）

先收集字段，缺失一律标「待定」，**禁止编造**。自然语言描述或直接填 YAML：

```yaml
skill_meta:
  name: "烈焰爆裂"            # 技能名
  name_en: "Blaze Burst"
  owner: "火焰法师·艾拉"
  element: fire               # 元素主题：fire/ice/lightning/holy/dark/nature/arcane/physical
  gameplay_use: attack        # attack / support / control / heal
  tier: ultimate              # normal / skill / ultimate / passive

effects:
  chain: [E1, E2, E6, E5, E8] # 表现单元组合链（§4），与元素/玩法分开建模
  notes: "聚气→爆发→命中→溅射→消散"

timing:
  cast_time_ms: 400           # 前摇
  active_time_ms: 800         # 主体持续
  recover_time_ms: 300        # 后摇
  hit_frame: 9                # 命中判定帧（0-indexed）
  loopable: false             # 是否需要首尾循环

art_direction:
  style: "2D anime"           # 2D pixel / 2D anime / 2.5D semi-real / stylized painterly
  palette: ["#FF6B00", "#FFD447", "#7A1A00"]
  camera: "top-down 45°"      # top-down 45° / side-view / isometric
  resolution: "512x512"
  fps: 24
  reference_images: []

engine_target:
  engine: godot4              # godot4 / unity / cocos / unreal / web
  export_format: ["png_sequence", "sprite_sheet_grid"]
  pivot: center_bottom        # center / center_bottom / custom
  premultiplied_alpha: false

constraints:
  forbid: ["真人形象", "血腥", "宗教符号"]
  platform_rating: "全年龄"
  device_budget: "中端手机，同屏 ≤ 32 特效"
```

**产出**：`01_brief/brief.yaml` + `01_brief/style_lock.md`（风格锁定：配色、元素、形态、视角、光向、参考图）。
**门禁**：用户确认 brief 与风格锁定后，才进入 Stage 1。

## 3. 六段管线与门禁

> **强制门禁**：每段结束后必须让用户确认（approve）才能进入下一段；未确认不生成后续内容。

| 阶段 | 产出目录 | 关键产出 | 门禁 |
|---|---|---|---|
| 0 Brief 与风格锁定 | `01_brief/` | brief.yaml、style_lock.md | 确认 |
| 1 概念图 | `02_concept/` | keyframe.png、keyframe_prompt.md | 确认 |
| 2 F1–F6 关键帧 | `02_concept/storyboard/` | sb_*_f01..f06.png、storyboard.md | 确认（成本最低返工点） |
| 3 动态预览 | `03_preview/` | *\_motion.mp4、*\_timing.json | 确认 |
| 4 Alpha 序列+元数据 | `04_frames/` `05_metadata/` | 透明 PNG 序列、meta.yaml、sheet | 自动校验通过 |
| 5 引擎接入+QA | `06_engine/` `07_qa/` | 接入脚本、实机截图、report.md | 交付 |

- Stage 1 概念图：主体居中占 60%–80%，背景纯色/透明，光影与 camera 一致，无 UI/文字/水印。
- Stage 2 关键帧：相机不切、站位不跳、主色按 palette 渐变（相邻帧色相差 ≤ 60°）；每帧可独立做宣传截图。
- Stage 3 动态预览：以 F1–F6 为关键帧插值；输出 timing.json（每帧 duration_ms、hit_frame）。
- Stage 4：跑 `scripts/validate_sequence.py`，全部通过才可进入 Stage 5。
- Stage 5：目标引擎实测后把状态改为 `engine_ok`；未实测只能标 `draft`。

## 4. E1–E8 表现单元（先定组合，再定帧）

E1 聚气 Charge · E2 爆发 Burst · E3 发射 Projectile · E4 旋转 Spin · E5 散开 Scatter · E6 击中 Impact · E7 持续 Aura/DoT · E8 消散 Dissipate

- **原则**：E1–E8 是可组合的表现单元，不是互斥分类。一个技能可组合多个单元；同一单元可复用不同材质与配色。「表现类型 / 元素主题 / 玩法用途」分开建字段（见 §7 meta.yaml）。
- **常用组合模板**：

| 技能概念 | 组合链 | 表现链路 |
|---|---|---|
| 火球术 | E1→E3→E6+E2→E8 | 掌心聚气→飞行拖尾→命中爆发→火星消散 |
| 旋风斩 | E1→E4+E7→E5→E8 | 起手蓄势→环形斩击→碎屑外散→尾迹退场 |
| 治疗光环 | E1→E7→E8 | 脚下成环→稳定循环→柔和消散（无命中语义） |
| 冰爆陷阱 | E7→E6+E2→E5→E8 | 待触发提示→接触爆发→冰片扩散→雾气消散 |

- 每个单元的节奏曲线、主体元素、易错点与检查项：**读 `references/effect-library.md`**。
- 把组合链映射到 F1–F6 各帧职责（§5），并写入 storyboard.md。

## 5. F1–F6 生命周期

**攻击类模板**（F4=命中/峰值）：

| 帧 | 职责 | 视觉重点 |
|---|---|---|
| F1 | 起势 / 聚气开始 | 低强度建立形态，明确能量来源 |
| F2 | 蓄能增强 | 体积 / 粒子密度 / 亮度逐步上升 |
| F3 | 释放 / 爆发 / 接近目标 | 方向与速度清晰，为命中蓄势 |
| F4 | 命中（峰值） | 反馈峰值；轮廓、冲击方向与目标关系明确 |
| F5 | 余波 / 碎片扩散 | 强度回落，保留运动惯性 |
| F6 | 消散 / 结束 | 平滑归零（alpha≈5%）；持续技能另行设计循环衔接 |

**非命中变体**：纯光环 / 治疗 / 持续类特效，F4 = 强度峰值 / 状态建立；必须在 storyboard.md 显式标注「扩展规则」，不得静默改变 F4 定义。

**连续性三原则**：① 相机锁定（同机位/同 FOV/同光源）；② 锚点稳定（pivot 位移 ≤ 帧宽 10%）；③ 色相守恒（相邻帧主色相差 ≤ 60°，跨阶段允许一次大跳）。

帧数策略（8 循环 / 16 标准 / 24–32 大招）、6→N 插值分配表、亮度曲线、非命中循环模板：**读 `references/frame-timing.md`**。

## 6. 交付目录与命名（硬性）

```
<skill_key>/
├── 01_brief/brief.yaml, style_lock.md
├── 02_concept/keyframe.png, keyframe_prompt.md,
│   └── storyboard/sb_<key>_f01.png … f06.png, storyboard.md
├── 03_preview/<key>_motion.mp4, <key>_timing.json
├── 04_frames/fx_<key>_<phase>_<variant>_v<ver>_<frame:04d>.png
├── 05_metadata/meta.yaml, <key>_sheet_h.png / _sheet_grid.png, <key>_sheet.json
├── 06_engine/（接入脚本、导入说明、实机截图/录屏）
└── 07_qa/report.md, alpha_check.png（深浅双底/棋盘格预览）
```

- 帧文件：`fx_{skill_key}_{phase}_{variant}_v{version}_{frame:04d}.png`
  - `phase` 子阶段：charge / release / impact / scatter / dissipate / loop
  - `variant`：a / b / c；`version`：v001 起递增
  - 例：`fx_fireball_impact_a_v001_0001.png`
- Storyboard：`sb_<skill_key>_f01.png … f06.png`；概念图：`keyframe.png`
- **禁止**：中文文件名、空格、大写、把版本号写进文件名（版本进目录 `v1/`、`v2/`）

## 7. 元数据（05_metadata/meta.yaml）

```yaml
asset_id: fx_fireball_impact_a
status: draft                 # draft / reviewed / engine_ok
skill_key: fireball
skill_types: [E1, E3, E6, E2, E8]   # 表现单元组合链
element: fire
gameplay_use: attack
canvas_px: [512, 512]
coordinate_origin: top_left
pivot_normalized: [0.5, 1.0]        # center_bottom
fps: 24
frame_count: 16
loop: false
alpha_mode: straight                # straight / premultiplied
blend_mode: alpha                   # alpha / additive
impact_time_ms: 420
cast_time_ms: 400
active_time_ms: 800
recover_time_ms: 300
hit_frame: 9                        # 0-indexed
engine_target: godot4
frame_pattern: "04_frames/fx_fireball_impact_a_v001_%04d.png"
```

## 8. Alpha 透明输出规范

1. **通道**：RGBA 8-bit，非预乘默认；引擎要求预乘时另存 `_pma` 版本并在 meta 声明。
2. **边缘**：四角 alpha=0；抠图边缘 defringe，无绿/黑/紫边残留。
3. **半透明**：光晕、火星、烟雾必须保留 alpha 渐变，禁止硬阈值二值化。
4. **统一 bbox**：全帧 alpha 并集的最小外接矩形 + 4px padding，防帧间抖动。
5. **色彩空间**：sRGB，不带 ICC profile。
6. **风险**：普通 MP4 无 alpha 通道，不视为透明母版；WebM/ProRes 的 alpha 需核验编码。优先直接生成透明背景帧，视频来源必须验证。
7. **性能公式**：显存占用 ≈ 宽×高×4 字节 × 帧数；PNG 体积 ≠ 显存占用。按设备预算定尺寸/帧率/图集方案。

## 9. 引擎落地

| 引擎 | 快速接入 | 导入要点 |
|---|---|---|
| Godot 4 | AnimatedSprite2D + SpriteFrames（见参考文档脚本） | Filter=Nearest/Linear；Fix Alpha Border=ON；Mipmaps=OFF |
| Unity | Sprite(Multiple) + Sprite Editor Grid Slice + Animation Clip | Sample=24；URP 用 Sprite-Lit-Default；默认不用预乘材质 |
| Cocos 3.x | 拖入 sheet 自动切图 + Animation / sp.Skeleton | 循环特效 wrapMode=Loop |
| Unreal | Paper2D Flipbook / Niagara Sprite + Sub UV | Sub Image Size 匹配网格 |
| Web/H5 | webp 动图或 PixiJS AnimatedSprite.fromFrames() | 小体积优先 |

每种引擎的代码与详细步骤：**读 `references/engine-integration.md`**。

## 10. 验收与自检（Stage 5 强制）

7 维验收清单：**视觉 / 时序 / 透明 / 资源 / 工程 / 性能 / 体验**。逐项打钩，写入 `07_qa/report.md`，未通过写明原因与修复动作。

- 自动校验：`python3 scripts/validate_sequence.py <skill_dir>`（命名、帧数、RGBA、四角透明、bbox、loop 首尾差、meta 一致性）
- 透明预览：生成深浅双底 + 棋盘格 `alpha_check.png` 人工确认
- 引擎实测：`06_engine/` 放实机截图/录屏，通过才可标 `engine_ok`
- 质量分级 S/A/B/不合格与反面案例：**读 `references/qa-checklist.md`**
- 交付前五维自审：叙事性 / 连续性 / 技术性 / 落地性 / 契合性，任意一项未过回到对应阶段修复，禁止带病交付

## 11. 常用命令

```bash
# 序列自动校验（命名/帧数/Alpha/bbox/loop）
python3 scripts/validate_sequence.py <skill_dir>

# PNG 序列 → 网格/横向 Sprite Sheet + JSON（TexturePacker 兼容）
python3 scripts/build_sheet.py 04_frames --out 05_metadata/sheet_grid.png --grid 4

# 动态预览 webp（美术/PM 确认用）
ffmpeg -framerate 24 -i 04_frames/fx_%04d.png -loop 0 preview.webp

# 视频抽帧为 RGBA PNG（源须含 alpha，如 ProRes 4444 / WebM VP9-alpha）
ffmpeg -i motion.mov -vf "fps=24" -pix_fmt rgba frames/fx_%04d.png
```

## 12. 风险与限制

- 插值可能导致轮廓漂移、碎片凭空出现 → 用 Stage 2 门禁先对齐再生成。
- 去背可能损失半透明烟雾/光晕/运动模糊 → 深浅双底检查。
- 生成视频的画幅/帧率/时长可能偏离设定 → 以 brief.yaml 为准回读校验。
- 引擎实测通过前，交付状态只能标 `draft`；`engine_ok` 必须有实机证据。
- 拉伸型静态面板可用九宫格，但帧序列特效不应九宫格拉伸，会扭曲形态。
