# WOF-052L Multi-Room Long Live Capture — Fresh Start Prompt

你负责 WOF-052L 的真人多房间长采集执行准备与运行阶段。

目标不是重新开发 Recorder，而是把已经 READY 的 Browser Fleet + WOF-052L Recorder 真正拼起来跑长采集。

读取：
- `parallel/BROWSER_FLEET/**`
- `parallel/WOF052L_RECORDER/**`
- `parallel/WOF052L_ANALYSIS/**`（若已存在）
- 当前 PYLAUNCH Worker discovery blocker
- `parallel/PM/CHINESE_UI_UX_REQUIREMENT.md`

原则：
- 1 小时不是硬上限；目标是 10 房间并行、持续长时间；
- 如果用户开 10 个房间，10 个都应自动采；
- 房间关/掉线/刷新只结束该房间，其余继续；
- 新房间随时加入；
- 自动保存 per-room / checkpoint / merged；
- 自动进入分析器（若分析器 READY）；
- 不要求用户逐房间点 Start；
- 不要求 DevTools/Worker Console/粘 JS。

本阶段先做：
1. 审核 Fleet + Recorder 当前拼接是否已具备一次启动全部工作的条件；
2. 生成一个中文 owner 操作入口，理想为：双击 -> 选择保存目录（只需第一次）-> 输入房间数量 -> Fleet + Recorder 自动启动；
3. 自动显示：在线房间、正在采集、已完成、T18、candidate、A4704、A4712、T23、只读/RAM writes；
4. 如果当前 Worker discovery blocker 会阻止采集，明确等待 PYLAUNCH/Worker Surface 根因修复，不要让用户白跑一小时；
5. blocker 一旦关闭，立刻把真人操作压成一次，并开始 10 房间长采集。

停止条件：
- **READY FOR 10-ROOM LONG CAPTURE**，只剩用户一次双击+开房；或
- 一个精确 blocker。

安全：read-only / ramWrites=0 / no input injection / no Worker replacement / no product/alpha changes。