# game-skill-vfx-production

游戏技能动效全流程制作 Skill —— 把一次"技能特效需求"从 Brief 一路落地为**可直接进游戏引擎**的 Alpha 透明帧序列、Sprite Sheet、参数化元数据与 QA 报告。

> 适用于 Godot / Unity / Cocos / Unreal / Web 的 2D 技能特效资产生产。触发词：技能特效、技能动效、帧序列、Sprite Sheet、粒子特效、透明背景、抠图等。

---

## ✨ 特性

- **六段管线 + 强制确认门禁**：Brief 需求锁定 → 概念图 → F1–F6 关键帧 → 动态预览 → Alpha 帧序列 → 引擎接入验收，每段须用户确认，杜绝返工。
- **E1–E8 表现单元库**：聚气 / 爆发 / 发射 / 旋转 / 散开 / 击中 / 持续 / 消散，可组合、非互斥；内置火球术、旋风斩、治疗光环、冰爆陷阱组合模板。
- **F1–F6 生命周期模板**：F4=命中/峰值，含非命中变体（光环/治疗类），附 6→N 插值分配与 8/16/24/32 帧策略。
- **标准化交付**：`01_brief … 07_qa` 目录规范、`fx_{skill}_{phase}_{variant}_v{ver}_{frame:04d}.png` 命名规范、meta.yaml 元数据 schema。
- **可执行工程脚本**：帧序列自动校验器 + Sprite Sheet 拼图器（TexturePacker 兼容 JSON），Alpha 质量可机器验证。
- **7 维验收清单**：视觉 / 时序 / 透明 / 资源 / 工程 / 性能 / 体验，S/A/B/不合格四级质量分级。

## 🚀 快速开始

把技能目录放入 Agent 的 skills 根目录（如 `.user_skills/`）即被加载。然后直接提需求：

```
"给火焰法师艾拉做一套 16 帧 AOE 爆炸技能特效，要能放进 Godot 4，带透明背景"
```

Agent 将自动执行：

```
Stage 0  Brief 与风格锁定（01_brief/）        ← 用户确认
Stage 1  技能概念图（02_concept/）             ← 用户确认
Stage 2  F1–F6 关键帧（02_concept/storyboard/） ← 用户确认
Stage 3  动态预览（03_preview/）               ← 用户确认
Stage 4  Alpha 帧序列 + 元数据（04_frames/ 05_metadata/） ← 自动校验
Stage 5  引擎接入 + QA（06_engine/ 07_qa/）    → 交付
```

## 📦 目录结构

```
game-skill-vfx-production/
├── SKILL.md                     # 技能主文件（六段管线 + 门禁 + E1–E8 + 交付规范）
├── README.md
├── references/
│   ├── effect-library.md        # E1–E8 表现单元库 + 组合模板 + 元素主题速查
│   ├── frame-timing.md          # F1–F6 职责 + 6→N 插值 + 帧数策略 + 亮度曲线
│   ├── engine-integration.md    # Godot/Unity/Cocos/Unreal/Web 接入代码与导入要点
│   └── qa-checklist.md          # 7 维验收清单 + 质量分级 + 反面案例
└── scripts/
    ├── validate_sequence.py     # 帧序列校验器（命名/帧数/RGBA/四角透明/跳动/循环）
    └── build_sheet.py           # PNG 序列 → 横向/网格 Sprite Sheet + JSON
```

## 🛠 脚本用法

```bash
# 1. 校验交付目录与帧序列（任一 FAIL 时 exit code = 1）
python3 scripts/validate_sequence.py <skill_dir>

# 2. PNG 序列 → 网格/横向 Sprite Sheet + JSON（TexturePacker 兼容）
python3 scripts/build_sheet.py 04_frames --out 05_metadata/sheet_grid.png --grid 4 --crop-bbox
```

依赖：Python 3.8+、Pillow；校验器解析 meta.yaml 需要 PyYAML（缺失时仅跳过 meta 检查）。

## 🧪 已验证

- `validate_sequence.py`：16 帧合法扩张场景 14 项全 PASS；坏命名 / 非 RGBA / 帧数不符 / 帧间跳动场景均被正确拦截（exit 1）。
- `build_sheet.py`：网格 / 横向 / 统一裁剪三种模式 + JSON 断言通过。
- Skill 结构校验（skill-creator quick_validate）：`Skill is valid!`

## 🗺 Roadmap

| 优先级 | 模块 | 状态 |
|---|---|---|
| P0 | skill-vfx-pipeline（本技能） | ✅ 已完成 |
| P0 | motion-asset-validator（序列校验器） | ✅ 已内置 |
| P1 | ui-motion-design（UI 交互动效） | 📌 规划中 |
| P1 | combat-motion-sync（角色动作/命中事件/镜头同步） | 📌 规划中 |
| P2 | environment-motion（场景环境动效） | 📌 规划中 |
| P2 | liveops-motion（运营/抽卡展示动效） | 📌 规划中 |

## 📄 License

MIT License
