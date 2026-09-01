from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MANIFEST = Path(__file__).resolve().parent / "package_manifest.json"

SCHEMA = "wof-owner-oneclick-package-v1"
GENERATOR = "parallel/OWNER_ONECLICK/refresh_manifest.py"
SELECTION_POLICY = "owner-oneclick-runtime-v2"
RUNTIME_SUFFIXES = {".py", ".js", ".mjs", ".cmd", ".bat", ".ps1"}
EXCLUDED_PARTS = {"tests", "__pycache__"}

FIXED_PATHS = {
    "WOF_一键工具.cmd",
    "WOF_TOOLKIT.cmd",
    "parallel/OPTOOLKIT/toolkit.py",
    "parallel/OPTOOLKIT/owner_zh_cn.py",
    "product/alpha/regression.mjs",
    "product/alpha/wof_alpha_core.js",
    "product/alpha/wof_alpha_hud_model.js",
    "product/alpha/wof_alpha_bootstrap.user.js",
    "product/alpha/wof_alpha_hud.js",
    "product/alpha/regression_result.json",
    "parallel/ALPHAQA_RC5/independent_bootstrap_retest.mjs",
}

PYLAUNCH_TOP = {
    "parallel/PYLAUNCH/RUN_WINDOWS_PROOF.cmd",
    "parallel/PYLAUNCH/RUN_WOF_LAUNCHER.bat",
    "parallel/PYLAUNCH/WOF_ONECLICK_PROOF_CN.cmd",
    "parallel/PYLAUNCH/launcher.py",
    "parallel/PYLAUNCH/requirements.txt",
}

LIVE_PROOF_TOP = {
    "parallel/LIVE_PROOF_BUNDLE/RUN_WOF_UNIFIED_LIVE_PROOF.cmd",
    "parallel/LIVE_PROOF_BUNDLE/unified_live_proof.py",
    "parallel/LIVE_PROOF_BUNDLE/unified_preflight.py",
    "parallel/LIVE_PROOF_BUNDLE/unified_preflight_entrypoint.py",
}

RUNTIME_ROOTS = (
    "parallel/WOF052L_RECORDER/",
    "parallel/BROWSER_FLEET/",
)


class ManifestError(RuntimeError):
    pass


