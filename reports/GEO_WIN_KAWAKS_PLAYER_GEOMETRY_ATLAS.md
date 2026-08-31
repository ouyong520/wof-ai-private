# WinKawaks P1/P2/P3 人物几何字段地图 — GEO 研究线

> 证据边界：本文仅记录 WinKawaks normalized CPS RAM 的 discovery evidence。不得直接作为 Browser/WASM production 证明；不修改 production-shadow；不推进 WOF-045；全程只读、无游戏内存写入。

## 对象布局

- P1 `0xFFBE1C`
- P2 `P1 + 0xE0`
- P3 `P1 + 0x1C0`
- player stride `0xE0`
- self-id `+0x7C = 0/4/8`
- Collector fresh discovery：唯一 `xor3` 映射

## 动态证据集

| 数据集 | 帧数 | 频率/时长 | distinct | 读错误 |
|---|---:|---|---:|---:|
| GEO-0001 | 600 | 10 s / 60.002 Hz | 472 | 0 |
| EFIELD-002（复用） | 3600 | 60 s / 59.993 Hz | 2848 | 0 |
| GEO-0003 | 600 | 10 s / 59.957 Hz | 507 | 0 |
| EFIELD-003（复用） | 3600 | 60 s / ~60 Hz | 多动作自然游戏 | 0 |
| GEO-0004 | 600 | 10 s / 59.926 Hz | 482 | 0 |

EFIELD 数据仅因为同一 raw frame 完整包含 P1/P2/P3 `0xE0` 对象而被本 GEO 线复用；仍然只是 WinKawaks discovery evidence。

## 当前字段地图

| WinKawaks relative offset | 当前解释 | 置信度 | 主要证据 |
|---|---|---|---|
| `+0x04..05` | 横向 local/low 坐标，8.8 fixed-point 候选 | 高 | 随横移平滑变化；与 page/high 字段共同跨 256 边界保持连续 |
| `+0x0A..0B` | 横向 page/high 补充分量 | 高 discovery | P1/P3 local-X 从 `FE/F8 -> 02/00` 跨边界时 `+0x0B 0->1`；早期 facing 假设已撤销 |
| `+0x08..09` | floor Y / depth，8.8 fixed-point 候选 | 高 | P1/P2/P3 典型值 `0x305C/0x4884/0x602E`；横移和跳跃期间稳定 |
| `+0x0C..0D` | Z / 跳跃垂直位移 family | 高 | 多个数据集出现上升—峰值—下降轨迹，floor-Y 同时保持稳定；低字节精确语义仍待细化 |
| `+0x47` | current horizontal direction/orientation 候选 | 中高 | 右移相位偏 `0`、左移偏 `255`；时序上可先于实际 X 运动 |
| `+0x99` | desired/queued horizontal direction 候选 | 中高 | GEO-0003 中常先于 `+0x47` 切换，再进入实际横移 |
| `+0x2D` | active-motion 状态候选 | 中高 | 多个独立样本 moving 多为 `2`、static 多为 `0`；并非严格二值，仍按状态 family 处理 |
| `+0x35` | moving/static complementary 状态候选 | 中高 | moving 几乎总为 `0`，static 多为 `255` |
| `+0x28/+0x36` | 相关 motion-state family | 中 | 与 `+0x2D/+0x35` 同向，但纯度较弱 |
| `+0x67` | timer/counter，非几何 | 中高 | countdown-like，排除坐标/尺寸解释 |

## 横坐标 page/local 模型

当前 WinKawaks working model：

```text
worldX_px ~= U16BE(+0x0A..0x0B) * 256
            + U16BE(+0x04..0x05) / 256
```

在常见样本 `+0x0A=0`、`+0x05=0` 时，可近似观察为：

```text
worldX_integer ~= (+0x0B << 8) | +0x04
```

这用于解释跨 local 0/255 边界的连续性；它尚未等同于最终 screen-X，因为 global camera 仍未锁定。

## Render / cache 块：`+0x90..+0xAF`

EFIELD-003（3600 帧）与 GEO-0004（600 帧）的联合分析把这一区域拆成了“render 位置 + 几何/形态元数据”混合块：

- `+0x9C`：render/local-X integer。运动时通常落后主 `+0x04` 约 1 帧；静止时精确相等。
- `+0x9D`：当前样本基本为 0，像 local-X 的小数/低位缓存槽。
- `+0xA2`：精确等于 floor-Y 整数字节 `+0x08`，P1/P2/P3 常见 `48/72/96`。
- `+0xA3`：与 X page `+0x0B` 高度一致；因此明确不是 facing 位。
- `+0xA4`：render-Z integer。跳跃时大多数帧跟 `+0x0C`，存在少量 render lag/动画偏差。
- `+0x9E`：目前最强 body/render extent-or-anchor 候选；不随坐标变化。
- `+0xAA`：另一条小尺寸/形态元数据候选；不随动作变化。

