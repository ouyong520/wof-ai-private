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
PIN_PATH = "parallel/OWNER_ONECLICK/visible_overlay_runtime_pin.json"
DEFAULT_PIN = ROOT / PIN_PATH

SCHEMA = "wof-owner-oneclick-package-v1"
GENERATOR = "parallel/OWNER_ONECLICK/refresh_manifest.py"
SELECTION_POLICY = "owner-oneclick-runtime-v8-visible-production-top-overlay-slice-a-pinned"
RUNTIME_SUFFIXES = {".py", ".js", ".mjs", ".cmd", ".bat", ".ps1", ".json"}
EXCLUDED_PARTS = {"tests", "__pycache__"}

FIXED_PATHS = {
    "WOF_一键工具.cmd",
    "WOF_TOOLKIT.cmd",
    "parallel/OWNER_ONECLICK/bootstrap_v2.ps1",
    PIN_PATH,
    "parallel/OPTOOLKIT/toolkit.py",
    "parallel/OPTOOLKIT/owner_zh_cn.py",
    "parallel/OPTOOLKIT/live_session.py",
    "parallel/HUDANCHOR_PROOF/wof_hudanchor_gl.js",
    "parallel/HUDANCHOR_PROOF/wof_owner_projection_worker.js",
    "parallel/HUDANCHOR_PROOF/wof_owner_projection_top.js",
    "product/alpha/regression.mjs",
    "product/alpha/wof_alpha_core.js",
    "product/alpha/wof_alpha_hud_model.js",
    "product/alpha/wof_alpha_bootstrap.user.js",
    "product/alpha/wof_alpha_loader.js",
    "product/alpha/wof_alpha_real_worker.js",
    "product/alpha/wof_alpha_field_adapter.js",
    "product/alpha/wof_alpha_enemy_target_labels.js",
    "product/alpha/wof_alpha_player_head_warning.js",
    "product/alpha/wof_alpha_hud.js",
    "product/alpha/wof_alpha_enemy_head_projection.json",
    "product/alpha/wof_alpha_player_head_projection.json",
    "product/alpha/regression_result.json",
    "parallel/ALPHAQA_RC5/independent_bootstrap_retest.mjs",
}

PYLAUNCH_TOP = {
    "parallel/PYLAUNCH/RUN_WINDOWS_PROOF.cmd",
    "parallel/PYLAUNCH/RUN_WOF_LAUNCHER.bat",
    "parallel/PYLAUNCH/WOF_ONECLICK_PROOF_CN.cmd",
    "parallel/PYLAUNCH/launcher.py",
    "parallel/PYLAUNCH/render_authority_measurement_entry.py",
    "parallel/PYLAUNCH/requirements.txt",
}

LIVE_PROOF_TOP = {
    "parallel/LIVE_PROOF_BUNDLE/RUN_WOF_UNIFIED_LIVE_PROOF.cmd",
    "parallel/LIVE_PROOF_BUNDLE/unified_live_proof.py",
    "parallel/LIVE_PROOF_BUNDLE/unified_preflight.py",
    "parallel/LIVE_PROOF_BUNDLE/unified_preflight_entrypoint.py",
}

RENDER_AUTHORITY_V3_PATHS = {
    "parallel/RENDER_AUTHORITY_V2/wof_render_authority_capture_worker.js",
    "parallel/RENDER_AUTHORITY_V3/measurement_runner.py",
}

RUNTIME_ROOTS = (
    "parallel/WOF052L_RECORDER/",
    "parallel/BROWSER_FLEET/",
)

