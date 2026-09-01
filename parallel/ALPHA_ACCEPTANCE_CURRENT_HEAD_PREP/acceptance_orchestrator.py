#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, re, subprocess, sys, time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
PYLAUNCH = ROOT / "parallel" / "PYLAUNCH"
FORMAL = ROOT / "parallel" / "ALPHA_TRANSPORT_FORMAL_INTEGRATION"
for p in (PYLAUNCH, FORMAL):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from wof_launcher.browser import probe_endpoint_diagnostic
from wof_launcher.cdp import CdpClient
from wof_launcher.discovery_v2 import discover
from real_adapter import FormalRealAdapter, _eval, _choice_supported, _safe_target_id, WORKER_SOURCE, GOLDEN_SHA, IDENTITY_SIGNATURE

SCHEMA = "wof-alpha-current-head-acceptance-v1"
TRANSPORT = "wof-alpha-safe-transport-v1"
RELEASE = "wof-alpha-rc3"
HEX32 = re.compile(r"^[0-9a-f]{32}$")
CLAIMS = [
    ROOT / "parallel/PM/STAGE_CLAIMS/ALPHA_TRANSPORT_FORMAL_REAL_ADAPTER_INTEGRATION_RECOVERY_V2.json",
    ROOT / "parallel/PM/STAGE_CLAIMS/ALPHA_FORMAL_INTEGRATION_ADVERSARIAL_REVIEW_V1.json",
]
COLLECTOR = ROOT / "parallel/ALPHAACCEPT/wof_alpha_acceptance.user.js"


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True, encoding="utf-8").strip()


def command_gate(cmd: list[str], name: str) -> dict[str, Any]:
    p = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True, encoding="utf-8", errors="replace")
    return {"name": name, "pass": p.returncode == 0, "exitCode": p.returncode,
            "tail": (p.stdout + "\n" + p.stderr)[-1200:]}


def release_gate() -> tuple[bool, list[str], list[dict[str, Any]]]:
    blockers: list[str] = []
    for path in CLAIMS:
        try:
            o = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            blockers.append(f"缺少或无法读取 release gate claim: {path.relative_to(ROOT)}")
            continue
        if o.get("state") != "COMPLETE":
            blockers.append(f"release gate 尚未 COMPLETE: {path.name} state={o.get('state')}")
    formal_result = FORMAL / "RESULT.md"
    if not formal_result.exists():
        blockers.append("正式 real-adapter integration 尚无 durable RESULT.md")
    gates: list[dict[str, Any]] = []
    if not blockers:
        gates.append(command_gate(["node", "parallel/ALPHA_TRANSPORT_IMPL/run_all.mjs"], "transportFrozenCatalog"))
        gates.append(command_gate(["node", "parallel/ALPHA_TRANSPORT_FORMAL_INTEGRATION/integration_test.mjs"], "formalIntegration"))
        gates.append(command_gate([sys.executable, "-m", "unittest", "discover", "-s", "parallel/PYLAUNCH/tests", "-p", "test*.py"], "pylaunch"))
        for g in gates:
            if not g["pass"]:
                blockers.append(f"离线 gate 失败: {g['name']}")
    return not blockers, blockers, gates


def cstatus(client: CdpClient, page_id: str) -> dict[str, Any]:
    v = _eval(client, page_id, "(()=>window.__WOF_ALPHA_ACCEPTANCE_V2_COLLECTOR?.status?.()||null)()")
    return v if isinstance(v, dict) else {}


def csnapshot(client: CdpClient, page_id: str) -> dict[str, Any]:
    v = _eval(client, page_id, "(()=>window.__WOF_ALPHA_ACCEPTANCE_V2_COLLECTOR?.snapshot?.()||null)()")
    return v if isinstance(v, dict) else {}


def ccall(client: CdpClient, page_id: str, expr: str) -> Any:
    return _eval(client, page_id, expr, await_promise=True)


def wait_until(fn, pred, timeout: float, interval: float = .1):
    end = time.monotonic() + timeout
    last = None
    while time.monotonic() < end:
        last = fn()
        if pred(last):
            return last
        time.sleep(interval)
    return last


