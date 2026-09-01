from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path
from typing import Callable

import unified_preflight

PREFLIGHT_BLOCKED_EXIT = 20


def run_guarded_live(
    root: Path,
    *,
    snapshot_manifest: Path | None = None,
    status_out: Path | None = None,
    regression_runner=unified_preflight._run_regression,
    live_runner: Callable[[], int] | None = None,
) -> tuple[int, dict]:
    status = unified_preflight.run_preflight(
        root,
        snapshot_manifest=snapshot_manifest,
        status_out=status_out,
        regression_runner=regression_runner,
    )
    if status["result"] != unified_preflight.PASS:
        return PREFLIGHT_BLOCKED_EXIT, status
    if live_runner is not None:
        return int(live_runner()), status
    live = root / "parallel" / "LIVE_PROOF_BUNDLE" / "unified_live_proof.py"
    rc = subprocess.call([sys.executable, str(live), "--project-root", str(root)])
    return int(rc), status


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="WOF 统一真人验证 fail-closed 入口")
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--snapshot-manifest")
    parser.add_argument("--preflight-status-out")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = Path(args.project_root).expanduser().resolve()
    manifest = Path(args.snapshot_manifest).expanduser().resolve() if args.snapshot_manifest else None
    status_out = Path(args.preflight_status_out).expanduser().resolve() if args.preflight_status_out else None
    rc, status = run_guarded_live(root, snapshot_manifest=manifest, status_out=status_out)
    if rc == PREFLIGHT_BLOCKED_EXIT:
        print("\n仓库侧预检未通过：Browser 未启动；Owner 不需要进入 WOF。")
        print("JSON：" + status["statusPath"])
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
