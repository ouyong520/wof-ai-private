# RC2 Alpha Bootstrap Acceptance Requirements

更新时间：2026-09-01

本文件是给 `ALPHA_RC2_FIX` owner 的实现/验收合同。本 lane 不修改 `product/alpha/**`。

## A. 必须交付的用户路径

RC2 必须提供一个明确、唯一支持的普通用户加载路径：

**WOF Alpha Bootstrap Chrome/Chromium extension -> 自动注入 live `gstyphoon.js` Worker -> 自动注入 top page -> end-to-end handshake。**

关闭 `ALPHAQA-004` 时，用户不得需要：

- 打开 DevTools；
- Console 粘贴命令；
- 切换 execution context；
- 手工识别 Worker；
- 知道 `gstyphoon.js` 名字。

工程阶段可以用 unpacked extension 做开发验收；面向普通 Alpha 用户的发布路径不能要求 Developer Mode / Load unpacked。

---

## B. Bootstrap implementation requirements

### B1. Minimal permissions / activation

- `debugger` 权限必须有明确用途，仅用于本次 bootstrap。
- 只允许受支持 WOF game origin。
- 默认由用户明确点击启动；不得后台静默 attach 任意页面。
- 成功或失败后都必须 detach debugger。

### B2. Canonical product entry point

- Bootstrap 必须执行 canonical `product/alpha/wof_alpha_loader.js`。
- Bootstrap 不得复制/分叉 Alpha predictor、RAM offsets、warning rules 或 HUD renderer。
- release descriptor 必须声明 expected release/version；推荐 immutable URL/digest。

### B3. Unique Worker selection

在任何 Alpha 产品代码执行之前，bootstrap 必须把 Worker 选择收敛为 exactly one candidate：

```text
related worker target
AND gstyphoon.js URL predicate
AND approved read-only runtime identity predicate
```

- 0 candidate -> fail closed。
- >1 candidate -> fail closed。
- runtime identity probe 异常 -> fail closed。
- target destroyed/replaced mid-bootstrap -> fail closed 或重新从零开始，不得继续对旧 session 声称成功。

不要使用 first-worker / newest-worker / arbitrary-worker fallback。

### B4. Worker-first ordering

必须先让 Worker runtime 成功，再安装 top HUD。

最低 Worker success check：

- `self.WOFALPHA` 或 RC2 等价 runtime handle 存在；
- release/version 正确；
- engine/running 正常；
- runtime identity 通过；
- no unsupported-runtime diagnostic；
- read-only invariant 保持。

Worker 失败时不得继续安装一个“看起来正常”的 HUD。

### B5. Top HUD check

Worker 成功后才能执行 top loader。

最低 top success check：

- top Alpha handle 存在；
- HUD handle 存在；
- WebGL draw hook 安装成功；
- release/version 正确；
- no initialization exception。

### B6. End-to-end success gate

`ALPHAQA-004` 的真正通过条件不是“两个 eval 都没报错”，而是 end-to-end live link 成立。

扩展必须等待/验证：

```text
worker runtime OK
AND top HUD OK
AND HUD received fresh state/ready from selected Worker
AND message freshness within stale threshold
AND release/session identity matches
```

RC2 修复 cross-tab/session contamination 后，这里必须绑定当前 bootstrap session/nonce/channel，不得接受其他标签页发来的旧 state。

只有这时可以向用户显示：

```text
WOF Alpha 已启用
```

否则统一视为未启用。

### B7. Cleanup

每种失败都必须：

- 停止继续注入；
- 尽可能调用本次已安装 Alpha runtime/HUD 的公开 stop/dispose；
- 清理 bootstrap 临时 listener/session；
- detach debugger；
- UI 明确显示未启用。

不得残留 bootstrap 自己的持续 RAM polling/debugging。

---

## C. Required real-browser acceptance matrix

至少在项目当前支持的 Chrome/Chromium 环境做以下真实 Browser 测试。

### C1. Happy path — Worker already running

前置：游戏已经运行，`gstyphoon.js` Worker 已存在。

操作：只点击扩展“启动 WOF Alpha”。

PASS：

- 无 DevTools；
- 无 Console；
- 自动找到 Worker；
- Worker runtime 启动；
- top HUD 启动；
- HUD connected/fresh；
- 扩展显示已启用；
- debugger 随后 detach；
- Alpha 继续运行。

这是最关键测试，因为它证明不依赖“抢在 Worker 创建前”。

### C2. Game not started

前置：页面打开但 emulator Worker 尚未创建。

PASS：

- 不向任意 Worker 注入；
- 显示可恢复的“尚未检测到游戏 Worker”；
- 用户启动游戏后再次点击即可成功；
- 不要求 reload/DevTools。

