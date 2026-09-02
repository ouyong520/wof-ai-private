"""Windows beginner UX for the strict Training Farm R0.4 real-WOF Owner runner.

This module is deliberately outside the proof authority. It only selects and hashes
an external local ROM, explains prerequisites, and launches the existing strict
``training.farm.real_wof_proof_owner_runner`` in a child process. It never copies,
unpacks, vendors, or rewrites ROM bytes and never upgrades synthetic evidence.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Mapping, Sequence

from .stable_retro_backend import (
    PINNED_STABLE_RETRO,
    SUPPORTED_PYTHON_MAX,
    SUPPORTED_PYTHON_MIN,
    dependency_probe,
)

STRICT_RUNNER_MODULE = "training.farm.real_wof_proof_owner_runner"
ROM_REFERENCE_RELATIVE = Path("training/farm/OWNER_LOCAL_ROM_REFERENCE.md")
_SHA256 = re.compile(r"[0-9a-f]{64}\Z")
_REFERENCE_NAME = re.compile(r"^- uploaded/local filename observed by PM:\s*`([^`]+)`\s*$", re.MULTILINE)
_REFERENCE_SIZE = re.compile(r"^- size:\s*`?(\d+)`?\s*bytes\s*$", re.MULTILINE)
_REFERENCE_SHA = re.compile(r"^- SHA-256:\s*`?([0-9A-Fa-f]{64})`?\s*$", re.MULTILINE)
_EVIDENCE_LINE = re.compile(r"^Evidence:\s*(.+?)\s*$", re.MULTILINE)


class BeginnerLauncherError(RuntimeError):
    """Beginner-layer input/configuration error; never a proof verdict."""


@dataclass(frozen=True)
class RomReference:
    display_filename: str
    size_bytes: int
    sha256: str


@dataclass(frozen=True)
class RomSelection:
    path: Path
    size_bytes: int
    sha256: str
    source: str
    reference_matched: bool
    expert_override: bool


@dataclass(frozen=True)
class BeginnerOutcome:
    exit_code: int
    verdict: str
    detail: str
    evidence_directory: Path | None
    selected_rom: Path | None
    rom_reference_matched: bool | None
    files: dict[str, Path | None]


FileChooser = Callable[[], Path | None]
ProcessRunner = Callable[[Sequence[str], Path, dict[str, str]], subprocess.CompletedProcess[str]]
DependencyChecker = Callable[[Path], Mapping[str, object]]


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _is_within(child: Path, parent: Path) -> bool:
    try:
        child.resolve(strict=False).relative_to(parent.resolve(strict=False))
        return True
    except ValueError:
        return False


def _sha_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        while True:
            chunk = fh.read(1024 * 1024)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def load_owner_rom_reference(repo_root: Path | None = None) -> RomReference | None:
    root = repo_root or _repo_root()
    path = root / ROM_REFERENCE_RELATIVE
    if not path.is_file():
        return None
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise BeginnerLauncherError(
            f"无法读取 Owner ROM 记录 {path}: {type(exc).__name__}: {exc}"
        ) from exc
    name = _REFERENCE_NAME.search(text)
    size = _REFERENCE_SIZE.search(text)
    sha = _REFERENCE_SHA.search(text)
    if not (name and size and sha):
        raise BeginnerLauncherError(
            "OWNER_LOCAL_ROM_REFERENCE.md 缺少可解析的 filename / size / SHA-256 记录"
        )
    digest = sha.group(1).lower()
    if not _SHA256.fullmatch(digest):
        raise BeginnerLauncherError("Owner ROM SHA-256 记录格式无效")
    return RomReference(
        display_filename=name.group(1),
        size_bytes=int(size.group(1)),
        sha256=digest,
    )


def choose_rom_with_windows_picker() -> Path | None:
    """Open a standard Windows-style file picker; cancellation returns None."""
    try:
        import tkinter as tk
        from tkinter import filedialog

        root = tk.Tk()
        root.withdraw()
        try:
            root.attributes("-topmost", True)
        except Exception:
            pass
        selected = filedialog.askopenfilename(
            title="选择本地 WOF ZIP / Select local WOF ZIP",
            filetypes=(("WOF / ZIP", "*.zip"), ("ZIP", "*.zip")),
        )
        root.destroy()
    except Exception as exc:
        raise BeginnerLauncherError(
            "无法打开 Windows 文件选择器。可把 WOF ZIP 直接拖到 "
            "run_real_wof_proof_beginner.cmd 上重试；"
            f"picker={type(exc).__name__}: {exc}"
        ) from exc
    return Path(selected) if selected else None


def validate_selected_rom(
    raw_path: str | os.PathLike[str],
    *,
    repo_root: Path,
    reference: RomReference | None,
    source: str,
    allow_unrecorded_rom: bool,
) -> RomSelection:
    path = Path(raw_path).expanduser()
    if not path.is_absolute():
        raise BeginnerLauncherError("选择的 WOF ZIP 必须是绝对路径")
    path = path.resolve(strict=False)
    if _is_within(path, repo_root):
        raise BeginnerLauncherError("WOF ZIP 必须保留在仓库目录之外，不能放进 Git 仓库")
    if not path.is_file():
        raise BeginnerLauncherError("选择的 WOF ZIP 不存在或不是普通文件")
    if path.suffix.lower() != ".zip":
        raise BeginnerLauncherError("请选择 .zip 文件；当前 Training Farm FBNeo 路径只接受外部 ZIP romset")
    try:
        size = path.stat().st_size
        digest = _sha_file(path)
    except OSError as exc:
        raise BeginnerLauncherError(
            f"选择的 ZIP 无法读取/计算 SHA256: {type(exc).__name__}: {exc}"
        ) from exc
    if not _SHA256.fullmatch(digest):
        raise BeginnerLauncherError("本地 ZIP SHA256 计算结果格式无效")

    if reference is None:
        if not allow_unrecorded_rom:
            raise BeginnerLauncherError(
                "仓库当前没有有效的 Owner ROM size/SHA256 记录；默认双击流程不会绕过身份核对"
            )
        matched = False
    else:
        matched = size == reference.size_bytes and digest == reference.sha256
        if not matched and not allow_unrecorded_rom:
            raise BeginnerLauncherError(
                "选择的 ZIP 与当前 Owner ROM 记录不一致，请重新选择正确文件；"
                f"observed size={size}, sha256={digest}"
            )

    return RomSelection(
        path=path,
        size_bytes=size,
        sha256=digest,
        source=source,
        reference_matched=matched,
        expert_override=bool(allow_unrecorded_rom and not matched),
    )


def dependency_wait_reason(report: Mapping[str, object]) -> str | None:
    py = sys.version_info[:2]
    if not (SUPPORTED_PYTHON_MIN <= py <= SUPPORTED_PYTHON_MAX):
        return (
            f"Python {platform.python_version()} 不受支持；需要 "
            f"{SUPPORTED_PYTHON_MIN[0]}.{SUPPORTED_PYTHON_MIN[1]}.."
            f"{SUPPORTED_PYTHON_MAX[0]}.{SUPPORTED_PYTHON_MAX[1]}"
        )
    if report.get("platform_supported") is not True:
        return "当前系统不受 Training Farm FBNeo proof runner 支持；需要 Windows 或 Linux"
    if report.get("stable_retro_present") is not True:
        return (
            f"缺少 stable-retro=={PINNED_STABLE_RETRO}。请按 "
            "training/farm/requirements-r0.1.txt 安装；本 launcher 不会自动下载 ROM/BIOS"
        )
    if report.get("stable_retro_version") != PINNED_STABLE_RETRO:
        return (
            f"stable-retro 版本不正确：检测到 {report.get('stable_retro_version')!r}，"
            f"严格要求 {PINNED_STABLE_RETRO}"
        )
    if report.get("fbneo_declared") is not True or report.get("fbneo_zip_mapping") is not True:
        return "Stable-Retro 的 FBNeo capability probe 未通过；请先修复本机 FBNeo 运行环境"
    if report.get("runtime_ready") is not True:
        return str(report.get("detail") or "Stable-Retro/FBNeo runtime 尚未就绪")
    return None


def _default_dependency_checker(path: Path) -> Mapping[str, object]:
    return dependency_probe(str(path)).to_dict()


def _default_process_runner(
    cmd: Sequence[str], cwd: Path, env: dict[str, str]
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        list(cmd),
        cwd=str(cwd),
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )


def launch_strict_owner_runner(
    selection: RomSelection,
    *,
    repo_root: Path,
    evidence_root: Path | None,
    process_runner: ProcessRunner,
    base_environment: Mapping[str, str],
) -> subprocess.CompletedProcess[str]:
    env = dict(base_environment)
    # Session-local only. The parent/global environment is never mutated.
    env["WOF_ROM_PATH"] = str(selection.path)
    cmd: list[str] = [sys.executable, "-m", STRICT_RUNNER_MODULE]
    if evidence_root is not None:
        cmd.extend(("--evidence-root", str(evidence_root)))
    return process_runner(cmd, repo_root, env)


def _extract_evidence_directory(stdout: str) -> Path | None:
    match = _EVIDENCE_LINE.search(stdout or "")
    if not match:
        return None
    return Path(match.group(1).strip())


def _read_summary(evidence_directory: Path | None) -> dict[str, object] | None:
    if evidence_directory is None:
        return None
    path = evidence_directory / "summary.json"
    if not path.is_file():
        return None
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return None
    return value if type(value) is dict else None


def _summary_verdict(summary: Mapping[str, object]) -> str:
    state = summary.get("state")
    detail = str(summary.get("detail", ""))
    if state == "PASS":
        return "PASS — R0.2 REAL WOF DETERMINISM + R0.4 REAL FORK SMOKE"
    if state == "WAITING_PREREQUISITE":
        return f"WAITING_PREREQUISITE — {detail}"
    if state == "BLOCKED_R0_2_REAL_DETERMINISM":
        return f"BLOCKED — R0.2 REAL DETERMINISM — {detail}"
    if state == "BLOCKED_R0_4_REAL_FORK_SMOKE":
        return f"BLOCKED — R0.4 REAL FORK SMOKE — {detail}"
    return f"BLOCKED — OWNER RUNNER — {detail or 'unknown strict-runner state'}"


def _stdout_verdict(stdout: str) -> str | None:
    for line in (stdout or "").splitlines():
        stripped = line.strip()
        if stripped.startswith(("PASS —", "WAITING_PREREQUISITE —", "BLOCKED —")):
            return stripped
    return None


def _files_for(evidence: Path | None) -> dict[str, Path | None]:
    names = {
        "summary.txt": "summary.txt",
        "summary.json": "summary.json",
        "R0.2 JSON": "r0_2_real_determinism.json",
        "R0.4 JSON": "r0_4_real_fork_smoke.json",
    }
    result: dict[str, Path | None] = {}
    for label, name in names.items():
        candidate = evidence / name if evidence is not None else None
        result[label] = candidate if candidate is not None and candidate.is_file() else None
    return result


def _waiting(detail: str, selected_rom: Path | None = None, matched: bool | None = None) -> BeginnerOutcome:
    return BeginnerOutcome(
        exit_code=2,
        verdict=f"WAITING_PREREQUISITE — {detail}",
        detail=detail,
        evidence_directory=None,
        selected_rom=selected_rom,
        rom_reference_matched=matched,
        files=_files_for(None),
    )


def run_beginner_flow(
    *,
    rom_argument: str | None = None,
    evidence_root: Path | None = None,
    allow_unrecorded_rom: bool = False,
    chooser: FileChooser | None = None,
    process_runner: ProcessRunner | None = None,
    dependency_checker: DependencyChecker | None = None,
    repo_root: Path | None = None,
    environment: Mapping[str, str] | None = None,
) -> BeginnerOutcome:
    root = (repo_root or _repo_root()).resolve(strict=False)
    env = dict(os.environ if environment is None else environment)
    chooser_fn = chooser or choose_rom_with_windows_picker
    process_fn = process_runner or _default_process_runner
    dependency_fn = dependency_checker or _default_dependency_checker

    source: str
    selected_raw: str | os.PathLike[str] | None
    if rom_argument:
        selected_raw = rom_argument
        source = "drag-drop/CLI"
    elif env.get("WOF_ROM_PATH"):
        selected_raw = env["WOF_ROM_PATH"]
        source = "existing WOF_ROM_PATH"
    else:
        try:
            selected = chooser_fn()
        except BeginnerLauncherError as exc:
            return _waiting(str(exc))
        except Exception as exc:
            return _waiting(f"文件选择器失败：{type(exc).__name__}: {exc}")
        if selected is None:
            return _waiting("未选择 WOF ZIP；请重新双击并选择本地合法持有的 .zip")
        selected_raw = selected
        source = "Windows file picker"

    try:
        reference = load_owner_rom_reference(root)
        selection = validate_selected_rom(
            selected_raw,
            repo_root=root,
            reference=reference,
            source=source,
            allow_unrecorded_rom=allow_unrecorded_rom,
        )
    except BeginnerLauncherError as exc:
        return _waiting(str(exc), Path(selected_raw) if selected_raw is not None else None, False)

    try:
        report = dependency_fn(selection.path)
    except Exception as exc:
        return _waiting(
            f"依赖预检失败：{type(exc).__name__}: {exc}",
            selection.path,
            selection.reference_matched,
        )
    dependency_reason = dependency_wait_reason(report)
    if dependency_reason:
        return _waiting(dependency_reason, selection.path, selection.reference_matched)

    try:
        cp = launch_strict_owner_runner(
            selection,
            repo_root=root,
            evidence_root=evidence_root,
            process_runner=process_fn,
            base_environment=env,
        )
    except OSError as exc:
        return BeginnerOutcome(
            exit_code=5,
            verdict=f"BLOCKED — OWNER RUNNER — 无法启动严格 proof runner: {type(exc).__name__}: {exc}",
            detail=str(exc),
            evidence_directory=None,
            selected_rom=selection.path,
            rom_reference_matched=selection.reference_matched,
            files=_files_for(None),
        )

    evidence = _extract_evidence_directory(cp.stdout or "")
    summary = _read_summary(evidence)
    verdict = _summary_verdict(summary) if summary is not None else _stdout_verdict(cp.stdout or "")
    if verdict is None:
        diagnostic = (cp.stderr or cp.stdout or "no output").strip().replace("\n", " ")[:800]
        verdict = f"BLOCKED — OWNER RUNNER — strict runner exit={cp.returncode}; {diagnostic}"
        exit_code = 5
    else:
        exit_code = cp.returncode
        if verdict.startswith("PASS —") and (cp.returncode != 0 or summary is None):
            verdict = "BLOCKED — OWNER RUNNER — PASS 输出缺少有效 summary.json 或退出码非 0"
            exit_code = 5

    return BeginnerOutcome(
        exit_code=exit_code,
        verdict=verdict,
        detail=str(summary.get("detail", "")) if summary is not None else verdict,
        evidence_directory=evidence,
        selected_rom=selection.path,
        rom_reference_matched=selection.reference_matched,
        files=_files_for(evidence),
    )


def print_final_screen(outcome: BeginnerOutcome) -> None:
    print()
    print("=" * 72)
    print("Training Farm R0.4 小白实机证明 / Beginner Real-WOF Proof")
    print("=" * 72)
    print(outcome.verdict)
    if outcome.selected_rom is not None:
        print(f"本地 ZIP / Local ZIP: {outcome.selected_rom}")
    if outcome.rom_reference_matched is True:
        print("ROM 身份核对: MATCH — size + SHA256 与 OWNER_LOCAL_ROM_REFERENCE.md 一致")
    elif outcome.rom_reference_matched is False and outcome.selected_rom is not None:
        print("ROM 身份核对: NOT MATCHED / NOT AVAILABLE")
    print(
        "证据目录 / Evidence: "
        + (str(outcome.evidence_directory) if outcome.evidence_directory else "尚未创建 / not created")
    )
    for label, path in outcome.files.items():
        print(f"{label}: {path if path is not None else 'not produced'}")
    if outcome.verdict.startswith("PASS —"):
        print("下一步 / Next: PASS => 告诉 PM：1")
    else:
        print("下一步 / Next: WAITING/BLOCKED => 发送 summary.txt；若未生成则发送本窗口截图")
    print("说明: 本 launcher 不复制/解压 ROM，不改变 R0.2/R0.4 实机证明判定。")


def maybe_offer_open_evidence(outcome: BeginnerOutcome) -> None:
    if os.name != "nt" or outcome.evidence_directory is None or not sys.stdin.isatty():
        return
    try:
        choice = input("输入 O 后回车打开证据文件夹；直接回车跳过 / O=open: ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        return
    if choice == "o":
        try:
            os.startfile(str(outcome.evidence_directory))  # type: ignore[attr-defined]
        except OSError as exc:
            print(f"无法打开证据目录 / Cannot open folder: {exc}")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Windows beginner launcher for the strict R0.2 + R0.4 real-WOF Owner proof"
    )
    ap.add_argument(
        "rom",
        nargs="?",
        help="optional external WOF .zip, including drag/drop path; otherwise uses WOF_ROM_PATH or picker",
    )
    ap.add_argument("--evidence-root", help="optional external evidence root passed unchanged to strict runner")
    ap.add_argument(
        "--allow-unrecorded-rom",
        action="store_true",
        help="EXPERT ONLY: allow an external legal ZIP whose size/SHA differs from the recorded Owner reference",
    )
    ap.add_argument(
        "--no-open-folder-prompt",
        action="store_true",
        help="skip the optional Windows evidence-folder prompt",
    )
    args = ap.parse_args(argv)
    outcome = run_beginner_flow(
        rom_argument=args.rom,
        evidence_root=Path(args.evidence_root) if args.evidence_root else None,
        allow_unrecorded_rom=args.allow_unrecorded_rom,
    )
    print_final_screen(outcome)
    if not args.no_open_folder_prompt:
        maybe_offer_open_evidence(outcome)
    return outcome.exit_code


if __name__ == "__main__":
    raise SystemExit(main())
