"""R0.4.7 deterministic ROM-free Windows portable real-WOF proof bundle builder."""
from __future__ import annotations

import argparse
import hashlib
import json
import stat
import subprocess
import zipfile
from pathlib import Path, PurePosixPath

from . import windows_portable_real_wof_bundle_verifier as verifier

MANIFEST_SCHEMA = verifier.SCHEMA
SIDECAR_SCHEMA = "wof-training-farm-windows-portable-real-wof-proof-bundle-artifact-v1"
STAGE_ID = "TRAINING_FARM_R0_4_7_WINDOWS_PORTABLE_REAL_WOF_PROOF_BUNDLE_V1"
PACKAGE_ID = "WOF_Training_Farm_R0_4_7_Windows_Portable_Real_WOF_Proof_Bundle_V1"
AUTHORITY_BASE_COMMIT = "2eda82450191ce3260e14b93d9d075a0da6cba0d"
DEPENDENCY_PIN = "stable-retro==0.9.8"
FIXED_ZIP_TIMESTAMP = verifier.FIXED_ZIP_TIMESTAMP
INNER_MANIFEST = verifier.INNER_MANIFEST
ROOT_ENTRY = "开始三国10训实机验证.cmd"
ASCII_ENTRY = "START_WOF_PROOF.cmd"
VERIFY_ENTRY = "验证便携包.cmd"
README_ENTRY = "README_开始这里.txt"
PAYLOAD_PREFIX = "payload/"
BundleError = verifier.VerifyError

PROOF_AUTHORITY_BLOBS = {
    "training/__init__.py": "be6357ef548e105315c18f77ddaff6fe785b98fa",
    "training/farm/__init__.py": "854ff42ff1dbf8c63607bbaeda13cfeae094a3c3",
    "training/farm/adapter.py": "61807eba0aa05959bb48cc7bcd059c7a0d802108",
    "training/farm/fake_backend.py": "4321a358fca4de1c535747015110fee0c74c42b3",
    "training/farm/stable_retro_backend.py": "14ba7bf41019900d5189931f7dbb0a2819e53998",
    "training/farm/identity.py": "9bfa117478b381ec5ac0ff21f02a1363c3271148",
    "training/farm/determinism.py": "7cedcd78fe21835b8cc674c2ad781676146984d5",
    "training/farm/determinism.schema.json": "22e0a25065f2d03864d759d9a3e01b187fe22462",
    "training/farm/determinism_actions.example.json": "ff273d576c8ecb8b3ef9db1805d142b7d408a3c0",
    "training/farm/observation_discovery.py": "349703a4a7271bcb8a5b712ee7d9a5bda326501e",
    "training/farm/savestate_fork.py": "dee25c68054c9a79c8af04a854def3dfc6352fd7",
    "training/farm/savestate_fork_contract.py": "c9b05f1a7383f56802a9d3983e507915b1bfd810",
    "training/farm/savestate_fork_branch.py": "db35b377eb3c1f0995b4882c187681ecb4698103",
    "training/farm/savestate_fork_runner.py": "4a76b3db49dc8c9970765cc435152920abb4549a",
    "training/farm/savestate_fork_plan.schema.json": "851dea648c09c8a079d0ba6a33f2c36c74a8ebc9",
    "training/farm/savestate_fork_result.schema.json": "8069e389c6b714de6add708a908b7f9c78d4ea4f",
    "training/farm/real_wof_fork_smoke.plan.json": "4fdc9156730bda758f1a342e332dd39f043d617a",
    "training/farm/real_wof_proof_owner_runner.py": "c966538befeb25f8b6fd694183fa4984ec73b9be",
    "training/farm/beginner_real_wof_launcher.py": "17491953c7d20c76a91b0169c1f8ab68971ce056",
    "training/farm/OWNER_LOCAL_ROM_REFERENCE.md": "e84053558e6acb2613223554792041b3f87a5fb9",
    "training/farm/windows_oneclick_bootstrap.py": "9edbfab10eebb054000e015a96b7d0f03ea91d0c",
    "training/farm/run_windows_oneclick_env_bootstrap.cmd": "2897a840aa4784ec3e83ec7dffb09227fee8f5bb",
    "training/farm/requirements-r0.1.txt": "b98c2e248020600645f4ef65b22ce7f970b5c6db",
}
PORTABLE_SUPPORT_BLOBS = {
    "training/farm/windows_portable_real_wof_bundle_verifier.py": "364b6134dfc5cb69c8efc15470c7dcccf47aa71a",
    "training/farm/windows_portable_real_wof_bundle.manifest.schema.json": "81c7341b9ba5e9147b3f3c1397b53997cd03d80c",
}