### C3. Multiple unrelated workers

前置：页面存在其他 Worker。

PASS：

- 只按 related-target + `gstyphoon.js` + runtime predicate 选择；
- 不向 unrelated Worker 执行 Alpha loader。

### C4. Ambiguous game Worker

制造或模拟两个都满足 URL predicate 的候选，但 identity 无法唯一化。

PASS：fail closed，不猜。

### C5. Wrong/unsupported runtime

对不满足批准 identity predicate 的 Worker 测试。

PASS：

- Worker 产品代码不启动；
- top HUD 不显示“已启用”；
- 用户看到不受支持提示。

### C6. Worker eval failure

模拟 loader fetch/parse/evaluate/runtime-start failure。

PASS：

- top HUD 不被当成成功路径安装；
- debugger detach；
- 明确失败。

### C7. HUD eval failure

Worker runtime 已启动，但 top HUD 初始化失败。

PASS：

- 不显示成功；
- 尽可能 stop Worker Alpha runtime，避免用户误以为 UI 只是没显示；
- detach。

### C8. No fresh bridge state

Worker/top objects 都存在，但故意让 Worker-to-HUD state 不到达或 stale。

PASS：

- 不显示 `WOF Alpha 已启用`；
- 明确 `Alpha 未连接到游戏数据`。

### C9. Cross-tab isolation

同时打开两个游戏 tab。

PASS：

- 在 tab A 点击 bootstrap 只启动/确认 A；
- A 的 success handshake 不能被 B 的 BroadcastChannel/state 满足；
- tab B 不应因此显示 Alpha 已启用。

这项要和 ALPHAQA 的 cross-tab/session 修复一起验收。

### C10. Re-run / idempotence

在已成功运行 Alpha 的 tab 再点一次“启动 WOF Alpha”。

PASS：

- 不出现双 engine/timer/HUD；
- 要么返回 already-running success，要么按产品公开 stop/dispose 后干净重启；
- handshake 仍是当前 session。

### C11. Page reload

成功后 reload 页面。

PASS：

- 旧 Worker/session 不被新页面错误复用；
- 默认显示未启用，直到新 session bootstrap 成功；
- 若以后实现自动启动，也必须重新做 identity + handshake。

### C12. Debugger unavailable

主动打开会冲突的 DevTools/debugger 状态或模拟 attach failure。

PASS：

- bootstrap 不继续半套安装；
- 明确提示关闭冲突调试器后重试；
- 无假成功。

---

## D. QA evidence required to close ALPHAQA-004

RC2 owner 应给 ALPHAQA 至少提交：

1. 扩展 manifest/implementation 路径与 release id；
2. 一段普通用户安装说明；
3. C1 happy-path 真实 Browser 证据；
4. C2 no-worker fail-closed 证据；
5. C3/C4 wrong-or-ambiguous Worker 不误注入证据；
6. C8 end-to-end handshake failure 不假成功证据；
7. C9 双 tab isolation 证据；
8. `product/alpha/**` read-only / no input injection / `ramWrites=0` 仍成立的回归证据；
9. 成功/失败后 debugger 已 detach 的证据。

ALPHAQA 不应仅凭 README 更新或“扩展按钮能点”关闭 P1。

---

## E. Stop / rejection criteria

以下任一存在，`ALPHAQA-004` 仍应保持 OPEN/BLOCKED：

- 普通用户还要打开 DevTools；
- 仍要求用户选择 `gstyphoon.js` context；
- top HUD 可以在 Worker runtime 未启动时显示“Alpha 已启用”；
- bootstrap 会猜测多个 Worker 中的一个；
- bootstrap 依赖必须在 Worker 创建前手工抢时机；
- 使用未经真实 Browser 证明的 blob/wrapper Worker 替换 emulator；
- cross-tab 旧消息可以满足当前 tab 的 success gate；
- debugger attach 后不 detach；
- Bootstrap 开始承载 predictor/产品逻辑，形成第二套 Alpha 实现。

---

## F. RC2 owner 最小实现顺序

1. 建一个最小 MV3 bootstrap extension shell。
2. 只实现 current-tab attach / detach。
3. 实现 related Worker discovery + exact-one identity probe。
4. 用 CDP 在 Worker 执行 canonical loader并读取 status。
5. 用 CDP 在 top page 执行 canonical loader并读取 HUD status。
6. 接 end-to-end fresh/session handshake。
7. 加失败清理与用户状态 UI。
8. 跑 C1-C12。
9. 把普通用户分发从 unpacked 迁到受控签名/商店分发。
10. 交给 ALPHAQA 复验。

完成以上后，bootstrap lane 不需要继续研究 Worker constructor wrapper。