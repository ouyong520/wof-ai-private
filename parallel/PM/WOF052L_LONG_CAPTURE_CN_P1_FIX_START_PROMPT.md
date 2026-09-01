# SUPERSEDED — WOF-052L Long Capture Chinese P1 Fix

本 narrow stage 已被更完整且同一写入域的一次性修复阶段取代：

`parallel/PM/WOF052L_RECORDER_DISCOVERY_V2_HARDENING_START_PROMPT.md`

原因：Cross-component audit 同时发现 Recorder 的 cross-page shared Worker P0、endpoint confinement、URL-scheme gate、direct-association P1。为了避免“先修中文 -> 再修 Discovery -> 再让 Owner 重测”，这些问题应在一个 fresh Recorder hardening stage 中一次关闭。

如果任何线程读取到本文件：

1. 不修改任何实现；
2. 输出：`ALREADY COMPLETE — SAFE TO CLOSE — 当前线程空闲（本 stage 已被 consolidated hardening supersede）`；
3. 停止。

由 PM 决定是否另开并派发新的 consolidated stage。