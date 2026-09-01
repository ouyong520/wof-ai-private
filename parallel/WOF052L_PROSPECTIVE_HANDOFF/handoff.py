from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
PARALLEL_DIR = HERE.parent
ANALYSIS_DIR = PARALLEL_DIR / "WOF052L_ANALYSIS"
VALIDATOR_DIR = PARALLEL_DIR / "PROSPECTIVE_VALIDATOR"
ANALYZER = ANALYSIS_DIR / "analyzer.py"
LIVE_VALIDATOR = VALIDATOR_DIR / "live_validator.py"

ANALYSIS_SCHEMA = "wof-052l-analysis-v1"
MANIFEST_SCHEMA = "wof-prospective-candidate-v1"
STATUS_SCHEMA = "wof-052l-prospective-handoff-v1"
WORLD = "Warriors of Fate (World 921031)"
WORLD_SHA256 = "5c369ce2de4f53d8cef87eca5623a1f0d39a779e885532d6f185b81357878f62"
WAITING = "WAITING_FOR_MORE_DISCOVERY_EVIDENCE"
READY = "AUTOMATIC_DISCOVERY_TO_PROSPECTIVE_HANDOFF_READY"
RUNNING = "PROSPECTIVE_VALIDATION_RUNNING"
COMPLETE = "PROSPECTIVE_VALIDATION_FINISHED"
ERROR = "HANDOFF_ERROR"

FEATURE_MAP: dict[str, tuple[str, str, int]] = {
    "exact_tail2": ("tail2", "signature", 2),
    "tm_tail2": ("tail2", "family", 2),
    "exact_tail3": ("tail3", "signature", 3),
    "tm_tail3": ("tail3", "family", 3),
    "exact_pair": ("pair", "signature", 2),
    "tm_pair": ("pair", "family", 2),
    "exact_triple": ("triple", "signature", 3),
    "tm_triple": ("triple", "family", 3),
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} 不是 JSON object")
    return payload


def write_json_atomic(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + f".tmp-{os.getpid()}")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    os.replace(tmp, path)


