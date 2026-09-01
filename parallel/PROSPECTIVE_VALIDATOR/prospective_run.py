from __future__ import annotations

import argparse
import json
import os
import subprocess
from datetime import datetime
from pathlib import Path

from validator import ValidationError, compact_result, load_json, load_traces, make_session, validate, validate_manifest

HERE = Path(__file__).resolve().parent
RECORDER_DIR = HERE.parent / "WOF052L_RECORDER"
RECORDER_CMD = RECORDER_DIR / "RUN_WOF052L_RECORDER.cmd"


def recorder_settings_path() -> Path:
    root = os.environ.get("LOCALAPPDATA") or str(Path.home() / ".local" / "share")
    return Path(root) / "WOF052LRecorder" / "settings.json"


def remembered_capture_dir() -> Path | None:
    try:
        raw = json.loads(recorder_settings_path().read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    value = raw.get("outputDir") if isinstance(raw, dict) else None
    return Path(value).expanduser().resolve() if value else None


def collect_room_json(capture_dir: Path) -> list[Path]:
    rooms = capture_dir / "rooms"
    return sorted(rooms.glob("*.json")) if rooms.is_dir() else []


def main() -> int:
    ap = argparse.ArgumentParser(description="WOF 一次性前瞻验证：冻结候选 -> 复用现有 Recorder/Fleet -> 自动统计")
    ap.add_argument("manifest", help="候选 manifest JSON")
    ap.add_argument("--capture-dir", help="Recorder 保存目录；省略时复用 Recorder 已记住的目录")
    ap.add_argument("--no-capture", action="store_true", help="不启动 Recorder，只验证已有冻结后 corpus")
    ap.add_argument("--corpus", nargs="*", default=[], help="--no-capture 时显式提供 corpus 文件")
    ap.add_argument("--result-dir", default=str(HERE / "results"), help="结果目录")
    args = ap.parse_args()

    try:
        manifest = validate_manifest(load_json(args.manifest))
    except (OSError, json.JSONDecodeError, ValidationError) as exc:
        print(f"候选 manifest 无效：{exc}")
        return 2

    result_dir = Path(args.result_dir).expanduser().resolve()
    result_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    session = make_session(manifest)
    session_file = result_dir / f"{stamp}_{manifest['id']}_session.json"
    session_file.write_text(json.dumps(session, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"候选已冻结：{manifest['id']}")
    print("安全：只读模式开启｜游戏内存写入 0｜游戏输入注入 无｜window.Worker 替换 无")

    corpus_paths: list[Path] = [Path(p).expanduser().resolve() for p in args.corpus]
    if not args.no_capture:
        if os.name != "nt":
            print("当前不是 Windows，无法自动启动 Recorder；请使用 --no-capture 指定已有 corpus。")
            return 2
        if not RECORDER_CMD.is_file():
            print(f"找不到现有 Recorder：{RECORDER_CMD}")
            return 2
        capture_dir = Path(args.capture_dir).expanduser().resolve() if args.capture_dir else remembered_capture_dir()
        cmd = ["cmd.exe", "/c", str(RECORDER_CMD)]
        if capture_dir:
            cmd += ["--output-dir", str(capture_dir)]
        print("正在复用现有 WOF-052L Recorder；Browser Fleet 存在时会由 Recorder 自动复用。")
        code = subprocess.call(cmd, cwd=str(RECORDER_DIR))
        if code not in (0, 130):
            print(f"Recorder 已结束，退出码：{code}；仍尝试读取已落盘证据。")
        capture_dir = capture_dir or remembered_capture_dir()
        if not capture_dir:
            print("无法确定 Recorder 保存目录。")
            return 2
        corpus_paths = collect_room_json(capture_dir)
        if not corpus_paths:
            print(f"没有找到 per-room JSON：{capture_dir / 'rooms'}")
            return 2

    if not corpus_paths:
        print("没有 corpus 可验证。")
        return 2

    try:
        traces, sources = load_traces(corpus_paths, session)
        result = validate(manifest, traces, sources)
    except (OSError, json.JSONDecodeError, ValidationError) as exc:
        print(f"验证失败：{exc}")
        return 2

    full_file = result_dir / f"{stamp}_{manifest['id']}_result.json"
    compact_file = result_dir / f"{stamp}_{manifest['id']}_compact.json"
    full_file.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    compact_file.write_text(json.dumps(compact_result(result), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(compact_result(result), ensure_ascii=False, indent=2))
    print(f"完整结果：{full_file}")
    print(f"紧凑结果：{compact_file}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
