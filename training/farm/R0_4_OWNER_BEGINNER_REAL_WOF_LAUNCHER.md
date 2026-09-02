# Training Farm R0.4 — Owner Beginner Real-WOF Launcher V1

Status: **OWNER UX ONLY — strict R0.2/R0.4 proof authority remains unchanged**

## 小白双击入口

Windows Owner 直接双击：

```text
training\farm\run_real_wof_proof_beginner.cmd
```

正常流程：

1. 如果系统已经设置 `WOF_ROM_PATH`，launcher 使用该外部路径，不弹选择框；
2. 否则弹出标准 ZIP 文件选择框；也可以把本地 WOF ZIP 直接拖到 `.cmd` 上；
3. launcher 在原位置读取 ZIP，只计算 size + SHA256，不复制、不解压；
4. 默认必须与 `training/farm/OWNER_LOCAL_ROM_REFERENCE.md` 当前记录同时匹配 size 与 SHA256；
5. 检查 Python、`stable-retro==0.9.8` 和 FBNeo capability；
6. 只在当前 child process 环境传入 `WOF_ROM_PATH`；
7. 调用既有严格 authority：

```text
python -m training.farm.real_wof_proof_owner_runner
```

8. 最终显示唯一主 verdict、证据目录和已产生的 JSON；Windows 交互终端可按 `O` 打开证据目录。

## ROM 身份保护

当前 Owner reference 只是一条仓库 metadata，不包含任何 ROM bytes。默认 beginner 流程不会因为文件名相同而接受 ZIP，必须同时匹配：

- size；
- SHA256。

不一致时 fail closed：

```text
WAITING_PREREQUISITE — 选择的 ZIP 与当前 Owner ROM 记录不一致，请重新选择正确文件
```

如果未来 Owner 合法持有另一份不同 ROM，需要专家显式从命令行使用：

```text
python -m training.farm.beginner_real_wof_launcher D:\ROM\other.zip --allow-unrecorded-rom
```

这个 override 只绕过 beginner 层的“当前 Owner metadata 是否匹配”检查；它**不会**绕过 strict runner 的 external ZIP、ROM SHA binding、R0.2/R0.4 real proof、source drift 或 `realWofProof=true` 规则。双击默认流程不带该参数。

## 依赖缺失

launcher 不自动安装依赖，也不下载 ROM、BIOS、专有 emulator/core binary 或游戏资源。

典型 `WAITING_PREREQUISITE`：

- Python 未安装，或不在当前 Farm 支持的 3.10..3.14；
- 缺少 `stable-retro==0.9.8`；
- Stable-Retro 版本不是精确 0.9.8；
- FBNeo capability probe 未通过；
- ZIP 未选择、不是外部绝对 `.zip`、不可读或与记录不匹配；
- strict runner 判定 evidence directory 不可用。

Python dependency 按当前 Farm pin 安装：

```text
training/farm/requirements-r0.1.txt
```

## 最终屏幕

主 verdict 只使用当前 strict runner contract：

```text
PASS — R0.2 REAL WOF DETERMINISM + R0.4 REAL FORK SMOKE
WAITING_PREREQUISITE — ...
BLOCKED — R0.2 REAL DETERMINISM — ...
BLOCKED — R0.4 REAL FORK SMOKE — ...
```

之后列出：

- `Evidence` 目录；
- `summary.txt`；
- `summary.json`；
- `r0_2_real_determinism.json`；
- `r0_4_real_fork_smoke.json`。

Owner 操作：

- PASS：告诉 PM `1`；
- WAITING/BLOCKED：发送 `summary.txt`；如果连 summary 都尚未生成，发送最终窗口截图。

## 安全 / authority 边界

本 V1 只新增 Owner onboarding/UX，不修改：

- `real_wof_proof_owner_runner.py`；
- R0.2 determinism consumer；
- R0.4 fork primitive/result validation；
- Farm runtime/fork source identity；
- source-drift guard；
- real proof scope / `realWofProof=true`；
- R0.5 / Reward / search / multi-worker / RL。

Mock/stub 只用于 implementation-owned launcher self-check，不能生成或升级为 real-WOF proof。

## Implementation self-check

```text
python -m unittest training.farm.tests.test_beginner_real_wof_launcher
```

覆盖：空格/中文/括号路径、picker cancel、wrong hash、matching hash、existing `WOF_ROM_PATH`、session-local child env、无 ROM copy、依赖提示、PASS/WAITING/BLOCKED 显示、missing reference fail-closed。