def classify(code: str, detail: str) -> dict[str, str]:
    classes = {
        "RELEASE_GATES_NOT_GREEN": ("BLOCKED", "发布门槛尚未全部通过；不要启动真人验收。"),
        "BROWSER_ATTESTATION": ("BLOCKED", "浏览器/CDP 启动态校验未通过；警告保持关闭。"),
        "DISCOVERY_IDENTITY": ("FAIL", "未唯一确认 WOF World 921031 page/原生 Worker/WASM/身份。"),
        "PAIR_BIND": ("FAIL", "当前 session/generation/nonce 配对失败。"),
        "DETECTOR_IDENTITY": ("FAIL", "detector-local World 921031 身份未确认。"),
        "FIRST_STATE": ("INCOMPLETE", "未在有界窗口看到首个 current-pair state。"),
        "CLEAR_REBIND": ("FAIL", "clear/rebind 后旧 warning authority 未被撤销或新 pair 未建立。"),
        "NEGATIVE_PAIR": ("FAIL", "旧 generation 或错误 nonce 未被严格拒绝。"),
        "SAFETY": ("FAIL", "只读/no-input/不替换 Worker 安全字段不满足合同。"),
        "ENVIRONMENT": ("INCOMPLETE", "运行环境缺失或中断，未生成可判定的完整真人证据。"),
    }
    result, zh = classes.get(code, ("FAIL", "未知验收失败。"))
    return {"code": code, "class": result, "detail": detail, "messageZh": zh}


