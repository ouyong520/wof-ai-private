# WOF Evidence Auto-Ingestor / 自动结果整理器

仓库侧状态：**READY**。

这是只读项目加速工具。它扫描 Windows 统一结果目录，把 PYLAUNCH、WOF-052L、Browser Fleet、Regression、Diagnostics 的 JSON/日志整理成一个紧凑摘要；不修改 `product/alpha/**`，不修改采集/Worker discovery 逻辑，不写游戏 RAM，不注入游戏输入。

## 最简单用法

二选一即可：

1. 双击根目录 `WOF_TOOLKIT.cmd`，选择 **8 自动整理并打包结果**。
2. 或直接双击 `parallel\EVIDENCE_INGESTOR\RUN_EVIDENCE_INGESTOR.cmd`。

默认扫描：

```text
%USERPROFILE%\Documents\WOF_RESULTS
```

每次运行都会新建：

```text
%USERPROFILE%\Documents\WOF_RESULTS\_自动整理\YYYYMMDD_HHMMSS\
    SUMMARY.json
    结果汇总.txt
    WOF_结果包_YYYYMMDD_HHMMSS.zip
```

原始证据只读，不删除、不移动、不覆盖。`_自动整理` 自己的输出会在后续扫描中自动排除，避免重复吞入自己。

## 自动识别

当前已登记：

- PYLAUNCH Windows proof：`wof-python-launcher-windows-proof-v1`
- WOF-052L room / merged：`wof-052l-recorder-v1`
- WOF-052L Browser Fleet merged：`wof-052l-fleet-supervisor-v1`
- Browser Fleet status：`wof-browser-fleet-v1`
- Operator Toolkit Regression / Diagnostics：支持当前 `wof-windows-operator-toolkit-v2-cn`，并通过 `run.py` 兼容后续 `wof-windows-operator-toolkit-v*` 版本
- Alpha RC5 regression result
- Alpha RC5 independent QA result
- `.log`、Regression stdout/stderr、Diagnostics 文本日志

未知 JSON/schema 不会让整批失败；会以警告记录进摘要，方便以后升级识别器。

## 当前仓库兼容入口

正常 owner 入口统一经过：

```text
parallel\EVIDENCE_INGESTOR\run.py
```

`run.py` 只负责当前仓库版本兼容，再复用 `ingestor.py` 核心整理逻辑。这样 Operator Toolkit 从 v1 升到当前 v2-cn 后，不会把正常 Regression / Diagnostics 误报成“未知版本”。

## 自动检查

对适用的结果类型检查：

- JSON 是否可解析
- schema/version/artifact 是否已登记
- 必要字段是否缺失
- `readOnly == true`
- `ramWrites == 0`
- `inputInjection == false`
- `World 921031` 是否确认
- 黄金 SHA-256 是否为：`5c369ce2de4f53d8cef87eca5623a1f0d39a779e885532d6f185b81357878f62`
- 文件内容 SHA-256 去重
- run / room / tool / date 分类

异常等级：

- `CRITICAL`：RAM 写入非 0、输入注入非 false、readOnly 非 true、World/SHA 身份不匹配
- `ERROR`：损坏 JSON、必要字段缺失、要求身份但缺失
- `WARNING`：未知 schema/version 或未知 JSON 结构
- `INFO`：重复文件等不阻断信息

`SUMMARY.json.overall`：

- `PASS`：没有 CRITICAL/ERROR/WARNING
- `ATTENTION`：有 ERROR/WARNING，但没有安全/身份 CRITICAL
- `FAIL`：存在安全或身份 CRITICAL

## 单个结果包

Toolkit 菜单 8 和双击 CMD 默认都会生成 ZIP。ZIP 包含：

- `SUMMARY.json`
- `结果汇总.txt`
- `PACKAGE_MANIFEST.json`
- `evidence/**` 下的唯一原始证据

相同内容只打包一次，重复路径记录在 manifest 中。原始目录不变。

## 命令行

当前仓库推荐：

```bat
python parallel\EVIDENCE_INGESTOR\run.py
python parallel\EVIDENCE_INGESTOR\run.py --package
python parallel\EVIDENCE_INGESTOR\run.py --root D:\Some\WOF_RESULTS --package
```

核心实现仍位于 `ingestor.py`。也支持 `WOF_RESULTS_DIR` 环境变量，Operator Toolkit 与独立入口因此使用同一个结果根目录。

## 离线回归

```bat
python -m unittest discover -s parallel\EVIDENCE_INGESTOR\tests -p test_*.py -v
```

基础实现已有 13 项 fixture 回归 PASS；当前仓库另外增加 3 项兼容回归，覆盖：

- Toolkit v2-cn Regression 不被误报未知版本；
- Toolkit v2-cn Diagnostics 不被误报未知版本；
- 一键 CMD 确认走 `run.py` 当前兼容入口。

## 最小 Windows proof

只需要一次真人 Windows 验证：

1. 保持现有 `%USERPROFILE%\Documents\WOF_RESULTS` 不动。
2. 双击 `WOF_TOOLKIT.cmd`，选择 `8`；或直接双击 `RUN_EVIDENCE_INGESTOR.cmd`。
3. 确认出现“WOF 自动结果整理完成”。
4. 打开 `_自动整理\<时间>\`，以后只需把 `SUMMARY.json` 或 ZIP 结果包交给 ChatGPT。

不需要 DevTools，不需要 Worker Console，不需要粘 JavaScript，也不需要进入游戏执行任何输入。
