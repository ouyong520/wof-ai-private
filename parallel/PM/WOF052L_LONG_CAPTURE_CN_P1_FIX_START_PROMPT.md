# WOF-052L 10-Room Long Capture — Fresh Chinese P1 Fix Start Prompt

stageId: `WOF052L_LONG_CAPTURE_CN_P1_FIX_V1`

## 启动去重守卫（必须最先执行）

开始任何实现前必须先读取：
- `parallel/PM/STAGE_DEDUP_GUARD.md`
- GitHub 默认分支最新状态
- 本阶段可能已有的 RESULT / STATUS / stop-condition commit

然后按顺序执行：
1. 如果本阶段 stop condition 已经满足，立即停止，输出：`ALREADY COMPLETE — SAFE TO CLOSE — 当前线程空闲`。
2. 如果 `parallel/PM/STAGE_CLAIMS/WOF052L_LONG_CAPTURE_CN_P1_FIX_V1.json` 已存在且该阶段尚未完成，立即停止，输出：`ALREADY CLAIMED — SAFE TO CLOSE — 当前线程空闲`。
3. 只有确认未完成、未被认领后，才允许用 GitHub create-file 原子创建上述 claim 文件；创建失败视为已被其他线程抢先认领，重新读取后停止。
4. claim 成功后输出：`CLAIM ACQUIRED — WORK STARTED`，再继续下面任务。
5. 达到 stop condition 后把 claim 更新为 `COMPLETE`；精确 blocker 则更新为 `BLOCKED`。不要删除 claim。

不要因为任务已完成/已认领而自行扩展相似工作。让本线程直接空闲退出，由 PM 补其他 stage。

你负责 WOF-052L 10-room long capture 的 fresh 最小 P1 修复线。

仓库：`ouyong520/wof-ai-private`

## 背景

Fresh independent QA 已给出明确 blocker：

`BLOCKED — P1 owner-facing 简体中文验收失败`

权威 QA 结果：
- `parallel/WOF052L_LIVE_CAPTURE_QA/RESULT.md`

问题不在 Discovery V2、World 921031 identity gate、multi-room isolation 或采集逻辑本身，而在正常 owner long-capture 路径仍会直接看到 English-only Fleet Recorder 状态/错误。

已确认的 owner-visible English 包括但不限于：
- `Fleet #<id>: WAITING <host>:<port>; other rooms continue.`
- `Fleet #<id>: CDP connect failed safely: <error>`
- `Fleet #<id>: Browser OK — <endpoint>`
- `WOF-052L fleet recorder #<id> -> <host>:<port>`

## 开始前读取

- `parallel/WOF052L_LIVE_CAPTURE_QA/RESULT.md`
- `parallel/PM/CHINESE_UI_UX_REQUIREMENT.md`
- `parallel/WOF052L_RECORDER/**`
- `parallel/WOF052L_LIVE_CAPTURE/**`
- 当前 Discovery V2 / long-capture regression 结果

## 写入范围

主要写入：
- `parallel/WOF052L_RECORDER/**`

只有当 owner long-capture wrapper 本身确实需要极小适配时，才允许修改：
- `parallel/WOF052L_LIVE_CAPTURE/**`

不要修改：
- `parallel/BROWSER_FLEET/**`
- `parallel/PYLAUNCH/**`
- `parallel/WOF052L_ANALYSIS/**`
- `product/alpha/**`

## 唯一目标

关闭这个 P1：正常 1 / 5 / 10-room owner workflow 不再要求理解 English-only status/error。

必须做到：
- `FleetRecorderManager.ensure_browser()` owner-visible 状态改为简体中文；
- `FleetRecorderManager.run_managed()` owner-visible 状态改为简体中文；
- 检查 `FleetSupervisor.run()` / child startup / disconnect / retry / finalize 路径是否还有直接 English-only owner text；
- endpoint、CDP、WOF-052L、host:port 等技术标识可以保留；
- 错误第一层必须是中文可理解说明，必要技术详情放第二层；
- Windows 10/11 CMD / UTF-8 / 中文路径不乱码；
- 不改变 JSON schema/internal key；
- 不改变 Discovery V2 admission semantics；
- 不改变 World 921031 SHA gate；
- 不改变 room isolation / fail-open behavior；
- 不改变 capture cadence / checkpoint / analysis handoff；
- 不新增攻击研究。

## 回归

至少覆盖：
- endpoint waiting；
- CDP connect failure；
- Browser connected；
- child recorder startup；
- room disconnect / retry；
- one-room failure does not stop others；
- 10-room simulated supervisor output；
- owner-visible output 无 English-only status/error；
- readOnly=true；
- ramWrites=0；
- inputInjection=false；
- no window.Worker replacement。

修复后不要自己宣布长采集真人 PASS。

## Stop condition

达到：

`FIX READY — READY FOR FRESH 10-ROOM LONG CAPTURE QA RETEST`

并把结果写入新的 fix result/status 文件，明确列出：
- 修改文件；
- 回归数量和 PASS；
- 中文 UX 检查；
- 安全边界；
- fresh QA retest 应重新验证的精确项目。
