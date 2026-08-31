# WinKawaks P1/P2/P3 人物几何字段地图 — GEO 研究线

> 证据边界：本文仅记录 WinKawaks normalized CPS RAM 的 discovery evidence。不得直接作为 Browser/WASM production 证明；不修改 production-shadow；不推进 WOF-045；全程只读、无游戏内存写入。

## 对象布局与证据

- P1 `0xFFBE1C`
- P2 `0xFFBEFC`
- P3 `0xFFBFDC`
- stride `0xE0`
- self-id `+0x7C = 0/4/8`
- Collector 会按当前 WinKawaks host lane mapping 归一化回逻辑 CPS 地址顺序；多 session 均 fresh-discover 唯一 `xor3`

主要动态集：

- GEO-0001：600 帧 / 10 s
- EFIELD-002（复用完整 P1/P2/P3）：3600 帧 / 60 s
- GEO-0003：600 帧 / 10 s
- EFIELD-003（复用）：3600 帧 / 60 s
- GEO-0004：600 帧 / 10 s
- EFIELD-004（新 WinKawaks session，复用）：3600 帧 / 60 s
- GEO-0006：1200 帧 / 20 s / 59.987 Hz / 1157 distinct / 0 read errors

所有 EFIELD 复用仅因为同一 raw frame 含完整三个 player object；仍只属于 WinKawaks-local discovery。

## 当前字段地图

| offset | 当前解释 | 置信度 | 关键证据 |
|---|---|---|---|
| `+0x04` | local X integer byte | 高 | 随横移变化；与 `+0x0B` 在 0/255 wrap 同帧联动 |
| `+0x0B` | X page/high byte，单位约 256 | 高 | 多组独立 wrap 事件能重建连续 X；早期 facing 假设已撤销 |
| `+0x08` | floor/depth Y integer anchor | 高候选 | P1/P2/P3 常见 48/72/96；横移与普通跳跃期间稳定 |
| `+0x0C` | vertical/Z integer byte，modulo 256 | 高 | 正向跳跃弧与跨 255/0 的连续负向轨迹重复出现 |
| `+0x11` | Z subpixel/fraction phase | 中高 | 与 `+0x0C` 联动；值域常为 0/32/64/.../224 |
| `+0x47` | current horizontal facing/orientation state | 高候选 | 左移几乎总 255、右移几乎总 0；静止阶段长期保持；通常在 X 开始移动前约 1–2 帧切换 |
| `+0x99` | requested/queued horizontal direction state | 高候选 | 转向时通常比 `+0x47` 更早约 4–5 帧切换，随后 `+0x47`、再随后 X movement |
| `+0x2D` | active-motion state family | 中高 | moving 多为 2、static 多为 0 |
| `+0x35` | complementary moving/static state | 中高 | moving 几乎总为 0、static 多为 255 |
| `+0x67` | timer/counter，非几何 | 中高 | countdown-like |
| `+0x9C` | lagged/render local-X cache | 高 | 与 `+0x04` 高相关；运动时常约滞后一帧，静止时相等 |
| `+0xA2` | cached floor/depth integer | 高 | 多组样本精确等于 `+0x08` |
| `+0xA3` | X page/cache family | 高 | 与 `+0x0B` 高度一致；明确不是 facing |
| `+0x9E` | independent player-specific form/render/state field | 中低 | 长 capture 内稳定，但跨 player/capture 可为 0/18/30/31/32/34/36/38；无稳定字段能一一决定它 |
| `+0xAA` | player-specific metadata candidate | 低 | player 内常稳定，但 enemy 同 offset 明显动态，通用 extent 假设已降权 |

## X：local + page 已高置信度锁定

跨多个独立 capture 的 wrap 事件：

- GEO-0003 P1：local `252 -> 0`，page `0 -> 1`，重建 `252 -> 256`
- GEO-0003 P2：local `1 -> 254`，page `2 -> 1`，重建 `513 -> 510`
- EFIELD-003 P1：local `254 -> 2`，page `0 -> 1`，重建 `254 -> 258`
- EFIELD-003 P3：local `248 -> 0`，page `0 -> 1`，重建 `248 -> 256`