# A Slice A pin is a complete runtime snapshot, not merely the files touched by
# the final commit. These are the authority -> tracker -> maintained HUD pieces
# that must remain byte-identical between the Slice A handoff and final package.
SLICE_A_RUNTIME_PATHS = (
    "parallel/RENDER_AUTHORITY_V3/measurement_runner.py",
    "parallel/PYLAUNCH/wof_launcher/render_authority_capture.py",
    "parallel/PYLAUNCH/wof_launcher/semantic_evidence_producer.py",
    "parallel/PYLAUNCH/wof_launcher/zero_click_identity_acquisition.py",
    "parallel/PYLAUNCH/wof_launcher/head_visual_tracker.py",
    "parallel/PYLAUNCH/wof_launcher/production_p1_overlay.py",
    "product/alpha/wof_alpha_hud_model.js",
    "product/alpha/wof_alpha_enemy_target_labels.js",
    "product/alpha/wof_alpha_player_head_warning.js",
    "product/alpha/wof_alpha_hud.js",
)

PRODUCTION_OVERLAY_SOURCE = "product/alpha/wof_alpha_hud.js"
REMOVED_FORKED_OVERLAY_SOURCE = "product/alpha/wof_alpha_p1_tracker_overlay.js"


class ManifestError(RuntimeError):
    pass