def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def git_blob_sha1(data: bytes) -> str:
    return verifier.git_blob(data)

def canonical_json_bytes(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode()

def _read_source(root: Path, rel: str, expected_blob: str) -> bytes:
    verifier.safe(rel)
    path = root / Path(*PurePosixPath(rel).parts)
    if path.is_symlink():
        raise BundleError(f"SYMLINK_NOT_ALLOWED: {rel}")
    if not path.is_file():
        raise BundleError(f"MISSING_SOURCE: {rel}")
    data = path.read_bytes()
    got = git_blob_sha1(data)
    if got != expected_blob:
        raise BundleError(f"SOURCE_BLOB_DRIFT: {rel}: expected={expected_blob} observed={got}")
    return data

def _crlf(text: str) -> bytes:
    return text.replace("\n", "\r\n").encode("utf-8-sig")

def _render_root_start() -> bytes:
    return _crlf(r'''@echo off
setlocal EnableExtensions DisableDelayedExpansion
chcp 65001 >nul 2>nul
set "BUNDLE_ROOT=%~dp0"
for %%I in ("%BUNDLE_ROOT%..") do set "LOCAL_ROOT=%%~fI\三国10训-data"
if not "%WOF_TRAINING_FARM_LOCAL_ROOT%"=="" set "LOCAL_ROOT=%WOF_TRAINING_FARM_LOCAL_ROOT%"
set "WOF_TRAINING_FARM_LOCAL_ROOT=%LOCAL_ROOT%"
set "WOF_BOOTSTRAP_NO_PAUSE=1"
call "%BUNDLE_ROOT%payload\training\farm\run_windows_oneclick_env_bootstrap.cmd" --local-root "%LOCAL_ROOT%" --evidence-root "%LOCAL_ROOT%\evidence" %*
set "RC=%ERRORLEVEL%"
echo.
if "%RC%"=="0" (echo [Training Farm] 命令完成。真实 R0.2/R0.4 是否 PASS 只以 strict runner 输出为准。) else (echo [Training Farm] 返回码 %RC%。请保留 WAITING_PREREQUISITE / BLOCKED 详情。)
if "%WOF_PORTABLE_NO_PAUSE%"=="" pause
exit /b %RC%
''')

def _render_ascii_start() -> bytes:
    return _crlf('@echo off\nsetlocal\ncall "%~dp0开始三国10训实机验证.cmd" %*\nexit /b %ERRORLEVEL%\n')

def _render_verify() -> bytes:
    return _crlf(r'''@echo off
setlocal EnableExtensions DisableDelayedExpansion
chcp 65001 >nul 2>nul
set "ROOT=%~dp0"
set "PY="
for %%V in (3.14 3.13 3.12 3.11 3.10) do if not defined PY (py -%%V -c "import sys; raise SystemExit(0 if (3,10)<=sys.version_info[:2]<=(3,14) else 1)" >nul 2>nul && set "PY=py -%%V")
if not defined PY (python -c "import sys; raise SystemExit(0 if (3,10)<=sys.version_info[:2]<=(3,14) else 1)" >nul 2>nul && set "PY=python")
if not defined PY (echo WAITING_PREREQUISITE - 需要 Python 3.10..3.14 才能执行便携包校验。& if "%WOF_PORTABLE_NO_PAUSE%"=="" pause& exit /b 2)
pushd "%ROOT%payload"
%PY% -m training.farm.windows_portable_real_wof_bundle_verifier --bundle-root "%ROOT%"
set "RC=%ERRORLEVEL%"
popd
if "%WOF_PORTABLE_NO_PAUSE%"=="" pause
exit /b %RC%
''')

def _render_readme(candidate: str) -> bytes:
    return _crlf(f'''Training Farm R0.4.7 Windows 便携实机证明包

来源 candidate: {candidate}

1. 解压到普通本地目录；中文、空格、括号路径均支持。
2. 可先双击“验证便携包.cmd”做 ROM-free 完整性校验。
3. 双击“开始三国10训实机验证.cmd”。
4. R0.4.6 会检测 Python 3.10..3.14、准备同级专用环境，并进入既有 Owner WOF ZIP 选择流程。
5. 只选择你合法持有、且位于本便携包之外的本地 WOF ZIP。
6. evidence 默认在便携包同级“三国10训-data\\evidence”。
7. 只有 strict runner 明确的 R0.2 REAL_WOF PASS + R0.4 REAL_WOF_FORK PASS 才是实机证明。

本包不包含、不下载、不复制 ROM/BIOS/game assets；realWofProof=false；R0.5 未授权；portable 层不修改 proof acceptance 语义。
''')

def build_manifest(root: Path, candidate: str) -> tuple[dict[str, object], dict[str, bytes]]:
    if not isinstance(candidate, str) or not verifier._SHA40.fullmatch(candidate):
        raise BundleError("INVALID_SOURCE_CANDIDATE")
    pins = dict(PROOF_AUTHORITY_BLOBS)
    pins.update(PORTABLE_SUPPORT_BLOBS)
    files: dict[str, bytes] = {}
    rows: list[dict[str, object]] = []
    for rel, blob in sorted(pins.items()):
        if not verifier._SHA40.fullmatch(blob):
            raise BundleError(f"UNPINNED_SOURCE: {rel}")
        data = _read_source(root, rel, blob)
        member = PAYLOAD_PREFIX + rel
        files[member] = data
        rows.append({"path": member, "size": len(data), "sha256": sha256_bytes(data), "role": "proof-runtime" if rel in PROOF_AUTHORITY_BLOBS else "portable-verifier", "sourcePath": rel, "gitBlobSha1": blob})
    generated = [(ROOT_ENTRY, _render_root_start(), "owner-entry"), (ASCII_ENTRY, _render_ascii_start(), "owner-entry-ascii"), (VERIFY_ENTRY, _render_verify(), "package-verifier-entry"), (README_ENTRY, _render_readme(candidate), "owner-readme")]
    for member, data, role in generated:
        verifier.safe(member)
        files[member] = data
        rows.append({"path": member, "size": len(data), "sha256": sha256_bytes(data), "role": role, "sourcePath": None, "gitBlobSha1": None})
    req = next(r for r in rows if r["path"] == PAYLOAD_PREFIX + "training/farm/requirements-r0.1.txt")
    manifest = {
        "schema": MANIFEST_SCHEMA, "version": 1, "stageId": STAGE_ID, "packageId": PACKAGE_ID,
        "sourceCandidate": candidate, "authorityBaseCommit": AUTHORITY_BASE_COMMIT,
        "deterministicMetadata": {"zipTimestamp": "1980-01-01T00:00:00Z", "zipCompression": "stored", "pathSeparator": "/"},
        "proofAuthority": {"r0_2ResultPath": "parallel/TRAINING_FARM_R0_2/RESULT.md", "r0_4ResultPath": "parallel/TRAINING_FARM_R0_4/RESULT.md", "r0_4_6ResultPath": "parallel/TRAINING_FARM_R0_4_6_WINDOWS_ONECLICK_ENV_BOOTSTRAP_V1/RESULT.md", "r0_2RealWofPassAvailable": False, "r0_4RealWofForkPassAvailable": False, "strictRuntimeBlobs": [{"path": p, "gitBlobSha1": s} for p, s in sorted(PROOF_AUTHORITY_BLOBS.items())]},
        "dependencyAuthority": {"path": "training/farm/requirements-r0.1.txt", "requirement": DEPENDENCY_PIN, "gitBlobSha1": req["gitBlobSha1"], "sha256": req["sha256"]},
        "entrypoints": {"start": ROOT_ENTRY, "startAscii": ASCII_ENTRY, "verify": VERIFY_ENTRY, "readme": README_ENTRY},
        "flags": {"containsRomBytes": False, "realWofProof": False, "r0_5Authorized": False, "readOnlyProof": True, "ramWrites": 0, "inputInjection": False},
        "files": sorted(rows, key=lambda r: str(r["path"])), "payloadAggregateSha256": verifier.aggregate(rows),
        "builder": {"module": "training.farm.windows_portable_real_wof_bundle", "verifierMember": PAYLOAD_PREFIX + "training/farm/windows_portable_real_wof_bundle_verifier.py", "schemaMember": PAYLOAD_PREFIX + "training/farm/windows_portable_real_wof_bundle.manifest.schema.json"},
    }
    verifier.validate_manifest(manifest)
    return manifest, files

def _zip_info(name: str) -> zipfile.ZipInfo:
    info = zipfile.ZipInfo(name, FIXED_ZIP_TIMESTAMP)
    info.compress_type = zipfile.ZIP_STORED
    info.create_system = 3
    info.external_attr = (stat.S_IFREG | 0o644) << 16
    info.flag_bits |= 0x800
    return info

def build_zip(root: Path, candidate: str, output: Path, sidecar_path: Path | None = None) -> dict[str, object]:
    manifest, files = build_manifest(root, candidate)
    manifest_bytes = canonical_json_bytes(manifest)
    output.parent.mkdir(parents=True, exist_ok=True)
    all_files = dict(files)
    all_files[INNER_MANIFEST] = manifest_bytes
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_STORED, strict_timestamps=True) as archive:
        for name in sorted(all_files):
            archive.writestr(_zip_info(name), all_files[name])
    raw = output.read_bytes()
    sidecar = {"schema": SIDECAR_SCHEMA, "version": 1, "packageId": PACKAGE_ID, "sourceCandidate": candidate, "zipFile": output.name, "zipSize": len(raw), "zipSha256": sha256_bytes(raw), "innerManifestPath": INNER_MANIFEST, "innerManifestSize": len(manifest_bytes), "innerManifestSha256": sha256_bytes(manifest_bytes), "payloadAggregateSha256": manifest["payloadAggregateSha256"], "containsRomBytes": False, "realWofProof": False, "r0_5Authorized": False}
    if sidecar_path:
        sidecar_path.parent.mkdir(parents=True, exist_ok=True)
        sidecar_path.write_bytes(canonical_json_bytes(sidecar))
    return sidecar

