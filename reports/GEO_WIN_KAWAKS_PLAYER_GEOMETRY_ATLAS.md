# WinKawaks P1/P2/P3 人物几何字段地图 — GEO 研究线

> 证据边界：本文仅记录 WinKawaks normalized CPS RAM 的 discovery evidence。不得直接作为 Browser/WASM production 证明；不修改 production-shadow；不推进 WOF-045；全程只读、无游戏内存写入。

## 对象布局与证据

- P1 `0xFFBE1C`
- P2 `0xFFBEFC`
- P3 `0xFFBFDC`
- stride `0xE0`
- self-id `+0x7C = 0/4/8`
- fresh Collector mapping：唯一 `xor3`

主要动态集：GEO-0001 600 帧、GEO-0003 600 帧、GEO-0004 600 帧，以及复用 EFIELD-002/003 两组 3600 帧完整 23-object raw。所有证据均为 WinKawaks-local discovery。

## 当前字段地图

| offset | 当前解释 | 置信度 | 关键证据 |
|---|---|---|---|
| `+0x04` | local X integer byte | 高 | 随横移变化；与 `+0x0B` 在 0/255 wrap 同帧联动 |
| `+0x0B` | X page/high byte，单位约 256 | 高 | 多组独立 wrap 事件能重建连续 X；早期 facing 假设已撤销 |
| `+0x08` | floor/depth Y integer | 高候选 | P1/P2/P3 典型值 48/72/96，横移与普通跳跃期间稳定 |
| `+0x0C` | vertical/Z integer byte，modulo 256 | 高 | 正向跳跃弧与负向连续轨迹均重复出现 |
| `+0x11` | Z subpixel/fraction phase | 中高 | 与 `+0x0C` 近逐次联动；值域常为 0/32/64/.../224 |
| `+0x47` | current horizontal direction/orientation candidate | 中高 | 右移偏 0、左移偏 255；变化可先于 X |
| `+0x99` | desired/queued horizontal direction candidate | 中高 | 常先于 `+0x47` 切换 |
| `+0x2D` | active-motion state family | 中高 | moving 多为 2、static 多为 0 |
| `+0x35` | complementary moving/static state | 中高 | moving 几乎总为 0、static 多为 255 |
| `+0x67` | timer/counter，非几何 | 中高 | countdown-like |
| `+0x9C` | lagged/render local-X cache | 高 | 与 `+0x04` 高相关、运动时常约滞后一帧 |
| `+0xA2` | cached floor/depth integer | 高 | 精确等于 `+0x08` |
| `+0xA3` | X page/cache family | 高 | 与 `+0x0B` 高度一致；明确不是 facing |
| `+0x9E` | player-specific stable form/render field | 中 | player 中长期稳定 30–38；enemy 同 offset 72,000/72,000 为 0 |
| `+0xAA` | player-specific metadata candidate | 低 | player 中稳定，但 enemy 同 offset 为动态低基数字段，通用 extent 假设已降权 |

## X：local + page 已锁得较强

跨多个独立 capture 的 wrap 事件：

- GEO-0003 P1：local `252 -> 0`，page `0 -> 1`，重建 `252 -> 256`
- GEO-0003 P2：local `1 -> 254`，page `2 -> 1`，重建 `513 -> 510`
- EFIELD-003 P1：local `254 -> 2`，page `0 -> 1`，重建 `254 -> 258`
- EFIELD-003 P3：local `248 -> 0`，page `0 -> 1`，重建 `248 -> 256`

当前整数模型：

```text
worldX ~= 256 * U8(+0x0B) + U8(+0x04)
```

把相邻 `+0x06..07` 当 X 高位会在这些事件产生约 ±252 px 假跳变，因此“连续 4-byte word-pair X”模型已被否定。`+0x05` 在当前样本一直为 0，尚不能证明是 X fraction。

## floor/depth：`+0x08` 比 `+0x08..09` 8.8 更合理

旧的 `U16BE(+0x08..09)/256` 工作解释已降级。`+0x08` 单字节直接得到 P1/P2/P3 = 48/72/96，恰好等距 24；`+0x09` 在现有场景中保持 player/form-specific 常量，没有动态证据证明它是 Y fraction。

因此当前以 `+0x08` 作为 floor/depth anchor，`+0x09` 暂列 unknown。真正的 Y page/fraction 需要 depth-only 场景验证。

## Z：`+0x0C` + `+0x11`，不是 `+0x0C..0D`

`+0x0D` 在整段跳跃/下落中固定（例 P1=52、P2=64、P3=0），因此不是实时 Z fraction。

