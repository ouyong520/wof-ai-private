# Evidence Auto-Ingestor Result

Date: 2026-09-01
Status: **REPOSITORY READY**

## Implemented

- 独立 `parallel/EVIDENCE_INGESTOR/**`，Python 标准库实现，无新增 pip 依赖。
- 默认只读扫描 `%USERPROFILE%\Documents\WOF_RESULTS`。
- 识别 PYLAUNCH proof、WOF-052L room/merged/fleet、Browser Fleet status、Toolkit Regression/Diagnostics、RC5 regression/QA、日志文本。
- JSON 损坏隔离；单文件失败不会阻断整批。
- known schema/version/artifact 校验。
- `readOnly` / `ramWrites` / `inputInjection` 安全汇总。
- World 921031 + golden SHA-256 校验（仅在该证据类型具备身份职责时强制）。
- SHA-256 内容去重，不删除原始文件。
- run / room / tool / date 分类。
- 输出紧凑 `SUMMARY.json` 和中文 `结果汇总.txt`。
- 一键 ZIP 结果包；重复内容只打包一次。
- 自动排除 `_自动整理/**`，重复运行不会自吞输出。
- 所有正常用户可见 CLI/CMD 信息默认简体中文。
- 已接入当前简体中文 Operator Toolkit：根目录 `WOF_TOOLKIT.cmd` -> 菜单 `8` -> Evidence Auto-Ingestor。
- 当前 owner/Toolkit/独立 CMD 统一通过 `parallel/EVIDENCE_INGESTOR/run.py` 进入核心 `ingestor.py`。
- `run.py` 已兼容当前 `wof-windows-operator-toolkit-v2-cn`，并接受 `wof-windows-operator-toolkit-v*` 后续版本，避免正常 Regression/Diagnostics 被误报为未知版本。

## Safety boundary

- `product/alpha/**`: untouched
- PYLAUNCH Worker discovery: untouched
- WOF-052L collection logic: untouched
- game RAM writes: 0
- gameplay input injection: 0
- source evidence mutation/deletion: 0

## Automated tests

完整当前测试集已实际执行：

```text
python -m unittest discover -s parallel/EVIDENCE_INGESTOR/tests -p test_*.py -v
18/18 PASS
```

覆盖：

- valid PYLAUNCH + World 921031
- broken JSON isolation
- duplicate detection
- RAM write violation
- World SHA mismatch
- WOF-052L merged
- Browser Fleet
- unknown schema warning
- output self-exclusion
- ZIP package
- log indexing
- Alpha RC5 regression recognition
- Alpha RC5 QA recognition
- current Toolkit v2-cn Regression recognition
- current Toolkit v2-cn Diagnostics recognition
- current `run.py` compatibility path
- one-click CMD uses `run.py --package`

## Owner workflow

Preferred:

```text
双击 WOF_TOOLKIT.cmd
→ 8 自动整理并打包结果
→ Documents\WOF_RESULTS\_自动整理\<时间>\SUMMARY.json
```

Standalone fallback:

```text
parallel\EVIDENCE_INGESTOR\RUN_EVIDENCE_INGESTOR.cmd
```

每次成功整理同时得到：

```text
SUMMARY.json
结果汇总.txt
WOF_结果包_<时间>.zip
```

## Remaining real-Windows proof

Repository implementation has no blocker. The only platform-specific acceptance is one minimal double-click/menu-8 proof; it does not require DevTools, Worker Console, JavaScript paste, game RAM write, or game input.
