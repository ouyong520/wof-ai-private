# Training Farm R0.4.6 — Windows 一键环境准备

这是 **R0.2/R0.4 真实 WOF proof 的环境准备层**，不是 proof 本身，也不是 R0.5。

## 正常使用：只双击一个文件

从 GitHub 下载/解压仓库后，双击：

```text
training\farm\run_windows_oneclick_env_bootstrap.cmd
```

正常流程不要求你手动设置环境变量、找 Python 路径或输入长命令。

一键流程会：

1. 从脚本自身位置确定仓库根目录，支持中文、空格和括号路径；
2. 优先发现当前 Training Farm 支持的 Python（仓库 authority 当前是 3.10..3.14），不会因为默认 `python` 恰好是不支持版本就放弃；
3. 在本地工作根创建/复用专用 `.venv`，不修改全局 Python 包；
4. 只按仓库 `training/farm/requirements-r0.1.txt` 同步依赖，并与 `stable_retro_backend.py` 的 Stable-Retro pin 做一致性检查；
5. 在 **不读取 ROM** 的依赖探测阶段验证 Stable-Retro 版本与 FBNeo capability/ZIP mapping；
6. 创建本地 evidence/log/runtime 等目录；
7. 环境就绪后，用专用 `.venv` Python 启动现有 `training.farm.beginner_real_wof_launcher`；
8. 原有 Windows 文件选择器出现后，选择仓库外合法持有的 WOF `.zip`；
9. 原有 strict Owner runner 继续执行当前源码 R0.2 determinism -> R0.4 fork smoke，并显示真实 evidence 目录。

`READY_FOR_OWNER_PROOF` 只表示环境已准备好。只有现有 strict runner 自己产生的

```text
PASS — R0.2 REAL WOF DETERMINISM + R0.4 REAL FORK SMOKE
```

才是实机证明；bootstrap/fixture/diagnostics 的 PASS 永远不是 real-WOF proof。

## 推荐本地布局

Owner 当前机器可以使用下面的布局，但代码没有硬编码 `F:`：

```text
F:\三国\三国10训\
├─ wof-ai-private-main\      # 解压后的仓库源码
├─ .venv\                    # bootstrap 专用 Python 环境
├─ ROM\                      # 仅目录；bootstrap 不会复制/移动 ROM
├─ evidence\
├─ logs\
├─ runtime\
├─ training-data\
└─ checkpoints\
```

默认 local root 是**仓库目录的父目录**。因此把 `wof-ai-private-main` 放在上面的目录后，直接双击即可得到该布局。也可从命令行用 `--local-root` / `--evidence-root` 指定其他位置。

## Python 缺失时

如果没有任何受支持的 Python，窗口会明确显示：

```text
WAITING_PREREQUISITE — 未找到受支持 Python
```

安装任意一个 Python 3.10..3.14 后重新双击即可。流程不会卸载现有 Python，也不会静默下载/安装 Python。

如果已有专用 `.venv`，但它损坏或版本已超出当前支持范围，bootstrap 会 fail-closed，要求先手动重命名/删除这个**专用** `.venv`；不会静默覆盖未知环境。

## 依赖与 FBNeo

依赖 authority 只来自当前仓库：

- `training/farm/requirements-r0.1.txt`
- `training/farm/stable_retro_backend.py`

当前两处要求 `stable-retro==0.9.8`。如果未来源码 authority 改变，bootstrap 读取当前源码而不是把 `0.9.8` 当成第二套固定 authority。

安装失败会区分：

- 网络/包索引不可用 -> `WAITING_PREREQUISITE`;
- wheel/build 失败 -> precise `BLOCKED`;
- requirement 与 backend pin 不一致 -> `BLOCKED`;
- 安装后版本不精确匹配 -> `BLOCKED`;
- FBNeo capability/ZIP mapping 不通过 -> `BLOCKED`.

不会为了通过本机环境而修改 pin。

## ROM 与 evidence 安全边界

bootstrap 不会下载、复制、移动、解压、上传、提交、base64、加密或拆分 ROM/BIOS/game assets。`ROM\` 只是可选空目录。真实 ROM 仍由现有 beginner launcher 的 picker 选择，并继续执行原有 size/SHA256 与仓库外路径规则。

默认 evidence 是 `<local-root>\evidence`，必须位于仓库外。bootstrap 只创建目录并把路径传给现有 strict runner，不会重写 `summary.json`、补造 proof 文件或改变 proof verdict。

现有真实输出仍是：

- `summary.txt`
- `summary.json`
- `r0_2_real_determinism.json`
- `r0_4_real_fork_smoke.json`

`WOF_ROM_PATH` 不写入 Registry/System/全局环境；现有 launcher 仍只在自己的 child/session 环境里传给 strict runner。

## ROM-free diagnostics

实现/排障可运行：

```text
python -m training.farm.windows_oneclick_bootstrap --diagnostics-json
```

该模式不创建 venv、不执行 pip、不启动 proof、不打开 ROM，不读取 `WOF_ROM_PATH` 指向的文件；即使父 shell 有该变量，依赖 probe 子进程也会移除它。JSON 明确包含：

```text
realWofProof=false
r0_5Authorized=false
realWorkerExecutionStarted=false
romAccessed=false
```

可用 `--prepare-only` 只完成环境准备并停在 `READY_FOR_OWNER_PROOF`，不会弹 ROM picker。

## 仍然锁住的门

R0.4.6 不改变任何 R0.2/R0.4 证明语义。R0.5 仍然必须等待：

1. current-source **R0.2 real WOF determinism PASS**；
2. current-source **R0.4 real fork PASS**；
3. 另一个明确 PM authorization。

本模块不会启动 2+ WOF workers，不包含 Reward/Search/RL，不猜 WOF RAM 地址，也不做 host keyboard/mouse/focus automation。
