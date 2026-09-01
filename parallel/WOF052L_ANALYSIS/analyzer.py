from __future__ import annotations

import argparse
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any

from common import (
    CANDIDATE_SIG, DEFAULT_MIN_PER_OUTCOME, DEFAULT_MIN_SEQUENCE_SUPPORT,
    DEFAULT_WATCH_INTERVAL, FLEET_SCHEMA, RECORDER_SCHEMA, WORLD_SHA256, Dataset, atomic_write_json,
    atomic_write_text, family_signature, load_json,
)
from engine import analyze
from ingest import build_dataset, input_signature
from report import render_text

# Re-exported for lightweight tests and downstream tooling.
__all__ = [
    "CANDIDATE_SIG", "WORLD_SHA256", "RECORDER_SCHEMA", "FLEET_SCHEMA", "Dataset", "analyze",
    "family_signature", "synthetic_trace", "build_dataset",
]


def default_recorder_output() -> Path | None:
    root = os.environ.get("LOCALAPPDATA")
    base = Path(root) if root else Path.home() / ".local" / "share"
    payload = load_json(base / "WOF052LRecorder" / "settings.json")
    if not payload or not payload.get("outputDir"):
        return None
    path = Path(str(payload["outputDir"])).expanduser()
    return path.resolve() if path.exists() else None


def resolve_analysis_output(args: argparse.Namespace) -> Path:
    if args.output_dir:
        return Path(args.output_dir).expanduser().resolve()
    if len(args.inputs) == 1:
        source = Path(args.inputs[0]).expanduser().resolve()
        if source.is_dir():
            return source / "analysis"
        if source.is_file():
            return source.parent / "analysis"
    return Path.cwd() / "analysis_output"


def analyze_once(args: argparse.Namespace) -> tuple[dict[str, Any], Path, Path]:
    result = analyze(
        build_dataset(args.inputs),
        min_per_outcome=args.min_per_outcome,
        min_sequence_support=args.min_sequence_support,
    )
    out_dir = resolve_analysis_output(args)
    json_path, text_path = out_dir / "analysis.json", out_dir / "分析结果.txt"
    atomic_write_json(json_path, result)
    atomic_write_text(text_path, render_text(result))
    return result, json_path, text_path


def run_watch(args: argparse.Namespace) -> int:
    print("WOF-052L 自动分析监控已启动。")
    print("只读分析 / 游戏内存写入 0 / 不注入输入 / 不自动晋级生产规则。")
    print("发现新的或更新后的 JSON 后，会自动刷新 analysis.json 与 分析结果.txt。")
    previous: tuple[tuple[str, int, int], ...] | None = None
    try:
        while True:
            current = input_signature(args.inputs)
            if current != previous:
                result, json_path, text_path = analyze_once(args)
                print(
                    f"[{datetime.now().strftime('%H:%M:%S')}] 已更新：T18 {result['t18']['verdictZh']} | "
                    f"A4704 {result['t18']['distribution']['A4704']} | A4712 {result['t18']['distribution']['A4712']}"
                )
                print(f"机器结果：{json_path}")
                print(f"中文结果：{text_path}")
                previous = current
            time.sleep(max(1.0, float(args.interval)))
    except KeyboardInterrupt:
        print("\n已停止自动分析监控。")
        return 0


def synthetic_trace(attack: int, next_sig: str, *, room: str, lead: float = 50.0, stable: bool = True) -> dict[str, Any]:
    return {
        "roomId": room,
        "slot": 1,
        "type": 18,
        "activeAttack": attack,
        "candidateSeen": True,
        "candidateStateIndexes": [0],
        "candidateFirstLeadMs": lead,
        "candidateLastLeadMs": lead - 5,
        "targetStable": stable,
        "sideStable": stable,
        "retargets": [] if stable else [{"from7E": 0, "to7E": 4}],
        "states": [{"signature": CANDIDATE_SIG}, {"signature": next_sig}],
    }


def self_test() -> int:
    ds = Dataset()
    a = "S0/A6/B4|BODY4728|FE8b660|NX8b204|Vffff|TM2|P6C4736"
    b = "S0/A2/B0|BODY4728|FE8b660|NX8b204|Vffff|TM3|P6C4736"
    for i in range(2):
        ds.add_trace(synthetic_trace(4704, a, room=f"a{i}"), "self")
        ds.add_trace(synthetic_trace(4712, b, room=f"b{i}"), "self")
    ds.identity_shas.add(WORLD_SHA256)
    result = analyze(ds, min_per_outcome=2, min_sequence_support=2)
    assert result["t18"]["verdict"] == "resolved"
    assert result["t18"]["prospectiveValidator"]["worthEntering"] is True
    assert result["t18"]["distribution"] == {"A4704": 2, "A4712": 2}
    ds2 = Dataset()
    ds2.add_trace(synthetic_trace(4704, a, room="a"), "self")
    ds2.add_trace(synthetic_trace(4712, b, room="b"), "self")
    assert analyze(ds2, min_per_outcome=2, min_sequence_support=2)["t18"]["verdict"] == "insufficient"
    assert family_signature("S0/A4/B2|BODY4728|FE1|NX2|V3|TM99|P6C4").endswith("|TM*|P6C4")
    print("自检通过 — WOF-052L 自动分析器的保守判定、序列统计与安全门槛正常。")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="WOF-052L 自动离线分析器")
    p.add_argument("inputs", nargs="*", help="一个或多个 JSON 文件/目录；目录会递归扫描 JSON")
    p.add_argument("--output-dir", default=None, help="输出目录；默认写到输入目录下的 analysis")
    p.add_argument("--watch", action="store_true", help="持续监控输入目录，JSON 变化后自动刷新结果")
    p.add_argument("--interval", type=float, default=DEFAULT_WATCH_INTERVAL, help="监控间隔秒数，默认 5")
    p.add_argument("--min-per-outcome", type=int, default=DEFAULT_MIN_PER_OUTCOME, help="A4704/A4712 各自最少候选周期，默认 2")
    p.add_argument("--min-sequence-support", type=int, default=DEFAULT_MIN_SEQUENCE_SUPPORT, help="互斥区分序列最少支持数，默认 2")
    p.add_argument("--self-test", action="store_true", help="运行离线自检")
    return p


def main() -> int:
    args = build_parser().parse_args()
    if args.self_test:
        return self_test()
    if not args.inputs:
        recorder_output = default_recorder_output()
        if recorder_output:
            args.inputs = [str(recorder_output)]
            print(f"已自动使用 WOF-052L Recorder 保存目录：{recorder_output}")
        else:
            print("错误：没有找到 Recorder 已保存的目录。请提供一个 WOF-052L JSON 文件或保存目录。", file=sys.stderr)
            return 2
    if args.watch:
        return run_watch(args)
    result, json_path, text_path = analyze_once(args)
    print(f"T18 判别：{result['t18']['verdictZh']}")
    print(f"支撑样本数：{result['t18']['supportSamples']}")
    print(f"A4704/A4712：{result['t18']['distribution']['A4704']}/{result['t18']['distribution']['A4712']}")
    print(f"是否值得进入新的前瞻验证器：{'是' if result['t18']['prospectiveValidator']['worthEntering'] else '否'}")
    print(f"中文结果：{text_path}")
    print(f"机器结果：{json_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