当前整数模型：

```text
worldX ~= 256 * U8(+0x0B) + U8(+0x04)
```

把相邻 `+0x06..07` 当 X 高位会在这些事件产生约 ±252 px 假跳变，因此“连续 4-byte X”模型被否定。`+0x05` 在当前样本长期为 0，尚不能证明是 X fraction。

## floor/depth：当前以 `+0x08` 为 anchor

旧的 `U16BE(+0x08..09)/256` 工作解释已降级。`+0x08` 单字节直接得到常见 P1/P2/P3 = 48/72/96，恰好等距 24；`+0x09` 在当前场景主要表现为 player/form-specific 常量，没有动态证据证明它是 Y fraction。

因此目前把 `+0x08` 作为 floor/depth anchor，`+0x09` 列 unknown。真正的 Y page/fraction 仍需 depth-only / depth-diversity 证据。

## Z：`+0x0C` + `+0x11`，不是 `+0x0C..0D` S16

`+0x0D` 在整段跳跃/下落中可保持固定（例如 P1=52、P2=64、P3=0），所以不能作为 live Z fraction。

观察到正向轨迹：

```text
0 -> 7 -> 10 -> 13 -> 16 -> ... -> 30 -> ... -> 7 -> 3 -> 0
```

也观察到跨 255/0 的负向连续轨迹：

```text
0 -> 255 -> 254 -> 253 -> 251 -> 248 -> ...
```

把 `+0x0C` 按 modulo-256 integer 沿路径 unwrap，可把后一类轨迹连续解释为 0、-1、-2、-3、-5、-8...，而不会在 signed-byte 127/128 边界制造假断裂。

`+0x11` 在相关轨迹中以 `0/32/64/96/128/160/192/224` 等量化值联动，符合亚像素 phase 候选。当前模型：

```text
Z ~= unwrap_mod256( U8(+0x0C) + U8(+0x11)/256 )
```

因此旧的 `S16/U16(+0x0C..0D)/256` 解释撤销。

## Render/cache 块

- `+0x9C`：X/render cache
- `+0xA2`：floor/depth cache
- `+0xA3`：X page cache
- `+0xA4`：旧 `render-Z` 假设撤销；系统扫描没有证明它稳定等于/滞后/共享 `+0x0C` delta
- 当前没有在 `0x90..0xAF` 锁到可靠 live render-Z cache

GEO-0006 是一个很干净的静止控制：三名玩家 1200 帧的 X/Y/Z 都不变，`+0x9C/+0xA2/+0xA3` 与主 anchor 全程一致。

## Direction / facing：`+0x99 -> +0x47 -> X`

七组 capture 联合，以重建后的 world-X delta 为运动 truth：

- 左移帧：`+0x47=255` 491 帧，`+0x47=0` 仅 7 帧；`+0x99` 同样几乎全部为 255。
- 右移帧：`+0x47=0` 745 帧，`+0x47=255` 仅 4 帧；`+0x99` 同样几乎全部为 0。
- 大量静止 episode 会持续保留 0 或 255，而不是归零，排除“纯水平速度 byte”。
- 明确转向例中，常见时序：`+0x99` 先切换约 5–7 帧 → `+0x47` 再切换约 1–2 帧 → X 开始运动。
- GEO-0006 三人全静止 1200 帧：P1/P2 `+47=0`，P3 `+47=1`；三人 `+99=0`。因此 `+47` 的完整值域不应粗暴限制成二值 0/255，仍可能存在 player/form-specific orientation state。

邻接 word 审计还表明不能把 `+47/+99` 简单吞进偶数对齐 S16：`+46` 的高 byte 在 P3 长期为 `0xD0` 而 P1/P2 为 0，`+98` 的高 byte 又独立在 0/2 间变化；真正稳定跟左右运动对应的是低 byte `+47/+99`。

