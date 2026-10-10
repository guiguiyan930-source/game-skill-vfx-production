# 引擎落地参考

目录：
1. [通用导入要点](#通用导入要点)
2. [Godot 4](#godot-4)
3. [Unity（URP / 内置管线）](#unityurp--内置管线)
4. [Cocos Creator 3.x](#cocos-creator-3x)
5. [Unreal（Paper2D / Niagara）](#unrealpaper2d--niagara)
6. [Web / H5](#web--h5)
7. [Pivot 与预乘 Alpha 注意](#pivot-与预乘-alpha-注意)

## 通用导入要点

- 2D 帧序列特效：Mipmaps=OFF；Filter=Nearest（像素风）/ Linear（写实）。
- Fix Alpha Border / 修复透明边缘 = ON（消除 1px 边缘残留）。
- 默认按非预乘（straight alpha）处理；只有 meta.yaml 声明 `alpha_mode: premultiplied` 时才用预乘材质。
- `engine_ok` 状态必须有实机截图/录屏证据，否则只能标 `draft`。

## Godot 4

**推荐路径**：AnimatedSprite2D + SpriteFrames，或 AtlasTexture 手动切帧。

```gdscript
# 加载网格 sheet，自动切帧（4×4 为例，单帧 512）
var frames = SpriteFrames.new()
var tex = load("res://vfx/fireball/fireball_sheet_grid.png")
var cols = 4
var fw = tex.get_width() / cols
var fh = tex.get_height() / (tex.get_height() / fw)  # 按实际行数
for i in range(16):
    var atlas = AtlasTexture.new()
    atlas.atlas = tex
    atlas.region = Rect2((i % cols) * fw, (i / cols) * fh, fw, fh)
    frames.add_frame("default", atlas, 1.0 / 24.0)   # 24 fps
$AnimatedSprite2D.sprite_frames = frames
$AnimatedSprite2D.play("default")
```

- 导入设置：Filter=Nearest（像素）/ Linear（写实）；Fix Alpha Border=ON；Mipmaps=OFF。
- 单帧 PNG 序列：直接 `AnimatedSprite2D` + 帧数组加载。
- 循环特效：`$AnimatedSprite2D.sprite_frames.set_animation_loop("default", true)`。

## Unity（URP / 内置管线）

**推荐路径**：Sprite（Multiple）+ Animation Clip。

1. 导入 `fireball_sheet_grid.png`：Texture Type=Sprite，Sprite Mode=Multiple。
2. Sprite Editor → Slice → Grid By Cell Size（填入单帧尺寸 512×512）。
3. 拖入 Hierarchy 自动生成 Animation Clip，Sample Rate = 24。
4. Material：内置管线 `Sprites/Default`；URP 用 `Sprite-Lit-Default`。
5. 帧事件：在命中帧（hit_frame）加 Animation Event 触发伤害/音效。

## Cocos Creator 3.x

1. 拖入 sheet 资源，选中后按 JSON 或 grid 自动切图。
2. 挂 `Animation` 组件（序列帧）或 `sp.Skeleton`（Spine 资产）。
3. 循环特效：`wrapMode: Loop`；命中事件用 Animation Event 对齐。

## Unreal（Paper2D / Niagara）

- **Paper2D**：Sprite Sheet → Paper Flipbook，FPS=24；命中帧做 Notify。
- **Niagara**：Sprite Renderer + Sub UV Module；Sub Image Size 设为 4×4（匹配网格），按帧索引驱动。

## Web / H5

- 首选 webp 动图（体积小、支持 alpha）。
- 或用 PixiJS：

```javascript
import { AnimatedSprite, Texture } from 'pixi.js';
const frames = [];
for (let i = 0; i < 16; i++) {
  frames.push(Texture.from(`fx_fireball_impact_a_v001_${String(i+1).padStart(4,'0')}.png`));
}
const anim = new AnimatedSprite(frames);
anim.animationSpeed = 24 / 60;
anim.loop = false;
app.stage.addChild(anim);
anim.play();
```

## Pivot 与预乘 Alpha 注意

- **Pivot 对齐**：`pivot_normalized` 决定特效锚点（如 `[0.5, 1.0]` = 中心底部），必须与角色手心/脚下挂点对齐，否则播放时"飘"。
- **预乘**：若引擎材质要求预乘 alpha，必须输出 `_pma` 版本（RGB 已乘 A），并在 meta.yaml 声明 `alpha_mode: premultiplied`；混用会导致半透明边缘变暗或发亮。
- **Additive 混合**：火焰/闪电等发光特效常用 `blend_mode: additive`，需在 meta.yaml 记录并选择对应材质，避免引擎默认 alpha 混合下变"灰"。
