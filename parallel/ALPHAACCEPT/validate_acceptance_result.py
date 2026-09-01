#!/usr/bin/env python3
"""Validate one WOF Alpha Browser Acceptance V2 JSON result.

Stdlib-only support tool. It never connects to the browser, reads game RAM, or injects input.
"""
from __future__ import annotations
import json, re, sys
from pathlib import Path

SCHEMA = "wof-alpha-browser-acceptance-v2"
RELEASE = "wof-alpha-rc3"
TRANSPORT = "wof-alpha-safe-transport-v1"
GOLDEN = "5c369ce2de4f53d8cef87eca5623a1f0d39a779e885532d6f185b81357878f62"
IDENTITY = "wof-world-921031-maincpu-sha256-v1:5c369ce2de4f53d8"
HEX32 = re.compile(r"^[0-9a-f]{32}$")
PASS_RESULT = "PASS — REAL BROWSER ACCEPTANCE V2"
BLOCKED_RESULT = "BLOCKED — TRANSPORT INTEGRATION NOT READY"


def require(cond: bool, msg: str, errors: list[str]) -> None:
    if not cond:
        errors.append(msg)


def validate(o: dict) -> list[str]:
    e: list[str] = []
    require(o.get("schema") == SCHEMA, "schema mismatch", e)
    require(o.get("release") == RELEASE, "release mismatch", e)
    require(o.get("transportVersion") == TRANSPORT, "transportVersion mismatch", e)
    require(o.get("goldenSha256") == GOLDEN, "goldenSha256 mismatch", e)
    require(o.get("expectedIdentitySignature") == IDENTITY, "identity signature mismatch", e)

    if o.get("result") == BLOCKED_RESULT:
        return e
    require(o.get("result") == PASS_RESULT, "top-level result is not PASS", e)

    g = o.get("integrationGate") or {}
    for k in ("status", "productRegression", "transportIntegrationTests", "pylaunchTests",
              "rc5NoWorkerReplacementRegression", "rc4DiagSessionStaleRegression", "exactStaleBoundary1500_1501"):
        require(g.get(k) == "PASS", f"integrationGate.{k} != PASS", e)

    l = o.get("launcher") or {}
    for k in ("browser", "wofPage", "worker", "wasmHeap", "world921031", "launcherIdentityGate"):
        require(l.get(k) is True, f"launcher.{k} != true", e)

    p = o.get("pair") or {}
    require(bool(HEX32.fullmatch(str(p.get("session", "")))), "pair.session is not 32 lowercase hex", e)
    require(isinstance(p.get("initialGeneration"), int) and p["initialGeneration"] >= 1, "invalid initialGeneration", e)
    require(isinstance(p.get("reboundGeneration"), int) and p["reboundGeneration"] > p.get("initialGeneration", 10**18), "reboundGeneration did not increase", e)
    require(bool(HEX32.fullmatch(str(p.get("initialNonce", "")))), "invalid initialNonce", e)
    require(bool(HEX32.fullmatch(str(p.get("reboundNonce", "")))), "invalid reboundNonce", e)
    require(p.get("initialNonce") != p.get("reboundNonce"), "pair nonce did not change", e)
    require(p.get("generationIncreased") is True and p.get("nonceChanged") is True, "fresh pair flags failed", e)

    ident = o.get("detectorIdentity") or {}
    require(ident.get("result") == "PASS" and ident.get("accepted") is True and ident.get("signature") == IDENTITY,
            "detector-local identity did not PASS", e)
    first = o.get("firstCurrentPairState") or {}
    require(first.get("result") == "PASS" and first.get("observed") is True and first.get("hudAuthorityOnlyAfterState") is True,
            "first current-pair state/HUD authority gate failed", e)
    empty = o.get("noWarningState") or {}
    require(empty.get("result") == "PASS" and empty.get("observed") is True, "no-warning state gate failed", e)

    stale = o.get("stale1500") or {}
    require(stale.get("result") in {"PASS", "OFFLINE_GATE_ONLY"}, "stale1500 result invalid", e)
    require(stale.get("exact1500_1501Gate") == "PASS", "exact 1500/1501 offline gate missing", e)

    diag = o.get("diagImmediateClear") or {}
    require(diag.get("result") in {"PASS", "NO_ACTIVE_WARNING"}, "diag immediate-clear gate failed", e)
    require(diag.get("currentPairDiagObserved") is True, "current-pair diag not observed", e)
    require(diag.get("waitedForStaleTimeout") is False, "diag incorrectly waited for stale timeout", e)

    rb = o.get("rebind") or {}
    require(rb.get("result") == "PASS" and rb.get("freshPair") is True and rb.get("freshStateObserved") is True and rb.get("oldAuthorityInherited") is False,
            "rebind freshness gate failed", e)

    neg = o.get("negativePairRejection") or {}
    require(neg.get("result") in {"PASS", "NO_ACTIVE_WARNING"}, "negative pair rejection result failed", e)
    for k in ("oldGenerationStateRejected", "oldGenerationDiagRejected", "wrongNonceStateRejected", "wrongNonceDiagRejected"):
        require(neg.get(k) is True, f"negativePairRejection.{k} != true", e)

    warn = o.get("warningSanity") or {}
    require(warn.get("result") in {"PASS", "NOT_EXERCISED"}, "warning sanity failed", e)
    require(not warn.get("invalidRows"), "invalid warning rows present", e)

    gp = o.get("gameplay") or {}
    require(gp.get("result") == "PASS", "gameplay result failed", e)
    require(gp.get("ownerConfirmedPlayableAtStart") is True, "owner playability confirmation missing", e)
    require(gp.get("renderAliveAcrossStopRebind") is True, "render liveness missing", e)
    require(gp.get("roomRemainedPlayable") is True, "room did not remain playable", e)
    require(gp.get("navigationInjected") is False, "navigation was injected", e)

    s = o.get("safety") or {}
    require(s.get("result") == "PASS", "safety result failed", e)
    require(s.get("readOnly") is True, "readOnly != true", e)
    require(s.get("ramWrites") == 0, "ramWrites != 0", e)
    require(s.get("inputInjection") is False, "inputInjection != false", e)
    require(s.get("windowWorkerReplacement") is False, "windowWorkerReplacement != false", e)
    require(not o.get("failures"), "failures array is not empty", e)
    require(not o.get("incomplete"), "incomplete array is not empty", e)
    return e


def main() -> int:
    if len(sys.argv) != 2:
        print("用法: python validate_acceptance_result.py <acceptance.json>")
        return 2
    try:
        obj = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"FAIL — 无法读取 JSON: {exc}")
        return 2
    if not isinstance(obj, dict):
        print("FAIL — 顶层必须是 JSON object")
        return 1
    errors = validate(obj)
    if errors:
        print("FAIL — ACCEPTANCE JSON INVALID")
        for x in errors:
            print(f"- {x}")
        return 1
    print("PASS — ACCEPTANCE JSON VALID")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
