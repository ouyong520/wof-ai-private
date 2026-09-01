# WOF-052L 10-Room Long Capture — Fresh Independent QA Start Prompt

你负责 WOF-052L 10 房间长采集链的全新独立 QA。

这是 QA，不是实现线。不要修改现有 Fleet / Recorder / Analyzer 核心实现来让测试通过；发现 P0/P1 时写明 blocker，交给 fresh fix stage。

读取：
- `parallel/WOF052L_LIVE_CAPTURE/**`
- `parallel/WOF052L_RECORDER/**`
- `parallel/BROWSER_FLEET/**`
- `parallel/WOF052L_ANALYSIS/**`
- 当前 Discovery V2 结果
- `parallel/PM/CHINESE_UI_UX_REQUIREMENT.md`

写入范围：仅 `parallel/WOF052L_LIVE_CAPTURE_QA/**`。

## 独立验证重点

必须重新验证：
- 1 / 5 / 10 endpoint orchestration；
- 10 个独立 profile/CDP endpoint 不串房；
- Discovery V2 admission 不是旧 `type=worker + URL` 单一路径；
- WASM/heap ready gate；
- exact World 921031 SHA gate；
- wrong identity / ambiguous Worker fail closed；
- 单房崩溃、reload、disconnect 只结束该房；
- 其余房间继续采；
- 新房间可加入；
- per-room/checkpoint/merged/fleet merged 自动落盘；
- Ctrl+C 正确 finalize；
- analyzer watch 自动读取新数据；
- A4704/A4712/T18/T23 汇总字段不会跨房混淆；
- no-waste preflight 能阻止旧 discovery/危险 CDP 方法；
- readOnly=true / ramWrites=0 / inputInjection=false；
- owner-facing 全中文；
- 不要求 DevTools/Worker Console/粘 JS。

优先用 mock/fake CDP endpoints 和已有 fixtures 做 10-room failure-isolation pressure regression，避免 owner 白跑一小时才发现编排 bug。

## Verdict

只有两种停止结果：
- `PASS — READY FOR ONE REAL 10-ROOM LONG CAPTURE`
- `BLOCKED — <精确 P0/P1>`

不要自己声称真实一小时数据已经采到。