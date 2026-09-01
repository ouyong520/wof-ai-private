# WOF Alpha Fixed HUD Stability — Fresh Independent Offline QA

- Stage: `ALPHA_FIXED_HUD_STABILITY_QA_V1`
- Tested baseline: `47389e321ca465b551ab30fa0835844e433da5d7`
- Verdict: **PASS — FIXED HUD STABLE FOR ALPHA FALLBACK**
- Product Alpha modified: **NO**
- HUDANCHOR modified/reopened: **NO**
- 真人 Browser required: **NO**（启动提示允许 repository-side deterministic evidence）

## 方法

本轮是 fresh independent offline QA。使用：

1. `product/alpha/wof_alpha_hud.js`、`wof_alpha_hud_model.js`、`wof_alpha_core.js`、`wof_alpha_bootstrap.user.js` 静态控制流/状态审计；
2. synthetic drawing-buffer resize/fullscreen/DPR-like vectors；
3. WebGL state save/draw/restore 审计；
4. `parallel/ALPHAACCEPT/PREP_SELFTEST_RESULT.json` 的只读安全证据交叉核对；
5. 只读核对 frozen `parallel/HUDANCHOR/IMPLEMENTATION_RECOMMENDATION.md` 的 fixed-fallback contract。

## 12 项结果

| # | 检查 | 结果 | 独立证据 |
|---|---|---|---|
| 1 | 固定 HUD 坐标不依赖 player X/Y/Z | PASS | `drawHud()` / `drawTexture()` 的位置只由当前 drawing-buffer W/H 与 HUD box 尺寸决定；没有 player xyz 输入。 |
| 2 | camera scroll 不改变固定 HUD 游戏画面锚点 | PASS | fixed HUD 几何没有 camera/scroll/translation 输入；相同 drawing-buffer + HUD state 得到相同屏幕坐标。 |
| 3 | P1/P2/P3 warning row 切换无旧目标残留 | PASS | warning rows 每次由当前 warnings 重建；内容 key 改变时 `paintBox()` 先 `clearRect()` 整个 HUD backing canvas；不存在目标坐标缓存。 |
| 4 | 多 warning 布局确定性 | PASS | `summarizeWarnings()` 按 target rank P1/P2/P3、side 排序，attack labels 也排序；输出稳定。 |
| 5 | drawing-buffer resize 后重新映射 | PASS | 每次 draw 都重新读取 `gl.drawingBufferWidth/Height`；没有历史 page/sidebar 坐标。 |
| 6 | fullscreen / DPR / viewport-like 变化使用当前 drawing-buffer | PASS | clip-space 转换直接使用当前 drawing buffer；CSS/page viewport 不进入 fixed HUD 几何。 |
| 7 | WebGL state save/draw/restore 不污染游戏 | PASS | `snapGL()` / `restoreGL()` 覆盖 program、buffer、texture、viewport、blend/depth/cull/scissor、blend func/equation、color mask、pixel-store、attrib-0；`upload()` 与 `drawTexture()` 均在 `finally` 恢复。 |
| 8 | diag/stale/disable 旧 warning 清理规则保持 | PASS | diag 立即清 `lastMsg/lastRx` 并重置 paint key；state 超过 1500 ms 不再 fresh；替换内容 paint 前清空 backing canvas。 |
| 9 | HUD unavailable/failure gameplay fail-open | PASS | wrapper 先执行 native game draw，再调用 HUD callback；callback exception 被捕获为 `lastError`，不反向打断 native game draw。Bootstrap attach failure 只记录错误，不替换 game Worker。 |
| 10 | readOnly=true / ramWrites=0 / no input | PASS | 当前 HUD/Core/Bootstrap 没有 gameplay RAM write 或 input injection 路径；ALPHAACCEPT selftest 同时记录 `readOnly=true`, `ramWrites=0`, `inputInjection=false`, `windowWorkerReplacement=false`。 |
| 11 | legacy HUD teardown 不残留 | PASS | Alpha HUD takeover 必须 dispose legacy `WOFHUD`，否则拒绝 takeover；同时 stop `WOFCANVAS`、dispose prior `WOFALPHAHUD`，只保留当前 bridge callback。 |
| 12 | anchored-HUD 未就绪 fixed fallback 可用 | PASS | 当前 Alpha fixed HUD 没有 HUDANCHOR runtime dependency；frozen HUDANCHOR recommendation 明确规定 resolver/projection invalid/stale 时使用 fixed in-game HUD。该目录本轮完全未改。 |

## Synthetic resize / drawing-buffer vectors

固定 warning 采用当前实现：`w=min(520,W-8)`，底部 warning `x=max(4,(W-w)/2)`，`y=max(4,H-h-8)`；top/diag 使用同一当前 W 重新居中，`y=8`。

| Drawing buffer | Warning h | 计算后的 warning rect `(x,y,w,h)` |
|---|---:|---|
| 1280×720 | 108 | `(380,604,520,108)` |
| 1920×1080 | 108 | `(700,964,520,108)` |
| 2560×1440 | 108 | `(1020,1324,520,108)` |
| 780×1280 | 108 | `(130,1164,520,108)` |
| 390×844 | 108 | `(4,728,382,108)` |

这些向量表明 buffer 尺寸变化后使用的是新 W/H；没有复用历史 CSS/page 坐标，因此固定 HUD 不会因为 resize/fullscreen/DPR-like buffer 变化漂到 sidebar/page UI。

## Blockers

**None.** 未发现 P0/P1/P2 产品级 fixed-HUD stability blocker。

## Frozen/reference lane

`parallel/HUDANCHOR/**` 仅作只读 reference contract 核对；没有修改、没有重新开启其 implementation lane。人物头顶 anchored HUD 仍然是后续能力，不阻塞本 Alpha fixed fallback。

## Next gate

回到既有 PM / release-hold flow；本 QA 不自行修改 Alpha 产品或宣布 release。

## Stop condition

**PASS — FIXED HUD STABLE FOR ALPHA FALLBACK**
