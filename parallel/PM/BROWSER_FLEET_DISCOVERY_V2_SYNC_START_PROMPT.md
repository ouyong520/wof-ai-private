# WOF Browser Fleet Worker Discovery V2 Sync — Fresh Start Prompt

你负责 WOF Browser Fleet Manager 的独立兼容修复线。

仓库：`ouyong520/wof-ai-private`

## 背景

真人 Windows 已证明旧 PYLAUNCH 的 `type=worker + gstyphoon*.js URL` 硬过滤会漏掉真实 WOF Worker surface。PYLAUNCH 已引入 discovery_v2；独立 WORKER_SURFACE 审计同时指出 Browser Fleet 的 cheap Worker status 也存在相近 type/URL prefilter 风险。

## 读取

- `parallel/WORKER_SURFACE/**`
- 最新 `parallel/PYLAUNCH/wof_launcher/discovery_v2.py`（只读参考，不修改 PYLAUNCH）
- `parallel/BROWSER_FLEET/**`
- `parallel/PM/CHINESE_UI_UX_REQUIREMENT.md`

## 写入范围

仅 `parallel/BROWSER_FLEET/**`。
不要修改 `parallel/PYLAUNCH/**`。
不要修改 `parallel/WOF052L_RECORDER/**`。
不要修改 `product/alpha/**`。

## 目标

让 Browser Fleet 的每实例 Worker/页面状态不再依赖旧的 direct `worker + gstyphoon URL` 单一路径。

需要：
- 复用/移植被证明安全的 page-related target / auto-attach / iframe/worker topology 思路；
- 状态仍只是 cheap indicator，不冒充 PYLAUNCH 的权威 World 921031 identity proof；
- 支持 Worker URL shape 变化、related target、reload/recreated Worker；
- 多实例严格绑定各自 CDP port/profile，不能串房；
- stale Fleet entry fail-open；
- 一实例 Worker discovery 异常不影响其他实例；
- 中文 owner 状态保持；
- readOnly=true / ramWrites=0 / inputInjection=false；
- 不替换 window.Worker；
- 不写 RAM、不注入输入。

## 测试

至少覆盖：
- direct worker backward compatibility；
- related-target-only；
- URL mismatch but related runtime；
- iframe -> worker；
- reload/recreated worker；
- 10 instance isolation；
- stale/missing endpoint；
- no cross-port association。

## Stop condition

**BROWSER FLEET DISCOVERY V2 READY**，并给出仓库侧 regression PASS；真人 Windows 只保留一个最小 bounded proof。