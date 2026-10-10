# E1–E8 表现单元库

目录：
1. [组合规则](#组合规则)
2. [E1 聚气 Charge](#e1-聚气-charge)
3. [E2 爆发 Burst](#e2-爆发-burst)
4. [E3 发射 Projectile](#e3-发射-projectile)
5. [E4 旋转 Spin](#e4-旋转-spin)
6. [E5 散开 Scatter](#e5-散开-scatter)
7. [E6 击中 Impact](#e6-击中-impact)
8. [E7 持续 Aura / DoT](#e7-持续-aura--dot)
9. [E8 消散 Dissipate](#e8-消散-dissipate)
10. [元素主题速查](#元素主题速查)

## 组合规则

- E1–E8 是**表现单元**，不是职业/元素分类。一个技能 = 单元链（如 `[E1, E3, E6, E2, E8]`）。
- 「表现类型 / 元素主题 / 玩法用途」分开建字段（meta.yaml 中 `skill_types` / `element` / `gameplay_use`）。
- 单元可复用：同一单元换配色/材质即换主题（如 E2 爆发：火=爆炸、冰=冰爆、雷=电击）。
- 非攻击类（治疗/光环/状态）不要强行套命中语义；见 E7 与 SKILL.md §5 非命中变体。

## E1 聚气 Charge

- **表现重点**：能量朝中心/施法挂点汇聚，强度逐步升高。
- **节奏**：可循环；0–20% 起手亮，20–100% 内聚增强；亮度到顶后持续（不回落）。
- **主体元素**：符文环、内聚粒子、中心亮点渐强、能量来源方向。
- **易错点**：粒子方向做反（应从外向内汇聚）；亮度到顶后未持续导致"泄气"。
- **制作检查**：聚合中心与施法挂点一致；蓄力预警可读性（对手能看懂"要放了"）。
- **Prompt 片段**：`energy charging inward to palm, swirling runes, glowing particles converging, loopable`

## E2 爆发 Burst

- **表现重点**：短时快速扩张，形成明确的释放峰值。
- **节奏**：0–10% 蓄力，10–30% 冲击波扩张最快，30–60% 最大，60–100% 余烟。
- **主体元素**：中心闪光 + 冲击环 + 碎片 + 烟柱。
- **易错点**：峰值帧不够亮；缺冲击环；烟雾直接消失（应半透明淡出 ≥3 帧）。
- **制作检查**：控制过曝（F4 高光 ≤2 帧峰值）；持续时间与玩法数值匹配。
- **Prompt 片段**：`massive fire explosion, shockwave ring, embers, top-down 45°, centered, black background, 2D game vfx sheet, high contrast`

## E3 发射 Projectile

- **表现重点**：突出运动方向、弹体与拖尾的关系。
- **节奏**：0–20% 抬手/聚能，20–30% 出手闪光，30–100% 弹体飞行 + 拖尾。
- **主体元素**：弹头 + 拖尾（3–5 帧长度）+ 出手闪。
- **易错点**：拖尾长度恒定（应随速度衰减，末尾 ease-out）；弹头无旋转细节。
- **制作检查**：区分起点 / 轨迹 / 终点 / 碰撞事件；命中帧对齐玩法 hit_frame。
- **Prompt 片段**：`fireball projectile with long tapered trail, motion blur, side view, transparent background, game asset`

## E4 旋转 Spin

- **表现重点**：围绕中心形成轨道、环形或螺旋运动。
- **节奏**：匀速旋转 + 脉冲亮度；可叠加扩散。
- **主体元素**：中心轴 + 螺旋条 + 边缘粒子。
- **易错点**：旋转不闭环（loopable 必须 F1=Fn）；螺旋方向与玩法定义相反；层级遮挡乱。
- **制作检查**：统一旋转轴、方向、层级遮挡；循环时首尾无缝。
- **Prompt 片段**：`swirling vortex ring rotating around axis, orbital particles, loopable, top-down view`

## E5 散开 Scatter

- **表现重点**：碎片、粒子或能量从中心向外扩散。
- **节奏**：0–20% 中心聚，20–40% 爆散最快，40–100% 粒子外飘衰减（ease-out，先快后慢）。
- **主体元素**：中心点 + 放射线 ×8–16 条 + 粒子群。
- **易错点**：粒子等速运动（应先快后慢）；路径不自然（直线穿模）；粒子/透明叠加过量。
- **制作检查**：路径自然；限制粒子数量与透明叠加（性能）。
- **Prompt 片段**：`burst of scattered shards and particles radiating outward, varied velocity, fading, transparent bg`

## E6 击中 Impact

- **表现重点**：短促而明确的接触反馈，表达命中点与方向。
- **节奏**：非常短（6–10 帧）：0–20% 白闪，20–50% 冲击环，50–100% 火星消散。
- **主体元素**：白色闪 + 十字/放射线 + 3–5 颗火星。
- **易错点**：白闪太长（应 ≤2 帧）；缺方向感；与伤害事件不同步（视觉误判）。
- **制作检查**：与伤害事件同步；命中点对齐角色挂点；方向与攻击方向一致。
- **Prompt 片段**：`impact flash, cross-shaped burst, radial sparks, 8 frames, transparent bg, game vfx`

## E7 持续 Aura / DoT

- **表现重点**：稳定循环并适度变化，持续表达范围或状态。
- **节奏**：循环 8 帧；呼吸感（亮度 sin 曲线）；首尾无缝。
- **主体元素**：地面法阵 / 环绕光带 / 缓慢粒子。
- **易错点**：变化太剧烈失去"持续"感；首尾不接；战场遮挡严重（应控制不透明度）。
- **制作检查**：首尾循环；遮挡层级合理；无命中语义时用「强度峰值」替代 F4 命中（显式标注）。
- **Prompt 片段**：`calm looping aura ring, breathing glow, subtle particles, seamless loop, transparent bg`

## E8 消散 Dissipate

- **表现重点**：亮度、密度或尺度逐步衰减到归零。
- **节奏**：3–6 帧；透明度线性 → 加速衰减；最后一帧 alpha≈5%。
- **主体元素**：残留粒子 + 烟 + 亮度下降 + 饱和度下降。
- **易错点**：瞬间截断（"啪"消失）；边缘残留；消散帧色相不变（应降饱和+降亮度，观感"结束了"）。
- **制作检查**：防止残留边缘；最后一帧接近透明；持续技能需设计循环衔接。
- **Prompt 片段**：`fading smoke, dissipating embers, low opacity, gentle fadeout, desaturated`

## 元素主题速查

| 元素 | 配色提示 | 形态提示 |
|---|---|---|
| fire | 橙红 #FF6B00 + 亮黄 + 深褐 | 火舌、火星、烟柱、冲击环 |
| ice | 冰蓝 #7FD8FF + 白 + 深蓝 | 冰晶、霜雾、碎裂多边形 |
| lightning | 电紫蓝 #6A5CFF + 白闪 | 闪电分支、电弧、点闪 |
| holy | 金白 #FFE9A8 + 天蓝 | 圣光、光环、羽状辉光 |
| dark | 紫黑 #3A1A5C + 绿磷 | 暗雾、紫焰、眼状符文 |
| nature | 绿 #7FD17F + 土棕 | 藤蔓、叶片、花粉粒子 |
| arcane | 品蓝 #8A6CFF + 青 | 符文、六芒阵、空间扭曲 |

统一 Prompt 后缀：`no text, no UI, no watermark, no character, pure vfx, transparent background`
