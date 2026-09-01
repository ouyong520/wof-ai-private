# WOF Evidence Auto-Ingestor — Fresh Start Prompt

你负责 WOF 项目新的项目加速工具：Evidence Auto-Ingestor / 自动结果整理器。

这不是攻击研究，不修改 Alpha 产品逻辑。

开始前读取当前：
- `WOF_TOOLKIT.cmd`
- `parallel/OPTOOLKIT/**`
- `parallel/PYLAUNCH/**`
- `parallel/WOF052L_RECORDER/**`
- `parallel/BROWSER_FLEET/**`
- `parallel/PM/CHINESE_UI_UX_REQUIREMENT.md`

目标：把以后所有 Windows 真人测试、Recorder、Fleet、Launcher、Regression、Diagnostics 产生的 JSON/日志自动整理，减少人工上传、辨认、合并、找文件的时间。

优先实现一个独立目录，例如 `parallel/EVIDENCE_INGESTOR/**`，并可被 Toolkit 调用。

要求：
- 默认监控/扫描 `%USERPROFILE%\Documents\WOF_RESULTS`；
- 自动识别 PYLAUNCH proof、WOF-052L room/fleet merged、Browser Fleet 状态、Regression、Diagnostics；
- 校验 JSON 是否可读、schema/版本是否已知；
- 自动检查并汇总 `readOnly` / `ramWrites` / `inputInjection` / World 921031 等安全字段；
- 自动去重；
- 自动按 run / room / tool / date 分类；
- 自动生成一个紧凑 `SUMMARY.json`；
- 同时生成一个给普通用户看的中文 `结果汇总.txt`；
- 标出损坏、缺字段、身份不匹配、RAM writes 非 0、重复文件等异常；
- 不删除原始证据；
- 不修改已有结果文件；
- 单个坏文件不能阻止其他结果整理；
- 可以一键运行，也可以被 `WOF_TOOLKIT.cmd` 集成；
- 所有用户可见提示默认简体中文。

最终目标：以后我只需要把一个 `SUMMARY.json` 或一个结果包交给 ChatGPT，而不是找几十个文件。

不要修改 `product/alpha/**`。
不要修改 PYLAUNCH 的 Worker discovery 逻辑。
不要修改 WOF-052L 采集逻辑。
不要写游戏 RAM。
不要注入游戏输入。

做到仓库侧 READY，并给出最小 Windows proof；如果现有 Toolkit 已有一部分能力，优先复用，不重复实现。