def verify_zip(path: Path, expected_source_candidate: str | None = None) -> dict[str, object]:
    out = verifier.verify_zip(path)
    if expected_source_candidate and out["sourceCandidate"] != expected_source_candidate:
        raise BundleError("SOURCE_CANDIDATE_MISMATCH")
    return out

def verify_extracted(root: Path, expected_source_candidate: str | None = None) -> dict[str, object]:
    out = verifier.verify_extracted(root)
    if expected_source_candidate and out["sourceCandidate"] != expected_source_candidate:
        raise BundleError("SOURCE_CANDIDATE_MISMATCH")
    return out

def _git_head(root: Path) -> str | None:
    try:
        cp = subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"], text=True, capture_output=True)
    except OSError:
        return None
    head = cp.stdout.strip().lower()
    return head if cp.returncode == 0 and verifier._SHA40.fullmatch(head) else None

def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Training Farm R0.4.7 deterministic portable bundle")
    sub = ap.add_subparsers(dest="cmd", required=True)
    build = sub.add_parser("build")
    build.add_argument("--source-root", default=str(Path(__file__).resolve().parents[2]))
    build.add_argument("--source-candidate", required=True)
    build.add_argument("--output", required=True)
    build.add_argument("--sidecar", required=True)
    build.add_argument("--allow-no-git", action="store_true")
    z = sub.add_parser("verify-zip"); z.add_argument("zip"); z.add_argument("--source-candidate")
    e = sub.add_parser("verify-extracted"); e.add_argument("bundle_root"); e.add_argument("--source-candidate")
    args = ap.parse_args(argv)
    try:
        if args.cmd == "build":
            root = Path(args.source_root).resolve(strict=False)
            head = _git_head(root)
            if head is None and not args.allow_no_git:
                raise BundleError("GIT_HEAD_UNAVAILABLE")
            if head is not None and head != args.source_candidate:
                raise BundleError(f"GIT_HEAD_MISMATCH: expected={args.source_candidate} observed={head}")
            print(json.dumps({"status": "PASS", **build_zip(root, args.source_candidate, Path(args.output), Path(args.sidecar))}, ensure_ascii=False, sort_keys=True))
            return 0
        out = verify_zip(Path(args.zip), args.source_candidate) if args.cmd == "verify-zip" else verify_extracted(Path(args.bundle_root), args.source_candidate)
        print(json.dumps(out, ensure_ascii=False, sort_keys=True)); return 0
    except BundleError as exc:
        print(json.dumps({"status": "BLOCKED", "reason": str(exc), "realWofProof": False, "r0_5Authorized": False}, ensure_ascii=False, sort_keys=True)); return 5

if __name__ == "__main__":
    raise SystemExit(main())
