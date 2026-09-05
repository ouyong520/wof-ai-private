from __future__ import annotations

import argparse
import json
import os
import sys
import zipfile
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[1]
PYLAUNCH = REPO_ROOT / "parallel" / "PYLAUNCH"
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))
if str(PYLAUNCH) not in sys.path:
    sys.path.insert(0, str(PYLAUNCH))

from qualification_analyzer import analyze_capture, render_markdown


def _write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def default_output_root() -> Path:
    local = os.environ.get("LOCALAPPDATA")
    if local:
        return Path(local) / "WOF_ALPHA_RENDER_AUTHORITY"
    return REPO_ROOT / ".w3_render_authority"


def _qualified_zip(session_dir: Path, output_root: Path) -> Path:
    packages = output_root / "packages"
    packages.mkdir(parents=True, exist_ok=True)
    zip_path = packages / f"WOF_W3_QUALIFIED_{session_dir.name}.zip"
    tmp = zip_path.with_suffix(".zip.partial")
    tmp.unlink(missing_ok=True)
    try:
        with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zf:
            for path in sorted(session_dir.rglob("*")):
                if path.is_file():
                    zf.write(path, path.relative_to(session_dir).as_posix())
        tmp.replace(zip_path)
    finally:
        tmp.unlink(missing_ok=True)
    return zip_path


def finalize_capture(capture_json: Path, output_root: Path | None = None) -> dict[str, Any]:
    capture_json = capture_json.resolve()
    capture = json.loads(capture_json.read_text(encoding="utf-8"))
    if not isinstance(capture, dict):
        raise ValueError("capture JSON must be an object")
    report = analyze_capture(capture)
    session_dir = capture_json.parent
    output_root = (output_root or session_dir.parent).resolve()
    json_path = session_dir / "RENDER_SOURCE_QUALIFICATION.json"
    md_path = session_dir / "RENDER_SOURCE_QUALIFICATION.md"
    _write_json(json_path, report)
    md_path.write_text(render_markdown(report), encoding="utf-8")
    zip_path = _qualified_zip(session_dir, output_root)
    latest = {
        "schema": "wof-w3-long-qualification-latest-v1",
        "status": report["status"],
        "sessionDir": str(session_dir),
        "captureJson": str(capture_json),
        "qualificationJson": str(json_path),
        "qualificationMarkdown": str(md_path),
        "qualifiedBundle": str(zip_path),
        "ownerAction": report.get("ownerAction"),
        "blockingProofEdge": report.get("blockingProofEdge"),
    }
    _write_json(output_root / "LATEST_W3_RENDER_SOURCE_QUALIFICATION.json", latest)
    return latest


def _new_session(before: set[Path], output_root: Path) -> Path:
    after = {p.resolve() for p in output_root.glob("render_authority_*") if p.is_dir()}
    created = sorted(after - before, key=lambda p: p.stat().st_mtime_ns)
    if not created:
        raise RuntimeError("bounded capture completed without a new render_authority session directory")
    return created[-1]


def run_live(root: Path, output_root: Path, host: str, port: int, browser: str, browser_path: str | None) -> int:
    root = root.resolve()
    output_root = output_root.resolve()
    output_root.mkdir(parents=True, exist_ok=True)
    before = {p.resolve() for p in output_root.glob("render_authority_*") if p.is_dir()}
    from measurement_runner import run as measurement_run

    rc = measurement_run(root, output_root, host, port, browser, browser_path)
    if rc != 0:
        return rc
    session_dir = _new_session(before, output_root)
    capture_json = session_dir / "RENDER_AUTHORITY_CAPTURE_RESULT.json"
    if not capture_json.is_file():
        raise RuntimeError(f"bounded capture result missing: {capture_json}")
    latest = finalize_capture(capture_json, output_root)
    print("\nW3 deterministic qualification complete.")
    print("status=" + str(latest["status"]))
    print("result=" + str(output_root / "LATEST_W3_RENDER_SOURCE_QUALIFICATION.json"))
    print("bundle=" + str(latest["qualifiedBundle"]))
    if latest.get("ownerAction"):
        print("next=" + str(latest["ownerAction"]))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="One-command bounded exact-World normal-play capture + deterministic W3 renderer-source qualification"
    )
    parser.add_argument("--root", type=Path, default=REPO_ROOT)
    parser.add_argument("--output-root", type=Path, default=default_output_root())
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=9223)
    parser.add_argument("--browser", choices=["auto", "chrome", "edge"], default="auto")
    parser.add_argument("--browser-path")
    parser.add_argument(
        "--capture-json",
        type=Path,
        help="Offline/dry mode: skip CDP capture and deterministically qualify an existing capture JSON.",
    )
    args = parser.parse_args()
    if args.capture_json:
        latest = finalize_capture(args.capture_json, args.output_root)
        print(json.dumps(latest, ensure_ascii=False, indent=2, sort_keys=True))
        return 0
    return run_live(args.root, args.output_root, args.host, args.port, args.browser, args.browser_path)


if __name__ == "__main__":
    raise SystemExit(main())