def run_git(root: Path, *args: str) -> str:
    cp = subprocess.run(
        ["git", *args],
        cwd=root,
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if cp.returncode:
        raise ManifestError(cp.stderr.strip() or cp.stdout.strip() or "git command failed")
    return cp.stdout


def resolve_commit(root: Path, source: str) -> str:
    commit = run_git(root, "rev-parse", f"{source}^{{commit}}").strip().lower()
    if not re.fullmatch(r"[0-9a-f]{40}", commit):
        raise ManifestError(f"无法解析固定 source commit：{source}")
    return commit


def commit_generated_at_utc(root: Path, commit: str) -> str:
    raw = run_git(root, "show", "-s", "--format=%cI", commit).strip()
    try:
        dt = datetime.fromisoformat(raw.replace("Z", "+00:00")).astimezone(timezone.utc)
    except ValueError as exc:
        raise ManifestError(f"无法解析 source commit 时间：{raw}") from exc
    return dt.isoformat(timespec="seconds").replace("+00:00", "Z")


def package_version(commit: str, generated_at_utc: str) -> str:
    dt = datetime.fromisoformat(generated_at_utc.replace("Z", "+00:00"))
    return f"{dt:%Y.%m.%d}.{commit[:12]}"


def git_blob_sha(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def is_runtime_path(path: str) -> bool:
    p = Path(path)
    if any(part in EXCLUDED_PARTS for part in p.parts):
        return False
    if p.name.startswith("test_"):
        return False
    if path in FIXED_PATHS or path in PYLAUNCH_TOP or path in LIVE_PROOF_TOP:
        return True
    if path.startswith("parallel/PYLAUNCH/wof_launcher/"):
        return p.suffix.lower() == ".py"
    if path.startswith(RUNTIME_ROOTS):
        return p.suffix.lower() in RUNTIME_SUFFIXES or p.name == "requirements.txt"
    return False


def selected_paths_from_commit(root: Path, commit: str) -> dict[str, str]:
    out = run_git(root, "-c", "core.quotepath=false", "ls-tree", "-r", commit, "--", "WOF_一键工具.cmd", "WOF_TOOLKIT.cmd",
                  "parallel/OPTOOLKIT", "parallel/PYLAUNCH", "parallel/WOF052L_RECORDER",
                  "parallel/BROWSER_FLEET", "parallel/LIVE_PROOF_BUNDLE",
                  "product/alpha", "parallel/ALPHAQA_RC5")
    selected: dict[str, str] = {}
    for line in out.splitlines():
        if not line.strip():
            continue
        meta, path = line.split("\t", 1)
        _mode, obj_type, sha = meta.split()
        if obj_type == "blob" and is_runtime_path(path):
            selected[path] = sha.lower()

    missing = sorted((FIXED_PATHS | PYLAUNCH_TOP | LIVE_PROOF_TOP) - selected.keys())
    if missing:
        raise ManifestError("固定 package runtime 文件缺失：" + ", ".join(missing))
    return dict(sorted(selected.items()))


def selected_worktree_paths(root: Path) -> list[str]:
    candidates: set[str] = set(FIXED_PATHS | PYLAUNCH_TOP | LIVE_PROOF_TOP)

    py_pkg = root / "parallel" / "PYLAUNCH" / "wof_launcher"
    if py_pkg.is_dir():
        for p in py_pkg.glob("*.py"):
            candidates.add(p.relative_to(root).as_posix())

    for rel_root in ("parallel/WOF052L_RECORDER", "parallel/BROWSER_FLEET"):
        base = root / rel_root
        if not base.is_dir():
            continue
        for p in base.rglob("*"):
            if not p.is_file():
                continue
            rel = p.relative_to(root).as_posix()
            if is_runtime_path(rel):
                candidates.add(rel)

    return sorted(path for path in candidates if (root / path).is_file() and is_runtime_path(path))


def component_paths(paths: Iterable[str], prefix: str) -> list[str]:
    return [p for p in paths if p.startswith(prefix)]


def generate_manifest(root: Path, source: str) -> dict:
    commit = resolve_commit(root, source)
    generated_at = commit_generated_at_utc(root, commit)
    selected = selected_paths_from_commit(root, commit)
    paths = list(selected)

    return {
        "schema": SCHEMA,
        "packageVersion": package_version(commit, generated_at),
        "sourceCommit": commit,
        "generatedAtUtc": generated_at,
        "generator": GENERATOR,
        "selectionPolicy": SELECTION_POLICY,
        "baseUrl": f"https://raw.githubusercontent.com/ouyong520/wof-ai-private/{commit}/",
        "components": {
            "pylaunch": {
                "revision": "discovery-v2-current-snapshot",
                "sourceCommit": commit,
                "windowsProofEntry": "parallel/PYLAUNCH/RUN_WINDOWS_PROOF.cmd",
                "directProofEntry": "parallel/PYLAUNCH/WOF_ONECLICK_PROOF_CN.cmd",
                "files": component_paths(paths, "parallel/PYLAUNCH/"),
            },
            "recorder": {
                "sourceCommit": commit,
                "ownerEntry": "parallel/WOF052L_RECORDER/owner_zh_cn.py",
                "files": component_paths(paths, "parallel/WOF052L_RECORDER/"),
            },
            "browserFleet": {
                "sourceCommit": commit,
                "ownerEntry": "parallel/BROWSER_FLEET/fleet_owner_zh_cn.py",
                "files": component_paths(paths, "parallel/BROWSER_FLEET/"),
            },
            "liveProof": {
                "sourceCommit": commit,
                "entry": "parallel/LIVE_PROOF_BUNDLE/RUN_WOF_UNIFIED_LIVE_PROOF.cmd",
                "files": component_paths(paths, "parallel/LIVE_PROOF_BUNDLE/"),
            },
        },
        "safety": {
            "readOnly": True,
            "ramWrites": 0,
            "inputInjection": False,
        },
        "files": [{"path": path, "gitBlobSha": selected[path]} for path in paths],
    }


def verify_worktree_payload(root: Path, manifest: dict) -> None:
    expected = {str(row["path"]): str(row["gitBlobSha"]).lower() for row in manifest.get("files", [])}
    current_paths = selected_worktree_paths(root)
    current_set = set(current_paths)
    expected_runtime_set = {p for p in expected if is_runtime_path(p)}

    missing = sorted(current_set - expected_runtime_set)
    if missing:
        raise ManifestError("当前运行时文件未进入 package manifest：" + ", ".join(missing))

    stale_removed = sorted(expected_runtime_set - current_set)
    if stale_removed:
        raise ManifestError("package manifest 仍包含已移除运行时文件：" + ", ".join(stale_removed))

    for path in current_paths:
        data = (root / path).read_bytes()
        actual = git_blob_sha(data)
        wanted = expected[path]
        if actual != wanted:
            raise ManifestError(
                f"文件完整性校验失败：{path} expected={wanted} actual={actual}"
            )


def render_manifest(manifest: dict) -> str:
    return json.dumps(manifest, ensure_ascii=False, indent=2) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="从一个明确 immutable git commit 确定性生成 Owner One-Click package manifest"
    )
    parser.add_argument("--source", default="HEAD", help="固定 package source commit/ref；默认 HEAD")
    parser.add_argument("--output", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--check", action="store_true", help="只校验现有 manifest 与 source/worktree 一致")
    args = parser.parse_args(argv)

    try:
        generated = generate_manifest(ROOT, args.source)
        if args.check:
            try:
                existing = json.loads(args.output.read_text(encoding="utf-8-sig"))
            except Exception as exc:
                raise ManifestError(f"无法读取 package manifest：{args.output}") from exc
            if existing != generated:
                raise ManifestError(
                    "package manifest 不是当前所选 immutable snapshot 的确定性产物；请重新生成"
                )
            verify_worktree_payload(ROOT, existing)
            print(
                "PACKAGE MANIFEST PASS："
                f"{existing['packageVersion']} source={existing['sourceCommit']} files={len(existing['files'])}"
            )
            return 0

        args.output.write_text(render_manifest(generated), encoding="utf-8")
        verify_worktree_payload(ROOT, generated)
        print(
            "PACKAGE MANIFEST REFRESHED："
            f"{generated['packageVersion']} source={generated['sourceCommit']} files={len(generated['files'])}"
        )
        return 0
    except ManifestError as exc:
        print(f"PACKAGE MANIFEST BLOCKED：{exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