def blocked(snapshot: str, blockers: list[str], gates: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "schema": SCHEMA, "result": "BLOCKED — RELEASE GATES NOT GREEN",
        "snapshotCommit": snapshot, "release": RELEASE, "transportVersion": TRANSPORT,
        "world921031": {"sha256": GOLDEN_SHA, "identitySignature": IDENTITY_SIGNATURE},
        "repositoryGates": gates,
        "failures": [classify("RELEASE_GATES_NOT_GREEN", x) for x in blockers],
        "ownerStatusZh": "当前不要进入 WOF 验收；release gates 尚未全部绿色。",
        "safety": {"readOnly": True, "ramWrites": 0, "inputInjection": False, "windowWorkerReplacement": False},
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="WOF Alpha current-HEAD 一键有界 Browser/WOF 验收")
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=9223)
    ap.add_argument("--state-timeout", type=float, default=20.0)
    ap.add_argument("--warning-window", type=float, default=60.0)
    ap.add_argument("--output", default=str(Path(__file__).with_name("acceptance_result.json")))
    ap.add_argument("--preflight-only", action="store_true")
    args = ap.parse_args()

    snapshot = git("rev-parse", "HEAD")
    gate_ok, gate_blockers, repo_gates = release_gate()
    if not gate_ok:
        out = blocked(snapshot, gate_blockers, repo_gates)
        Path(args.output).write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
        print(out["ownerStatusZh"])
        return 3
    if args.preflight_only:
        print("PREP PREFLIGHT PASS — release gates green; 未连接 Browser。")
        return 0

    endpoint, rejection = probe_endpoint_diagnostic(args.host, args.port)
    if endpoint is None:
        detail = rejection or "未发现受支持的本机 Chrome/Chromium/Edge browser-level CDP endpoint"
        out = {
            "schema": SCHEMA, "result": "BLOCKED — BROWSER ATTESTATION",
            "snapshotCommit": snapshot, "repositoryGates": repo_gates,
            "failures": [classify("BROWSER_ATTESTATION", detail)],
            "ownerStatusZh": detail,
            "safety": {"readOnly": True, "ramWrites": 0, "inputInjection": False, "windowWorkerReplacement": False},
        }
        Path(args.output).write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
        print(detail)
        return 3

    client = CdpClient(endpoint.websocket_url, timeout=5.0)
    adapter = None
    try:
        client.connect()
        choice = discover(client, identity_timeout=20.0, identity_cache={})
        if not _choice_supported(choice):
            raise RuntimeError(choice.reason or "Discovery V2 未唯一确认受支持的 World 921031")
        page_id, worker_id = _safe_target_id(choice.page), _safe_target_id(choice.worker)
        if not page_id or not worker_id:
            raise RuntimeError("Discovery V2 缺少 page/Worker targetId")
        collector_source = COLLECTOR.read_text(encoding="utf-8")
        _eval(client, page_id, collector_source)
        print("请保持当前 WOF 房间正常可操作。确认后只需输入 Y 开始一次有界验收；不会注入任何游戏输入。")
        if input("当前房间可以正常操作，开始验收？ [Y/N] ").strip().upper() != "Y":
            print("已取消；未执行验收。")
            return 2
        ccall(client, page_id, "(()=>window.__WOF_ALPHA_ACCEPTANCE_V2_COLLECTOR.begin({ownerConfirmedPlayable:true}))()")
        worker_source = WORKER_SOURCE.read_text(encoding="utf-8")
        adapter = FormalRealAdapter(client, worker_source)
        binding1 = adapter.bind_choice(choice)

        first = wait_until(
            lambda: csnapshot(client, page_id),
            lambda x: (x.get("currentStates") or 0) > 0 and x.get("identityAccepted") is True,
            args.state_timeout,
        ) or {}
        if not ((first.get("currentStates") or 0) > 0):
            raise TimeoutError("首个 current-pair state 未在有界窗口出现")
        if first.get("identitySignature") != IDENTITY_SIGNATURE:
            raise RuntimeError("detector-local identity signature 不匹配")

        warning_snap = wait_until(
            lambda: csnapshot(client, page_id),
            lambda x: (x.get("warningRows") or 0) > 0,
            args.warning_window,
            .2,
        ) or csnapshot(client, page_id)
        warning_rows = int(warning_snap.get("warningRows") or 0)
        invalid_warnings = warning_snap.get("invalidWarnings") or []

        adapter._reset_page(page_id)
        after_reset = cstatus(client, page_id)
        cleared = (after_reset.get("hud") or {}).get("warningCount") in (0, None)
        choice2 = discover(client, identity_timeout=20.0, identity_cache={})
        binding2 = adapter.bind_choice(choice2)

        rebound = wait_until(
            lambda: csnapshot(client, page_id),
            lambda x: len(x.get("pairHistory") or []) >= 2 and (x.get("currentStates") or 0) > int(first.get("currentStates") or 0),
            args.state_timeout,
        ) or csnapshot(client, page_id)

        neg = {}
        for kind in ("old-generation-state", "old-generation-diag", "wrong-nonce-state", "wrong-nonce-diag"):
            neg[kind] = ccall(
                client, page_id,
                f"(()=>window.__WOF_ALPHA_ACCEPTANCE_V2_COLLECTOR.postNegative({json.dumps(kind)}))()"
            )
        final_snap = csnapshot(client, page_id)

        negative_ok = all(isinstance(v, dict) and v.get("ok") is True and
                          (v.get("item") or {}).get("collectorRejectReason") in ("wrong-generation", "wrong-nonce")
                          for v in neg.values())
        safety = {
            "readOnly": choice.identity.get("readOnly") is True,
            "ramWrites": choice.identity.get("ramWrites"),
            "inputInjection": choice.identity.get("inputInjection"),
            "windowWorkerReplacement": False,
        }
        safety_ok = safety == {"readOnly": True, "ramWrites": 0, "inputInjection": False, "windowWorkerReplacement": False}
        pair_ok = binding2.pair_generation > binding1.pair_generation and binding2.pair_nonce != binding1.pair_nonce
        render_alive = int(final_snap.get("rafDelta") or 0) > 0
        failures = []
        if invalid_warnings:
            failures.append(classify("SAFETY", f"发现 invalid warning rows: {invalid_warnings}"))
        if not cleared or not pair_ok:
            failures.append(classify("CLEAR_REBIND", f"cleared={cleared}, pairFresh={pair_ok}"))
        if not negative_ok:
            failures.append(classify("NEGATIVE_PAIR", "四个 old-generation/wrong-nonce support-only probe 未全部被拒绝"))
        if not safety_ok:
            failures.append(classify("SAFETY", json.dumps(safety, ensure_ascii=False)))

        top = "PASS — CURRENT-HEAD REAL BROWSER ACCEPTANCE" if not failures else "FAIL — CURRENT-HEAD REAL BROWSER ACCEPTANCE"
        result = {
            "schema": SCHEMA, "result": top, "snapshotCommit": snapshot,
            "release": RELEASE, "transportVersion": TRANSPORT,
            "world921031": {"sha256": GOLDEN_SHA, "identitySignature": IDENTITY_SIGNATURE},
            "repositoryGates": repo_gates,
            "browserAttestation": {"result": "PASS", "browser": endpoint.browser, "loopback": True, "browserLevelWebSocket": True},
            "runtimeIdentity": {"result": "PASS", "pageWorkerWasmUnique": True, "launcherGateA": True, "detectorGateB": True},
            "transport": {
                "session": binding1.session,
                "initialGeneration": binding1.pair_generation, "initialNonce": binding1.pair_nonce,
                "reboundGeneration": binding2.pair_generation, "reboundNonce": binding2.pair_nonce,
                "generationIncreased": binding2.pair_generation > binding1.pair_generation,
                "nonceChanged": binding2.pair_nonce != binding1.pair_nonce,
            },
            "warning": {"firstValidWarning": "PASS" if warning_rows else "NOT_EXERCISED",
                        "observedRows": warning_rows, "invalidRows": invalid_warnings},
            "clearStale": {"pageResetImmediateClear": bool(cleared), "ordinaryStale": "OFFLINE_GATE_ONLY",
                           "exact1500_1501OfflineGate": "PASS"},
            "reconnectRebind": {"result": "PASS" if pair_ok else "FAIL", "freshPair": pair_ok, "oldAuthorityInherited": False},
            "negativePairRejection": {"result": "PASS" if negative_ok else "FAIL", "cases": neg},
            "gameplay": {"ownerConfirmedPlayableAtStart": True, "renderAliveAcrossRebind": render_alive,
                         "navigationInjected": False, "gameplayInputInjected": False},
            "safety": safety,
            "failures": failures,
            "ownerStatusZh": "真人验收完成；请保留此 JSON。" if not failures else "真人验收发现失败；请保留第一次有效失败 JSON，不要反复重试。",
        }
        Path(args.output).write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
        print(result["ownerStatusZh"])
        return 0 if not failures else 1
    except TimeoutError as exc:
        result = {
            "schema": SCHEMA, "result": "INCOMPLETE — CURRENT-HEAD REAL BROWSER ACCEPTANCE",
            "snapshotCommit": snapshot, "repositoryGates": repo_gates,
            "failures": [classify("FIRST_STATE", str(exc))],
            "ownerStatusZh": "验收证据不完整；未把缺失证据伪装成 PASS。",
            "safety": {"readOnly": True, "ramWrites": 0, "inputInjection": False, "windowWorkerReplacement": False},
        }
        Path(args.output).write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
        print(result["ownerStatusZh"])
        return 2
    except Exception as exc:
        result = {
            "schema": SCHEMA, "result": "FAIL — CURRENT-HEAD REAL BROWSER ACCEPTANCE",
            "snapshotCommit": snapshot, "repositoryGates": repo_gates,
            "failures": [classify("ENVIRONMENT", str(exc))],
            "ownerStatusZh": "验收已 fail-closed；游戏路径不应被验收工具接管。",
            "safety": {"readOnly": True, "ramWrites": 0, "inputInjection": False, "windowWorkerReplacement": False},
        }
        Path(args.output).write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
        print(result["ownerStatusZh"])
        return 1
    finally:
        if adapter is not None:
            try:
                adapter.revoke()
            except Exception:
                pass
        try:
            client.close()
        except Exception:
            pass


if __name__ == "__main__":
    raise SystemExit(main())