当前命名：

```text
+0x99 = requested / queued direction state candidate
+0x47 = current facing / orientation state candidate
```

动态行为强支持 `0≈right / 255≈left`，但由于静止 P3 存在 `+47=1`，literal visual facing 的完整编码仍不宣称最终锁死。

## `+0x9E / +0xAA` 交叉判别

初期五组 player capture 中 `+0x9E/+0xAA` 在每个 player×capture 内均无 transition，因此不是逐动画帧 top/bottom offset。

EFIELD-003 enemy 交叉：

- enemy `+0x9E`：72,000 / 72,000 slot-frame 全为 0
- enemy `+0xAA`：12 unique、191 changes、3 changing slots

再把 EFIELD-004 加入做 6 capture × 3 player = 18 个稳定 mode 共变分析：

- `player+0x9E` 观察到 `0/18/30/31/32/34/36/38`
- 除它自身外，没有稳定 U8/U16 字段与它形成恒差、精确副本或一一映射
- 因此它更像独立的 player-specific descriptor/form/render/state 参数，不能叫 width/height/radius/top/bottom
- `+0xAA` 同样不能推广为通用 extent

## Camera / screen relation

已对 EFIELD-003 和 EFIELD-004 两组 3600 帧、全 23 objects 做 common-mode 横向位移搜索。

EFIELD-003：主候选没有形成 3+ active objects 连续共同平移，仅 `+0x9C` 有一个孤立 3-enemy `-2` 事件。

EFIELD-004：也没有形成可靠连续 common-mode run；只有少量 3-enemy 同步小位移，以及一个三玩家 `+0x0B=-1` 的孤立事件，更像 page wrap / 状态事件而不是 camera scroll。

所以自然数据仍**不能**证明 `worldX -> screenX` 的变换或 global camera-X。GEO-0005 人工滚屏 gate 因长期未执行而取消，以避免阻塞共享 Collector；不构成语义证据。

## GEO-0006 结果

`GEO-0006-passive-geometry-camera-20s60-20260831-1657Z` 已 DONE/PASS：

- 1200 frames
- 20 s @ 59.987 Hz
- 1157 distinct raw frames
- 0 read errors / 0 frame-size errors
- read-only / no game writes
- full raw uploaded

这一段玩家本身几乎完全静止，因此没有提供 camera、X wrap、Y-depth 或 Z-jump 新动态，但成为很强的 static control，尤其支持 `+47` 不是纯速度字段。

## top / bottom / left / right 当前状态

- **left/right position anchor**：X local/page 结构已高置信度锁定。
- **horizontal extent**：尚未找到有轴向证明的 live RAM extent；`+9E/+AA` 都不能直接命名为宽度或半径。
- **bottom/floor anchor**：`+0x08` floor/depth 较强；但最终 screen bottom 仍缺 camera/projection。
- **vertical displacement**：`+0x0C/+0x11` modulo+subpixel 模型目前最强。
- **top/bottom sprite bounds**：多轮高频 raw 仍未发现随动画帧变化的独立 live bound 字段；更可能来自 ROM sprite/frame descriptor、shape table 或其他非显式 player RAM byte。

## 下一步

1. 优先用 passive/depth-diversity 数据继续锁 Y page/fraction，不再让人工 gate 阻塞共享 Collector。
2. 继续自动扫描 player animation/body/descriptor family，寻找能通向 sprite/frame bounds 的指针或索引。
3. 实际 ROM bytes 可访问时，对 player sprite geometry consumer 做 68000 xref。
4. camera-scroll 控制只在 READY 路径可靠且确实必要时再做。
5. 后续单独验证 literal facing、left-2P 和 P1/P2/P3 geometry 差异。
6. extent 轴向被证明后再发布正式 top/bottom/left/right 公式。

本报告只属于 GEO 独立研究线，不推进 WOF-045，不作为 Browser production-shadow promotion 证据。
