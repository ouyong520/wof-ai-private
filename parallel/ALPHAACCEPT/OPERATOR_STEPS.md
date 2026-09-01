# WOF Alpha Browser Acceptance V2 — 用户操作

## 现在不要运行

当前状态：

**验收准备已完成，正在等待 Safe Transport Integration。**

只有当集成阶段明确写出：

`INTEGRATION IMPLEMENTED — READY FOR BOUNDED REAL BROWSER ACCEPTANCE`

才执行下面的一次真人验收。

## 未来最终操作

集成完成后，用户只需要：

1. 用中文 Launcher / Toolkit 启动 WOF。
2. 正常进入一个房间，确认游戏现在可以正常移动、攻击、继续游玩。
3. 点击一次：
   **“当前房间可以正常操作，开始验收”**
4. 之后不要打开 DevTools，也不要切 Worker Console，不要粘贴 JS。工具会自动完成 current pair、identity、stale/diag、rebind、旧 generation/nonce 拒绝和安全状态检查。
5. 最后只保留工具生成的一个 JSON。

不需要为了验收故意寻找稀有攻击。已经批准的 T18 条件如果自然出现，工具会自动记录；没有出现时不会因此判定基础设施失败。

## 最终 JSON 结果

可能出现：

- `PASS — REAL BROWSER ACCEPTANCE V2`
- `FAIL — REAL BROWSER ACCEPTANCE V2`
- `INCOMPLETE — REAL BROWSER ACCEPTANCE V2`
- `BLOCKED — TRANSPORT INTEGRATION NOT READY`

如果是 `PASS`，把这个 JSON 交给 QA/PM。PASS 只是 Browser 验收证据，不等于自动发布 Alpha。

如果是 `FAIL`，不要反复重试直到碰巧通过。保留第一次有效失败 JSON，交给 QA/PM。

如果是 `INCOMPLETE`，只处理 JSON 明确指出的环境问题后再跑一次。

如果是 `BLOCKED`，说明 transport 或离线 gate 还没准备好，不需要用户做额外技术操作。

## 用户不需要做的事情

- 不开 DevTools；
- 不选 Worker Console；
- 不粘贴 JavaScript；
- 不检查 RAM；
- 不复制长命令；
- 不手工比较大量 Console 字段；
- 不制造攻击研究样本。

## 安全说明

验收工具本身不写游戏 RAM，不注入键盘/鼠标/手柄输入，不替换 `window.Worker`，不修改游戏速度。

最终 JSON 必须保持：

```text
readOnly=true
ramWrites=0
inputInjection=false
```
