# WinKawaks P1/P2/P3 人物几何字段地图 — GEO 研究线

> 证据边界：本文仅记录 WinKawaks normalized CPS RAM 的 discovery evidence。不得直接作为 Browser/WASM production 证明，不修改 production-shadow 规则。

## 对象布局

- P1 `0xFFBE1C`
- P2 `P1 + 0xE0`
- P3 `P1 + 0x1C0`
- player stride `0xE0`
- self-id `+0x7C = 0/4/8`
- 当前 Collector fresh discovery：唯一 `xor3` 映射

## 已用动态证据

### GEO-0001

- 10 秒 / 60 Hz / 600 帧
- 472 distinct frames
- 0 read errors
- raw: `captures/GEO-0001-dynamic-baseline-20260831-1517Z.jsonl.gz`

### EFIELD-002 复用

另一只读研究线产生的 60 秒自然游戏 raw，因为帧中同样完整保留 P1/P2/P3，所以仅作为本地 discovery 复用：

- 60 秒 / 3600 帧
- 2848 distinct frames
- 0 read errors
- raw: `captures/EFIELD-002-natural-diversity-60s60.jsonl.gz`

### GEO-0003

- 10 秒 / 60 Hz / 600 帧
- 507 distinct frames
- 0 read errors
- P1/P2 均有明显横向和跳跃变化，P3 全程静止，可作为独立复验
- raw: `captures/GEO-0003-natural-geometry-10s60-20260831-1549Z.jsonl.gz`

## 当前字段地图

| WinKawaks relative offset | 当前解释 | 置信度 | 关键证据 |
|---|---|---|---|
| `+0x04..05` | 横向 low/local 分量，疑似 8.8 fixed | 高 | 平滑随横移变化；跨 256 边界时与 `+0x0A..0B` 联动 |
| `+0x0A..0B` | 横向 page/high 分量 | 高 | P1 `FC→00` 同时 page `0→1`；P2 `01→FE` 同时 page `2→1` |
| `+0x08..09` | floor Y / depth，疑似 8.8 fixed | 高候选 | P1/P2/P3 在横移/跳跃期间分别稳定在 `0x305C/0x4884/0x602E` |
| `+0x0C..0D` | Z / 跳跃垂直位移，疑似 8.8 fixed | 高 | 出现清晰上升—峰值—下降轨迹，而 floor Y 保持不变 |
| `+0x9C..9D` | lagged/render-cache low/local X | 高 | 强跟随 `+0x04..05`；跨页时精确保存上一位置 |
| `+0xA3` | lagged/cache X page | 高 | GEO-0003 中 P1/P2 `A3[t] == 0B[t-1]` 逐帧 100% 成立 |
| `+0xA2` | cached/render floor-Y integer component | 中高 | P1/P2/P3 = 48/72/96，恰等于 `+0x08..09` 整数高字节 |
| `+0x9E` | render/geometry anchor 或 extent 候选 | 低 | GEO-0003 P1/P2/P3 = 30/31/30，移动/跳跃时保持不变；需进一步动作/人物对照 |
| `+0x47` | current horizontal direction/orientation 候选 | 中高 | 右移前切为 0，左移前切为 255；变化先于实际 X 运动 |
| `+0x99` | queued/desired horizontal direction 候选 | 中高 | 通常比 `+0x47` 更早切换，再由 `+0x47` 跟进 |
| `+0x2D` | active-motion 状态候选 | 中高 | 两个独立数据集均表现为 moving≈2 / static≈0，跨 P1/P2/P3 一致 |
| `+0x35` | complementary moving/static 状态候选 | 中高 | moving 几乎总为 0；static 多为 255；静止 P3 600/600 = 255 |
| `+0x28` | motion lead/state 候选 | 中 | 2/0 模式与移动相关，但弱于 `+0x2D` |
| `+0x36` | complementary motion state | 中 | 类似 `+0x35`，P2 一致性较弱 |
| `+0x67` | timer/counter，非几何 | 中高 | countdown-like，排除几何 |

## 横坐标组合模型

早期把 `+0x0B/+0xA3` 当 facing 的假设已撤销。

GEO-0003 的跨 256 边界行为支持：

```text
worldX_px ~= U16BE(+0x0A..0B) * 256 + U16BE(+0x04..05) / 256
```

在当前样本 `+0x0A=0`、`+0x05=0`，可简化观察为：

```text
worldX_integer = (+0x0B << 8) | +0x04
```

P1 示例：252 → 256；P2 示例：513 → 510，跨页保持连续。

## 方向 / 朝向

目前最强方向字段是 `+0x47/+0x99`，不是 `+0x0B/+0xA3`。

GEO-0003 的时序：

```text
P1: +0x99 255→0
 -> +0x47 255→0
 -> X 开始向右移动

P2: +0x99 0→255
 -> +0x47 0→255
 -> X 开始向左移动
```

因此工作解释：

- `+0x47`: current horizontal direction/orientation
- `+0x99`: desired/queued horizontal direction
- 相对运动证据支持 `0≈right / 255≈left`

但 literal visual facing 仍需一次已知 LEFT/RIGHT 静止场景才能锁死。

## 移动 / 静止

当前优先级：

1. `+0x2D`
2. `+0x35`
3. `+0x28/+0x36`

GEO-0003 独立复验：

- P1 `+0x2D`: moving top=2 94.1%，static top=0 86.2%
- P2 `+0x2D`: moving top=2 96.8%，static top=0 86.2%
- 静止 P3 `+0x2D=0` 600/600
- P1/P2 moving 时 `+0x35=0` 100%
- 静止 P3 `+0x35=255` 600/600

## Camera / screen 坐标

现有 60 秒 + GEO-0003 均未出现“两个以上玩家同帧具有完全相同的非零 local-X delta”的 clean shared-scroll 片段，因此还没有真正锁定 global camera 字段。

当前只证明人物对象自身存在 low/local + page/high 的横坐标结构；不能据此直接宣称 `+0x04` 就是最终 screen-X。

## P1/P2/P3 差异

核心几何字段在三个 `0xE0` player object 内相对位置一致。已知差异主要是：

- self-id `+0x7C=0/4/8`
- floor/depth 当前值不同
- `+0x1B/+0x6C/+0x72/+0x73` 等存在明显角色/动作特异值
- `+0x9E` 30/31/30 是当前值得继续研究的静态 geometry-anchor/extent 候选

## 下一步

1. 继续筛 top/bottom/left/right 的 extent/anchor 字段，优先检查 `+0x9E` 及动作切换时低基数尺寸字段。
2. 采集包含更多自然动作变化的短 burst，验证 extent 候选是否随姿态变化。
3. 需要时再做 camera-scroll 专门场景。
4. literal facing 最终使用已知 LEFT/RIGHT 静止场景锁值。
5. 后续单独做 left-2P 与 P1/P2/P3 人物结构差异控制。

本报告只属于 GEO 独立研究线，不推进 WOF-045，不作为 Browser production-shadow promotion 证据。