def sha256_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def file_sha256(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def canonical_manifest_bytes(manifest: dict[str, Any]) -> bytes:
    return json.dumps(manifest, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8")


def candidate_sha256(manifest: dict[str, Any]) -> str:
    return sha256_bytes(canonical_manifest_bytes(manifest))


def safe_token(value: str, limit: int = 40) -> str:
    out = "".join(c if c.isalnum() else "_" for c in value.upper())
    out = "_".join(x for x in out.split("_") if x)
    return (out or "CANDIDATE")[:limit]


def default_runtime_dir() -> Path:
    root = os.environ.get("LOCALAPPDATA")
    if root:
        return Path(root) / "WOF Future Danger" / "ProspectiveHandoff"
    return HERE / "runtime"


def recorder_output_dir() -> Path | None:
    root = os.environ.get("LOCALAPPDATA")
    base = Path(root) if root else Path.home() / ".local" / "share"
    settings = base / "WOF052LRecorder" / "settings.json"
    try:
        payload = load_json(settings)
    except (OSError, ValueError, json.JSONDecodeError):
        return None
    output = payload.get("outputDir")
    if not output:
        return None
    return Path(str(output)).expanduser().resolve()


def default_analysis_path() -> Path | None:
    output = recorder_output_dir()
    return output / "analysis" / "analysis.json" if output else None


def refresh_analysis(recorder_dir: Path, analysis_path: Path) -> tuple[bool, str]:
    if not ANALYZER.exists():
        return False, f"找不到 analyzer.py：{ANALYZER}"
    cmd = [sys.executable, str(ANALYZER), str(recorder_dir)]
    proc = subprocess.run(cmd, cwd=str(ANALYSIS_DIR), text=True, capture_output=True)
    if proc.returncode != 0:
        detail = (proc.stderr or proc.stdout or "unknown analyzer error").strip()
        return False, f"自动分析刷新失败（exit {proc.returncode}）：{detail}"
    if not analysis_path.exists():
        return False, f"分析器成功退出，但没有生成 {analysis_path}"
    return True, (proc.stdout or "").strip()


def _int_attack(value: Any) -> int:
    text = str(value or "").strip().upper()
    if text.startswith("A"):
        text = text[1:]
    attack = int(text)
    if attack not in (4704, 4712):
        raise ValueError(f"只允许 T18 已知两种结果 A4704/A4712，实际为 {value}")
    return attack


def evaluate_analysis(analysis: dict[str, Any]) -> tuple[bool, list[str], dict[str, Any] | None]:
    reasons: list[str] = []
    if analysis.get("schema") != ANALYSIS_SCHEMA:
        reasons.append(f"analysis.schema 必须是 {ANALYSIS_SCHEMA}")

    safety = analysis.get("safety") or {}
    if safety.get("analysisReadOnly") is not True:
        reasons.append("analysisReadOnly != true")
    if safety.get("ramWrites") != 0:
        reasons.append("ramWrites != 0")
    if safety.get("inputInjection") is not False:
        reasons.append("inputInjection != false")
    if safety.get("productionRuleAutoPromotion") is not False:
        reasons.append("productionRuleAutoPromotion 必须保持 false")
    if safety.get("inputSafetyViolations"):
        reasons.append("analysis 存在 inputSafetyViolations")

    identity = analysis.get("identity") or {}
    if identity.get("ok") is not True:
        reasons.append("World 921031 identity gate 未通过")
    if identity.get("requiredSha256") != WORLD_SHA256:
        reasons.append("requiredSha256 不是 World 921031 黄金 SHA-256")
    observed = identity.get("observedSha256")
    if observed != [WORLD_SHA256]:
        reasons.append("observedSha256 必须且只能包含 World 921031 黄金 SHA-256")

    t18 = analysis.get("t18") or {}
    guardrail = t18.get("guardrail") or {}
    if guardrail.get("singleStateA4704SpecificPromotionForbidden") is not True:
        reasons.append("T18 single-state ambiguity guardrail 缺失")
    if t18.get("verdict") != "resolved":
        reasons.append("T18 判别仍不足")

    distribution = t18.get("distribution") or {}
    thresholds = t18.get("thresholds") or {}
    min_per_outcome = int(thresholds.get("minCandidateCyclesPerOutcome") or 0)
    if min_per_outcome <= 0:
        reasons.append("缺少有效 minCandidateCyclesPerOutcome")
    for attack in ("A4704", "A4712"):
        try:
            count = int(distribution.get(attack, 0))
        except (TypeError, ValueError):
            count = 0
        if min_per_outcome > 0 and count < min_per_outcome:
            reasons.append(f"{attack} 支撑 {count} < 门槛 {min_per_outcome}")

    pv = t18.get("prospectiveValidator") or {}
    if pv.get("worthEntering") is not True:
        reasons.append("analysis 未授权进入 research-only prospective validator")
    candidate = pv.get("candidate") if isinstance(pv.get("candidate"), dict) else None
    if not candidate:
        reasons.append("analysis 没有明确 ordered discriminator candidate")
        return False, reasons, None

    feature = str(candidate.get("feature") or "")
    if feature not in FEATURE_MAP:
        reasons.append(f"候选 feature {feature or '<missing>'} 不是允许的 ordered tail2/tail3/pair/triple")
    if candidate.get("exclusive") is not True:
        reasons.append("候选不是 exclusive")
    try:
        support = int(candidate.get("support", 0))
        opposite = int(candidate.get("oppositeSupport", -1))
    except (TypeError, ValueError):
        support, opposite = 0, -1
    min_seq = int(thresholds.get("minExclusiveSequenceSupport") or 0)
    if min_seq <= 0:
        reasons.append("缺少有效 minExclusiveSequenceSupport")
    elif support < min_seq:
        reasons.append(f"ordered discriminator support {support} < 门槛 {min_seq}")
    if opposite != 0:
        reasons.append(f"ordered discriminator oppositeSupport 必须为 0，实际 {opposite}")
    try:
        _int_attack(candidate.get("outcome"))
    except (TypeError, ValueError) as exc:
        reasons.append(str(exc))

    if feature in FEATURE_MAP:
        _, _, expected_len = FEATURE_MAP[feature]
        pattern = str(candidate.get("pattern") or "")
        states = [x.strip() for x in pattern.split(" -> ") if x.strip()]
        if len(states) != expected_len:
            reasons.append(f"{feature} pattern 应有 {expected_len} 个状态，实际 {len(states)}")

    return not reasons, reasons, candidate


def build_manifest(analysis: dict[str, Any], analysis_sha: str, candidate: dict[str, Any], frozen_at: str) -> dict[str, Any]:
    feature = str(candidate["feature"])
    if feature not in FEATURE_MAP:
        raise ValueError(f"禁止从非 ordered feature 生成 manifest：{feature}")
    kind, matcher_key, expected_len = FEATURE_MAP[feature]
    states = [x.strip() for x in str(candidate.get("pattern") or "").split(" -> ") if x.strip()]
    if len(states) != expected_len:
        raise ValueError(f"{feature} pattern 长度错误：{len(states)} != {expected_len}")
    attack = _int_attack(candidate.get("outcome"))
    support = int(candidate.get("support", 0))
    opposite = int(candidate.get("oppositeSupport", -1))
    if candidate.get("exclusive") is not True or opposite != 0:
        raise ValueError("禁止从非互斥 ordered discriminator 生成 manifest")

    pattern_sha = sha256_bytes(str(candidate["pattern"]).encode("utf-8"))[:12]
    candidate_id = f"WOF052L_T18_A{attack}_{safe_token(feature)}_{pattern_sha}"
    return {
        "schema": MANIFEST_SCHEMA,
        "id": candidate_id,
        "promotion": "research-only",
        "identity": {
            "world": WORLD,
            "sha256": WORLD_SHA256,
        },
        "rule": {
            "sequence": {
                "kind": kind,
                "states": [{matcher_key: state} for state in states],
            },
            "currentPredicates": [
                {"path": "type", "op": "eq", "value": 18},
            ],
        },
        "outcome": {
            "expectedAttacks": [attack],
        },
        "provenance": {
            "source": "WOF-052L analysis.json automatic handoff",
            "analysisSchema": analysis.get("schema"),
            "analysisSha256": analysis_sha,
            "analysisGeneratedAt": analysis.get("generatedAt"),
            "handoffFrozenAt": frozen_at,
            "discoveryEvidenceOnly": True,
            "candidateFeature": feature,
            "candidatePattern": candidate.get("pattern"),
            "candidateSupport": support,
            "candidateOppositeSupport": opposite,
            "candidatePurity": candidate.get("purity"),
            "singleStateA4704SpecificPromotionForbidden": True,
        },
        "safety": {
            "readOnly": True,
            "ramWrites": 0,
            "inputInjection": False,
            "windowWorkerReplacement": False,
            "productionPromotionAllowed": False,
        },
    }


def status_base(analysis_path: Path | None) -> dict[str, Any]:
    return {
        "schema": STATUS_SCHEMA,
        "updatedAt": utc_now(),
        "status": WAITING,
        "statusZh": "等待更多 discovery 证据",
        "analysisPath": str(analysis_path) if analysis_path else None,
        "evidenceBoundary": {
            "discoveryCannotSatisfyProspectiveGate": True,
            "historicalRecorderEvidenceClass": "discovery",
            "prospectiveStartsOnlyAfterFrozenCandidate": True,
            "liveValidatorSessionFreezeAuthoritative": True,
        },
        "safety": {
            "readOnly": True,
            "ramWrites": 0,
            "inputInjection": False,
            "windowWorkerReplacement": False,
            "productionPromotionAllowed": False,
            "productAlphaModified": False,
            "validatorCoreModified": False,
            "recorderCoreModified": False,
        },
    }


def waiting_status(analysis_path: Path | None, reasons: list[str], analysis_sha: str | None = None) -> dict[str, Any]:
    out = status_base(analysis_path)
    out["status"] = WAITING
    out["statusZh"] = "等待更多 discovery 证据"
    out["analysisSha256"] = analysis_sha
    out["reasonsZh"] = reasons
    return out


def ready_status(
    analysis_path: Path,
    analysis_sha: str,
    manifest_path: Path,
    manifest: dict[str, Any],
    manifest_sha: str,
    frozen_at: str,
) -> dict[str, Any]:
    out = status_base(analysis_path)
    out.update({
        "status": READY,
        "statusZh": "自动 discovery -> prospective handoff 已就绪",
        "analysisSha256": analysis_sha,
        "candidate": {
            "id": manifest["id"],
            "manifestPath": str(manifest_path),
            "manifestSha256": manifest_sha,
            "frozenAt": frozen_at,
            "promotion": "research-only",
            "expectedAttacks": manifest["outcome"]["expectedAttacks"],
            "sequence": manifest["rule"]["sequence"],
        },
    })
    return out


def prepare_from_analysis(analysis_path: Path, output_dir: Path) -> tuple[dict[str, Any], Path | None]:
    try:
        raw = analysis_path.read_bytes()
        analysis = json.loads(raw.decode("utf-8"))
        if not isinstance(analysis, dict):
            raise ValueError("analysis.json root 不是 object")
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        return waiting_status(analysis_path, [f"analysis.json 不可用：{exc}"]), None

    analysis_sha = sha256_bytes(raw)
    ready, reasons, candidate = evaluate_analysis(analysis)
    if not ready or candidate is None:
        return waiting_status(analysis_path, reasons, analysis_sha), None

    frozen_at = utc_now()
    try:
        manifest = build_manifest(analysis, analysis_sha, candidate, frozen_at)
        manifest_sha = candidate_sha256(manifest)
    except (KeyError, TypeError, ValueError) as exc:
        return waiting_status(analysis_path, [f"ordered candidate 无法安全转换：{exc}"], analysis_sha), None

    output_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = output_dir / f"{manifest['id']}.candidate.json"
    write_json_atomic(manifest_path, manifest)
    status = ready_status(analysis_path, analysis_sha, manifest_path, manifest, manifest_sha, frozen_at)
    return status, manifest_path


def validator_command(manifest_path: Path, corpus_path: Path, fleet_manifest: Path | None) -> list[str]:
    cmd = [sys.executable, str(LIVE_VALIDATOR), str(manifest_path), "--output", str(corpus_path)]
    if fleet_manifest is not None:
        cmd += ["--fleet-manifest", str(fleet_manifest)]
    return cmd


def run_validator(
    status: dict[str, Any],
    manifest_path: Path,
    output_dir: Path,
    status_path: Path,
    fleet_manifest: Path | None,
) -> int:
    if not LIVE_VALIDATOR.exists():
        status["status"] = ERROR
        status["statusZh"] = "找不到现有 Prospective Validator Framework"
        status["error"] = str(LIVE_VALIDATOR)
        status["updatedAt"] = utc_now()
        write_json_atomic(status_path, status)
        print(f"[错误] {status['statusZh']}：{LIVE_VALIDATOR}")
        return 3

    try:
        on_disk_manifest = load_json(manifest_path)
        on_disk_sha = candidate_sha256(on_disk_manifest)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        on_disk_sha = None
        load_error = str(exc)
    else:
        load_error = None
    expected_sha = str((status.get("candidate") or {}).get("manifestSha256") or "")
    if on_disk_sha != expected_sha:
        status["status"] = ERROR
        status["statusZh"] = "候选 manifest 在冻结后发生变化，已拒绝启动 prospective"
        status["error"] = load_error or f"frozen sha {expected_sha} != current sha {on_disk_sha}"
        status["updatedAt"] = utc_now()
        write_json_atomic(status_path, status)
        print(f"[错误] {status['statusZh']}：{status['error']}")
        return 4

    corpus_path = output_dir / f"{manifest_path.stem}.live_corpus.json"
    result_path = corpus_path.with_name(corpus_path.stem + ".result.json")
    cmd = validator_command(manifest_path, corpus_path, fleet_manifest)
    status["status"] = RUNNING
    status["statusZh"] = "已冻结 research-only 候选，正在使用 Browser Fleet 进行 prospective 验证"
    status["updatedAt"] = utc_now()
    status["validator"] = {
        "framework": str(LIVE_VALIDATOR),
        "browserFleet": str(fleet_manifest) if fleet_manifest else "default Browser Fleet manifest / localhost CDP discovery",
        "corpusPath": str(corpus_path),
        "resultPath": str(result_path),
        "command": cmd,
    }
    write_json_atomic(status_path, status)
    print("[前瞻] 候选已冻结；从现在开始只接受新 live prospective evidence。")
    print("[前瞻] 正在调用现有 Prospective Validator Framework；Browser Fleet 每个 endpoint 独立验证。")
    print("[安全] 只读=true｜游戏 RAM 写入=0｜输入注入=无｜production 自动晋级=禁止")

    proc = subprocess.run(cmd, cwd=str(VALIDATOR_DIR))
    status["updatedAt"] = utc_now()
    status["validator"]["exitCode"] = proc.returncode
    if corpus_path.exists():
        try:
            corpus = load_json(corpus_path)
            status["validator"]["validatorFrozenAt"] = corpus.get("frozenAt")
            status["validator"]["candidateSha256"] = corpus.get("candidateSha256")
            status["validator"]["evidenceClass"] = corpus.get("evidenceClass")
            status["validator"]["corpusStatus"] = corpus.get("status")
        except (OSError, ValueError, json.JSONDecodeError):
            pass
    validator_sha = status["validator"].get("candidateSha256")
    if validator_sha is not None and validator_sha != expected_sha:
        status["status"] = ERROR
        status["statusZh"] = "Validator 实际冻结的 candidate SHA 与 Handoff 冻结 SHA 不一致"
        status["error"] = f"handoff {expected_sha} != validator {validator_sha}"
        write_json_atomic(status_path, status)
        return 5
    status["status"] = COMPLETE if proc.returncode == 0 else ERROR
    status["statusZh"] = "prospective 验证已结束；仍为 research-only，不自动晋级 production" if proc.returncode == 0 else "prospective 验证异常结束；游戏与其他房间保持 fail-open"
    write_json_atomic(status_path, status)
    return proc.returncode


def print_waiting(status: dict[str, Any]) -> None:
    print(f"状态：{WAITING}")
    for reason in status.get("reasonsZh") or []:
        print(f"- {reason}")
    print("不会生成 A4704-specific single-state candidate；继续自然 discovery 采集即可。")


def one_cycle(args: argparse.Namespace, analysis_path: Path | None, output_dir: Path, status_path: Path) -> tuple[str, int]:
    if analysis_path is None:
        status = waiting_status(None, ["找不到 WOF-052L Recorder 保存目录；尚无 analysis.json 可消费。"])
        write_json_atomic(status_path, status)
        print_waiting(status)
        return WAITING, 0

    recorder_dir = recorder_output_dir()
    if args.refresh_analysis and args.analysis is None and recorder_dir is not None:
        ok, detail = refresh_analysis(recorder_dir, analysis_path)
        if not ok:
            status = waiting_status(analysis_path, [detail])
            write_json_atomic(status_path, status)
            print_waiting(status)
            return WAITING, 0

    if not analysis_path.exists():
        status = waiting_status(analysis_path, ["analysis.json 尚未生成。"])
        write_json_atomic(status_path, status)
        print_waiting(status)
        return WAITING, 0

    status, manifest_path = prepare_from_analysis(analysis_path, output_dir)
    write_json_atomic(status_path, status)
    if status["status"] != READY or manifest_path is None:
        print_waiting(status)
        return WAITING, 0

    print("状态：AUTOMATIC DISCOVERY -> PROSPECTIVE HANDOFF READY")
    print(f"候选：{status['candidate']['id']}")
    print(f"Manifest SHA-256：{status['candidate']['manifestSha256']}")
    print(f"冻结时间：{status['candidate']['frozenAt']}")
    print("证据边界：历史 discovery 不能满足 prospective gate；只使用冻结后的新 live corpus。")
    if args.prepare_only:
        return READY, 0
    rc = run_validator(status, manifest_path, output_dir, status_path, args.fleet_manifest)
    return COMPLETE if rc == 0 else ERROR, rc


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description="WOF-052L Analysis -> Prospective Validator 自动 handoff")
    ap.add_argument("--analysis", type=Path, help="analysis.json 路径；默认读取 Recorder 保存目录下 analysis\\analysis.json")
    ap.add_argument("--output-dir", type=Path, default=default_runtime_dir(), help="manifest/status/live corpus 输出目录")
    ap.add_argument("--status-json", type=Path, help="唯一机器状态 JSON；默认 <output-dir>\\handoff_status.json")
    ap.add_argument("--fleet-manifest", type=Path, help="Browser Fleet instances.json；省略则交给现有 live validator 自动发现")
    ap.add_argument("--watch", action="store_true", help="持续刷新/等待 analysis，达到门槛后自动进入 prospective")
    ap.add_argument("--poll-seconds", type=float, default=5.0, help="watch 轮询秒数，默认 5")
    ap.add_argument("--no-refresh-analysis", dest="refresh_analysis", action="store_false", help="不主动刷新 analyzer，只消费现有 analysis.json")
    ap.add_argument("--prepare-only", action="store_true", help="只生成/冻结 manifest，不启动 live validator（测试/审计用）")
    ap.set_defaults(refresh_analysis=True)
    return ap


def main() -> int:
    args = build_parser().parse_args()
    output_dir = args.output_dir.expanduser().resolve()
    status_path = (args.status_json or (output_dir / "handoff_status.json")).expanduser().resolve()
    analysis_path = args.analysis.expanduser().resolve() if args.analysis else default_analysis_path()

    if not args.watch:
        _, rc = one_cycle(args, analysis_path, output_dir, status_path)
        print(f"机器状态：{status_path}")
        return rc

    last_waiting_digest: str | None = None
    print("WOF-052L -> Prospective 自动 handoff 已启动。")
    print("达到 ordered discriminator 门槛前保持 WAITING；达到后自动冻结 research-only manifest 并进入 Browser Fleet prospective。")
    try:
        while True:
            state, rc = one_cycle(args, analysis_path, output_dir, status_path)
            if state != WAITING:
                print(f"机器状态：{status_path}")
                return rc
            try:
                digest = file_sha256(status_path)
            except OSError:
                digest = None
            if digest != last_waiting_digest:
                print(f"机器状态：{status_path}")
                last_waiting_digest = digest
            time.sleep(max(1.0, float(args.poll_seconds)))
            if args.analysis is None:
                analysis_path = default_analysis_path()
    except KeyboardInterrupt:
        print("\n已停止 handoff 监控；没有改变任何 production rule。")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