def run_git(root: Path, *args: str) -> str:
    cp = subprocess.run(
        ["git", *args], cwd=root, text=True, encoding="utf-8", errors="replace",
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False,
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
    if path in FIXED_PATHS or path in PYLAUNCH_TOP or path in LIVE_PROOF_TOP or path in RENDER_AUTHORITY_V3_PATHS:
        return True
    if path.startswith("parallel/PYLAUNCH/wof_launcher/"):
        return p.suffix.lower() == ".py"
    if path.startswith(RUNTIME_ROOTS):
        return p.suffix.lower() in RUNTIME_SUFFIXES or p.name == "requirements.txt"
    return False


def selected_paths_from_commit(root: Path, commit: str) -> dict[str, str]:
    out = run_git(
        root, "-c", "core.quotepath=false", "ls-tree", "-r", commit, "--",
        "WOF_一键工具.cmd", "WOF_TOOLKIT.cmd", "parallel/OWNER_ONECLICK", "parallel/OPTOOLKIT",
        "parallel/PYLAUNCH", "parallel/RENDER_AUTHORITY_V2", "parallel/RENDER_AUTHORITY_V3",
        "parallel/WOF052L_RECORDER", "parallel/BROWSER_FLEET", "parallel/LIVE_PROOF_BUNDLE",
        "parallel/HUDANCHOR_PROOF", "product/alpha", "parallel/ALPHAQA_RC5",
    )
    selected: dict[str, str] = {}
    for line in out.splitlines():
        if not line.strip():
            continue
        meta, path = line.split("\t", 1)
        _mode, obj_type, sha = meta.split()
        if obj_type == "blob" and is_runtime_path(path):
            selected[path] = sha.lower()
    missing = sorted((FIXED_PATHS | PYLAUNCH_TOP | LIVE_PROOF_TOP | RENDER_AUTHORITY_V3_PATHS) - selected.keys())
    if missing:
        raise ManifestError("固定 package runtime 文件缺失：" + ", ".join(missing))
    return dict(sorted(selected.items()))


def selected_worktree_paths(root: Path) -> list[str]:
    candidates: set[str] = set(FIXED_PATHS | PYLAUNCH_TOP | LIVE_PROOF_TOP | RENDER_AUTHORITY_V3_PATHS)
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


def _git_file_text(root: Path, commit: str, path: str) -> str:
    return run_git(root, "show", f"{commit}:{path}")


def _blob_at(root: Path, commit: str, path: str) -> str:
    out = run_git(root, "-c", "core.quotepath=false", "ls-tree", commit, "--", path).strip()
    if not out:
        raise ManifestError(f"固定 commit 缺少 runtime 文件：{path}")
    meta, actual_path = out.split("\t", 1)
    _mode, obj_type, sha = meta.split()
    if obj_type != "blob" or actual_path != path:
        raise ManifestError(f"固定 runtime 不是普通文件：{path}")
    return sha.lower()


def _read_pin_file(root: Path) -> dict | None:
    path = root / PIN_PATH
    try:
        value = json.loads(path.read_text(encoding="utf-8-sig"))
    except FileNotFoundError:
        return None
    except Exception as exc:
        raise ManifestError(f"无法读取 Slice A pin：{path}") from exc
    return value if isinstance(value, dict) else None


def resolve_slice_a_pin(root: Path, explicit: str | None) -> tuple[str, dict]:
    pin = _read_pin_file(root)
    candidate = explicit or (str(pin.get("sliceARuntimeCommit")) if pin and pin.get("sliceARuntimeCommit") else None)
    if not candidate:
        raise ManifestError("Slice A exact commit 尚未提供；拒绝生成 production package manifest")
    commit = resolve_commit(root, candidate)
    if pin is not None:
        if pin.get("schema") != "alpha-v1-visible-top-overlay-slice-a-pin-v1":
            raise ManifestError("Slice A pin schema 不匹配")
        if str(pin.get("sliceARuntimeCommit") or "").lower() != commit:
            raise ManifestError("显式 Slice A commit 与 durable pin 文件不一致")
        if pin.get("normalPath") != "production-top-overlay":
            raise ManifestError("Slice A pin normalPath 不是 production-top-overlay")
        if pin.get("productionOverlaySource") != PRODUCTION_OVERLAY_SOURCE:
            raise ManifestError("Slice A pin 未选择 maintained Alpha HUD")
        if pin.get("productionOverlayEnabled") is not True or pin.get("productionOverlaySuppressed") is not False:
            raise ManifestError("Slice A pin overlay enable/suppress contract 不满足")
    return commit, pin or {"sliceARuntimeCommit": commit}


def validate_visible_overlay_text(text: str) -> None:
    enabled_true = re.search(r"['\"]productionOverlayEnabled['\"]\s*:\s*True\b", text)
    enabled_false = re.search(r"['\"]productionOverlayEnabled['\"]\s*:\s*False\b", text)
    suppressed_false = re.search(r"['\"]productionOverlaySuppressed['\"]\s*:\s*False\b", text)
    suppressed_true = re.search(r"['\"]productionOverlaySuppressed['\"]\s*:\s*True\b", text)
    if not enabled_true or enabled_false:
        raise ManifestError("selected normal runtime 未证明 productionOverlayEnabled=true")
    if not suppressed_false or suppressed_true:
        raise ManifestError("selected normal runtime 未证明 productionOverlaySuppressed=false")
    for key in ("manualCalibration", "legacyProjectionSelected"):
        if not re.search(rf"['\"]{key}['\"]\s*:\s*False\b", text):
            raise ManifestError(f"selected runtime 未保持 {key}=false")
    if PRODUCTION_OVERLAY_SOURCE not in text:
        raise ManifestError("selected runtime 未选择 maintained Alpha HUD production source")
    if REMOVED_FORKED_OVERLAY_SOURCE in text:
        raise ManifestError("selected runtime 仍引用已移除 forked P1 overlay")


def validate_overlay_adapter_text(text: str) -> None:
    required = [
        'SOURCE = "product/alpha/wof_alpha_hud.js"',
        "window.WOFALPHAHUD",
        "bindP1HeadTrackerAuthority",
        "setP1HeadTracker",
        "clearP1HeadTrackerAuthority",
        '"productionOverlayEnabled": True',
        '"readOnly": True',
        '"ramWrites": 0',
        '"inputInjection": False',
    ]
    missing = [token for token in required if token not in text]
    if missing:
        raise ManifestError("production overlay adapter contract 缺失：" + ", ".join(missing))
    if REMOVED_FORKED_OVERLAY_SOURCE in text:
        raise ManifestError("production overlay adapter 仍引用已移除 forked HUD")


def validate_slice_a_pin(root: Path, source_commit: str, slice_a_source: str | None) -> dict:
    slice_a, pin_meta = resolve_slice_a_pin(root, slice_a_source)
    cp = subprocess.run(
        ["git", "merge-base", "--is-ancestor", slice_a, source_commit], cwd=root,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False,
    )
    if cp.returncode != 0:
        raise ManifestError("Slice A exact commit 不是 package source 的 ancestor，拒绝 pin")
    rows = []
    for path in SLICE_A_RUNTIME_PATHS:
        slice_blob = _blob_at(root, slice_a, path)
        source_blob = _blob_at(root, source_commit, path)
        if source_blob != slice_blob:
            raise ManifestError(f"Slice A runtime 在 package source 中已漂移：{path}")
        rows.append({"path": path, "gitBlobSha": slice_blob})
    validate_visible_overlay_text(_git_file_text(root, source_commit, "parallel/RENDER_AUTHORITY_V3/measurement_runner.py"))
    validate_overlay_adapter_text(_git_file_text(root, source_commit, "parallel/PYLAUNCH/wof_launcher/production_p1_overlay.py"))
    return {"commit": slice_a, "files": rows, "pin": pin_meta}


def verify_publishable_manifest(manifest: dict) -> None:
    components = manifest.get("components")
    render = components.get("renderAuthorityV3") if isinstance(components, dict) else None
    if not isinstance(render, dict):
        raise ManifestError("manifest 未选择 renderAuthorityV3 production runtime")
    source = str(manifest.get("sourceCommit") or "")
    slice_a = str(render.get("sliceARuntimeCommit") or "")
    checks = [
        (re.fullmatch(r"[0-9a-f]{40}", source) is not None, "sourceCommit 未固定"),
        (re.fullmatch(r"[0-9a-f]{40}", slice_a) is not None, "Slice A exact commit 未固定"),
        (render.get("selectedNormalPath") == "production-top-overlay", "normal path 不是 production top overlay"),
        (render.get("productionOverlaySource") == PRODUCTION_OVERLAY_SOURCE, "production overlay source 不是 maintained Alpha HUD"),
        (render.get("productionOverlayEnabled") is True, "productionOverlayEnabled 必须为 true"),
        (render.get("productionOverlaySuppressed") is False, "productionOverlaySuppressed 必须为 false"),
        (render.get("diagnosticOnly") is False, "diagnostic-only 候选不可发布"),
        (render.get("emptyBrowserMayCountAsSuccess") is False, "空浏览器不得计为成功"),
        (render.get("whiteAcquisitionMarkerIsProduct") is False, "白色 acquisition marker 不得冒充正式产品"),
        (render.get("automaticSeedRequiredBeforeFallback") is True, "自动获取必须先于点击 fallback"),
        (render.get("ownerClickFallbackMaximumPerAuthorityGeneration") == 1, "fallback 点击上限必须为 1"),
    ]
    safety = manifest.get("safety") if isinstance(manifest.get("safety"), dict) else {}
    checks += [
        (safety.get("readOnly") is True, "readOnly 必须为 true"),
        (safety.get("ramWrites") == 0, "ramWrites 必须为 0"),
        (safety.get("inputInjection") is False, "inputInjection 必须为 false"),
        (safety.get("manualCalibration") is False, "manualCalibration 必须为 false"),
        (safety.get("legacyProjectionSelected") is False, "legacyProjectionSelected 必须为 false"),
        (safety.get("productionOverlayEnabled") is True, "safety.productionOverlayEnabled 必须为 true"),
        (safety.get("productionOverlaySuppressed") is False, "safety.productionOverlaySuppressed 必须为 false"),
    ]
    projection = components.get("projectionProof") if isinstance(components, dict) else None
    if isinstance(projection, dict):
        checks.append((projection.get("selected") is False, "legacy projection proof 不得成为 selected normal path"))
    for ok, reason in checks:
        if not ok:
            raise ManifestError(reason)


def generate_manifest(root: Path, source: str, slice_a_commit: str | None = None) -> dict:
    commit = resolve_commit(root, source)
    slice_a = validate_slice_a_pin(root, commit, slice_a_commit)
    generated_at = commit_generated_at_utc(root, commit)
    selected = selected_paths_from_commit(root, commit)
    paths = list(selected)
    render_files = sorted(set([
        "parallel/PYLAUNCH/render_authority_measurement_entry.py",
        "parallel/PYLAUNCH/wof_launcher/render_measurement_ui.py",
        "parallel/RENDER_AUTHORITY_V2/wof_render_authority_capture_worker.js",
        *SLICE_A_RUNTIME_PATHS,
    ]))
    for path in render_files:
        if path not in selected:
            raise ManifestError("production top-overlay package 文件未被选择：" + path)
    manifest = {
        "schema": SCHEMA,
        "packageVersion": package_version(commit, generated_at),
        "sourceCommit": commit,
        "generatedAtUtc": generated_at,
        "generator": GENERATOR,
        "selectionPolicy": SELECTION_POLICY,
        "baseUrl": f"https://raw.githubusercontent.com/ouyong520/wof-ai-private/{commit}/",
        "components": {
            "ownerOneclick": {
                "sourceCommit": commit,
                "bootstrap": "parallel/OWNER_ONECLICK/bootstrap_v2.ps1",
                "runtimePin": PIN_PATH,
                "files": [p for p in paths if p.startswith("parallel/OWNER_ONECLICK/") or p in {"WOF_一键工具.cmd", "WOF_TOOLKIT.cmd"}],
            },
            "alpha": {"sourceCommit": commit, "fieldAdapter": "product/alpha/wof_alpha_field_adapter.js", "files": component_paths(paths, "product/alpha/")},
            "pylaunch": {"revision": "visible-production-top-overlay-slice-a-pinned", "sourceCommit": commit, "windowsProofEntry": "parallel/PYLAUNCH/RUN_WINDOWS_PROOF.cmd", "directProofEntry": "parallel/PYLAUNCH/WOF_ONECLICK_PROOF_CN.cmd", "files": component_paths(paths, "parallel/PYLAUNCH/")},
            "operatorToolkit": {"sourceCommit": commit, "ownerEntry": "parallel/OPTOOLKIT/owner_zh_cn.py", "files": component_paths(paths, "parallel/OPTOOLKIT/")},
            "renderAuthorityV3": {
                "sourceCommit": commit,
                "sliceARuntimeCommit": slice_a["commit"],
                "sliceARuntimeFiles": slice_a["files"],
                "mode": "owner-visible-production-top-overlay-v1",
                "selectedNormalPath": "production-top-overlay",
                "productionOverlaySource": PRODUCTION_OVERLAY_SOURCE,
                "entry": "parallel/PYLAUNCH/render_authority_measurement_entry.py",
                "ownerFlow": "menu6 -> reuse/enter WOF -> visible tray status -> automatic P1 attempt -> SAFE_UNIQUE zero-click OR bounded one-click real-P1-head fallback -> same maintained Alpha production top overlay -> loss hides -> recovery reappears",
                "ownerClickExpectedNormal": 0,
                "ownerClickMaximumPerAuthorityGeneration": 1,
                "ownerClickFallbackMaximumPerAuthorityGeneration": 1,
                "automaticSeedRequiredBeforeFallback": True,
                "semanticIdentityGate": "W2_FAIL_CLOSED",
                "genericHudPaletteSemanticIdentityAllowed": False,
                "hudPortraitMayIdentifyButNeverSeedSceneHead": True,
                "confidenceLossBehavior": "HIDE_AND_AUTO_RECOVER",
                "productionOverlayEnabled": True,
                "productionOverlaySuppressed": False,
                "diagnosticOnly": False,
                "emptyBrowserMayCountAsSuccess": False,
                "whiteAcquisitionMarkerIsProduct": False,
                "ownerStatusStates": ["WAITING_FOR_WOF", "AUTO_ACQUIRING_P1", "ONE_CLICK_REQUIRED", "TOP_OVERLAY_VISIBLE", "TEMPORARILY_LOST_RECOVERING", "BLOCKED"],
                "files": render_files,
            },
            "projectionProof": {"sourceCommit": commit, "selected": False, "mode": "legacy-compatibility-not-normal-path", "files": component_paths(paths, "parallel/HUDANCHOR_PROOF/")},
            "recorder": {"sourceCommit": commit, "ownerEntry": "parallel/WOF052L_RECORDER/owner_zh_cn.py", "files": component_paths(paths, "parallel/WOF052L_RECORDER/")},
            "browserFleet": {"sourceCommit": commit, "ownerEntry": "parallel/BROWSER_FLEET/fleet_owner_zh_cn.py", "files": component_paths(paths, "parallel/BROWSER_FLEET/")},
            "liveProof": {"sourceCommit": commit, "entry": "parallel/LIVE_PROOF_BUNDLE/RUN_WOF_UNIFIED_LIVE_PROOF.cmd", "files": component_paths(paths, "parallel/LIVE_PROOF_BUNDLE/")},
        },
        "safety": {
            "readOnly": True,
            "ramWrites": 0,
            "inputInjection": False,
            "manualCalibration": False,
            "legacyProjectionSelected": False,
            "ownerClickMaximumPerAuthorityGeneration": 1,
            "productionOverlayEnabled": True,
            "productionOverlaySuppressed": False,
        },
        "files": [{"path": path, "gitBlobSha": selected[path]} for path in paths],
    }
    verify_publishable_manifest(manifest)
    return manifest


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
            raise ManifestError(f"文件完整性校验失败：{path} expected={wanted} actual={actual}")


def render_manifest(manifest: dict) -> str:
    return json.dumps(manifest, ensure_ascii=False, indent=2) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="从一个明确 immutable git commit 确定性生成 Owner One-Click package manifest")
    parser.add_argument("--source", default="HEAD", help="固定 package source commit/ref；默认 HEAD")
    parser.add_argument("--slice-a-commit", help="Slice A visible-overlay integration 的 exact commit；未提供时读取 durable runtime pin")
    parser.add_argument("--output", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--check", action="store_true", help="只校验现有 manifest 与 source/worktree 一致")
    args = parser.parse_args(argv)
    try:
        if args.check:
            try:
                existing = json.loads(args.output.read_text(encoding="utf-8-sig"))
            except Exception as exc:
                raise ManifestError(f"无法读取 package manifest：{args.output}") from exc
            render = existing.get("components", {}).get("renderAuthorityV3", {}) if isinstance(existing, dict) else {}
            pinned = args.slice_a_commit or (render.get("sliceARuntimeCommit") if isinstance(render, dict) else None)
            generated = generate_manifest(ROOT, args.source, str(pinned) if pinned else None)
            verify_publishable_manifest(existing)
            if existing != generated:
                raise ManifestError("package manifest 不是当前所选 immutable snapshot + Slice A exact pin 的确定性产物；请重新生成")
            verify_worktree_payload(ROOT, existing)
            print("PACKAGE MANIFEST PASS：" f"{existing['packageVersion']} source={existing['sourceCommit']} sliceA={generated['components']['renderAuthorityV3']['sliceARuntimeCommit']} files={len(existing['files'])}")
            return 0
        generated = generate_manifest(ROOT, args.source, args.slice_a_commit)
        args.output.write_text(render_manifest(generated), encoding="utf-8")
        verify_worktree_payload(ROOT, generated)
        print("PACKAGE MANIFEST REFRESHED：" f"{generated['packageVersion']} source={generated['sourceCommit']} sliceA={generated['components']['renderAuthorityV3']['sliceARuntimeCommit']} files={len(generated['files'])}")
        return 0
    except ManifestError as exc:
        print(f"PACKAGE MANIFEST BLOCKED：{exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