正常正向轨迹：

```text
0 -> 7 -> 10 -> 13 -> 16 -> ... -> 30 -> ... -> 7 -> 3 -> 0
```

另一些负向轨迹从：

```text
0 -> 255 -> 254 -> 253 -> 251 -> 248 -> ... -> 129 -> 118 -> 106 -> ...
```

开始。将 `+0x0C` 作为 modulo-256 integer 并按路径 unwrap 后，第二类轨迹可连续解释为 0、-1、-2、-3、-5、-8 ... -127、-138、-150 ...，而不是在 signed 127/128 处制造假断裂。

同时 `+0x11` 在这些轨迹中以 0/32/64/96/128/160/192/224 等量化值随 `+0x0C` 变化，符合亚像素相位。当前 working model：

```text
Z ~= unwrap_mod256( U8(+0x0C) + U8(+0x11)/256 )
```

这仍是 discovery 级模型，但显著优于旧的 `S16/U16(+0x0C..0D)/256`。

## Render/cache 块纠错

系统扫描 GEO-0003、GEO-0004、EFIELD-003 的 `+0x90..+0xAF` 后，没有发现任何 byte 在 Z-change 帧稳定等于、滞后或共享 `+0x0C` delta。

- `+0x9C`：保留 X/render cache
- `+0xA2`：floor/depth cache
- `+0xA3`：X page cache
- `+0xA4`：所有检查流中保持 0；**旧 `A4=render-Z` 假设正式撤销**
- 当前没有在 `0x90..AF` 内锁到 live render-Z cache

## `+0x9E / +0xAA` 交叉判别

五组 player capture 共约 9000 帧中，`+0x9E/+0xAA` 在每个 player×capture 组合内部均 0 transition，说明它们不是逐动画帧 top/bottom offset。

进一步用 EFIELD-003 的 20 enemy objects 交叉：

- enemy `+0x9E`：72,000/72,000 slot-frame 全为 0
- enemy `+0xAA`：12 unique、191 changes、3 changing slots

所以：

- `player+0x9E` 可保留为 player-specific form/render field，但不能推广为所有 0xE0 对象通用 body extent。
- `player+0xAA` 的 width/height/extent 解释显著降权。

## Camera / screen relation

对 EFIELD-003 3600 帧、全部 23 objects 做 common-mode 横向位移搜索：`+0x04/+0x07/+0x08/+0x0B` 等主候选没有出现 3+ active objects 同帧相同非零 delta；`+0x9C` 仅有 1 个孤立的 3-enemy `-2` 事件，无连续 run。

因此自然样本没有 usable camera-scroll episode，尚不能证明 `worldX -> screenX` 的变换或 global camera-X。

`GEO-0005` 人工滚屏 gate 因长期未执行而被取消，仅为避免阻塞共享 Collector，不构成语义证据。`GEO-0006` passive 20s task 已排队但最近一次检查尚无 status，提示本地 Collector 当前可能未轮询。

## Direction / motion

- strongest direction pair：`+0x99 -> +0x47 -> X movement`
- 相对运动支持 `0≈right / 255≈left`，literal visual facing 仍需已知朝向控制
- moving/static 优先：`+0x2D`、`+0x35`，其次 `+0x28/+0x36`

## top / bottom / left / right 当前状态

- **left/right anchor**：X 位置结构已高置信度锁定，但 horizontal extent 尚未找到轴向证明。
- **bottom/floor**：`+0x08` floor/depth anchor 已较强；screen projection 仍缺 camera relation。
- **vertical offset**：`+0x0C/+0x11` 已形成 modulo+subpixel 模型。
- **top/bottom sprite bounds**：约 9000 帧仍未发现随动画帧变化的独立 live bound 字段；越来越像来自 ROM sprite/frame descriptor、shape table 或 form-level geometry，而非单一 RAM byte。

## 下一步

1. 若本地 Collector 恢复，优先用 passive/depth-diversity capture 验证 Y page/fraction，而不是再用人工 gate 阻塞队列。
2. 继续寻找 ROM/frame descriptor 的 player sprite geometry consumer；实际 ROM bytes 可用时做 68000 xref。
3. camera-scroll 只在 Collector/READY 链路可靠后再做控制实验。
4. 后续单独锁 literal facing、left-2P 和 P1/P2/P3 geometry 差异。
5. extent 轴向被证明后再发布正式 top/bottom/left/right 公式。

本报告只属于 GEO 独立研究线，不推进 WOF-045，不作为 Browser production-shadow promotion 证据。