因此不能把 `0x9C..A4` 当成简单连续坐标拷贝。

## `+0x9E / +0xAA` 五组联合判别

对 GEO-0001、EFIELD-002、GEO-0003、EFIELD-003、GEO-0004 共 9000 帧进行联合检查：

- **所有 15 个 player×capture 组合中，`+0x9E` 帧内 transition 数均为 0。**
- **所有 15 个组合中，`+0xAA` 帧内 transition 数均为 0。**
- 同期 `+0x1B`、`+0x70..73` 等动作/body 字段大量变化，证明 `+0x9E/+0xAA` 不是逐动画帧动作状态。
- `+0x9E` 跨采集可变，见到约 `30..38`：
  - P1：36 / 31 / 30 / 31 / 31
  - P2：31 / 34 / 31 / 34 / 32
  - P3：32 / 38 / 30 / 38 / 38
- `+0xAA` 极稳定：五组采集中 P1=6、P2=6、P3=5。

当前解释：

- `+0x9E`：**角色/形态级 body extent 或 render anchor**，置信度升为中等；不像当前姿态帧 top/bottom offset。
- `+0xAA`：**更稳定的小尺寸/形态参数或角色元数据**，中低置信度；还不能确定是 horizontal/depth/vertical 哪一轴。

目前没有证据允许把 `+0x9E` 直接命名为 width/height，也不能把 `+0xAA` 直接命名为某个半径。

## 方向 / 朝向

早期 `+0x0B/+0xA3 = facing` 已被数据否定并撤销。

当前 strongest pair：

```text
+0x99  desired/queued direction candidate
   -> +0x47 current direction/orientation candidate
   -> horizontal X movement
```

自然运动支持 `0≈right / 255≈left`，但 literal visual facing 仍需一次已知 LEFT/RIGHT 静止控制才能最终锁值。

## 移动 / 静止

优先级：

1. `+0x2D`
2. `+0x35`
3. `+0x28/+0x36`

这些字段与基于 X/Y/Z 变化定义的 motion truth 在 P1/P2/P3 多数据集上重复分离，但仍只作为 WinKawaks 状态候选。

## Camera / screen 坐标

现有自然样本尚未提供干净的 shared-camera-scroll episode：此前 EFIELD-002/GEO-0003 中没有“两个以上玩家同一帧具有完全相同非零 local-X delta”的可靠公共滚动片段。

当前只锁定人物对象自身存在 local-X + page/high 的结构；还没有证明：

- 哪个全局字段是 camera-X / camera-Y；
- `worldX` 到物理 screen-X 的精确转换；
- camera 滚动时 `+0x9C` 的 render-X 是否已减 camera。

Browser 历史 camera probe 只能用于实验设计，不能作为 WinKawaks 数值语义证明。

## P1/P2/P3 结构差异

核心布局在三个 `0xE0` player object 中相同：

- `+0x7C = 0/4/8` self-id
- `+0x92 = 0/4/8` 也重复 slot/self selector 形态，非几何
- `+0x04..05` local-X
- `+0x0A..0B` X page/high family
- `+0x08..09` floor/depth
- `+0x0C..0D` Z family
- `+0x9C/+0xA2/+0xA3/+0xA4` render position cache family

玩家/角色/形态差异目前集中在 `+0x1B/+0x6C/+0x70..73/+0x9E/+0xAA` 等字段。

## top / bottom / left / right 当前状态

已知坐标 anchor 足以开始构造候选几何，但**边界公式尚未证明**：

- left/right：主 X 已基本锁定，但缺少已知 horizontal extent 的轴向语义；`+0x9E` 与 `+0xAA` 都不能直接认定为 X 半宽。
- bottom：floor-Y 与 Z 已分离，render-Y/Z 缓存也已找到，但 screen projection 仍缺 camera 关系。
- top：五组数据没有找到随逐帧动画变化的独立 top-offset 字段；这增加了“top 来自 ROM sprite/frame descriptor 或固定形态参数”的可能性。

现有 Browser descriptor/geometry 脚本主要描述敌人攻击时序和目标相对距离，没有直接提供 player sprite width/height，因此不能拿来直接命名 WinKawaks `+0x9E/+0xAA`。

## 下一步

1. 优先获取/定位 68000 ROM 字节后静态搜索 player `+0x9E/+0xAA` 的消费者，直接判定轴向和用途。
2. 若 ROM xref 暂不可用，再做专门 camera-scroll 控制，锁 camera/world/screen 转换。
3. literal facing 用已知静止 LEFT/RIGHT 场景锁 `+0x47/+0x99` 的视觉方向。
4. left-2P 与 P1/P2/P3 结构差异用独立控制场景验证。
5. 在 extent 轴向锁定后再正式给出 top/bottom/left/right 公式。

本报告只属于 GEO 独立研究线，不推进 WOF-045，不作为 Browser production-shadow promotion 证据。
