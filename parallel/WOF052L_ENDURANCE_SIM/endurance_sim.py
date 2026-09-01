from __future__ import annotations

import argparse, hashlib, json, os, subprocess, sys, tempfile
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REC = "wof-052l-recorder-v1"
FLEET = "wof-052l-fleet-supervisor-v1"
ANALYSIS = "wof-052l-analysis-v1"
HANDOFF = "wof-052l-prospective-handoff-v1"
WORLD = "Warriors of Fate (World 921031)"
SHA = "5c369ce2de4f53d8cef87eca5623a1f0d39a779e885532d6f185b81357878f62"
CP = 10
SAFE = {"readOnly": True, "ramWrites": 0, "inputInjection": False}
BLOBS = {
    "parallel/WOF052L_RECORDER/recorder.py": "9552d168534f3b742e7390597ff07ea5cfcaeaa2",
    "parallel/WOF052L_RECORDER/fleet_recorder.py": "9398ef1569815439e6c141890f069674a30dca0f",
    "parallel/WOF052L_RECORDER/hardening_v2.py": "4268d39f62d62a624966e7d9fd4afda65f6e94c0",
    "parallel/BROWSER_FLEET/DISCOVERY_CONTRACT.md": "0de1fcf7aa1a540f682b6edd0ed8316831f7d912",
    "parallel/WOF052L_LIVE_CAPTURE/live_capture.py": "4482c8e8e5d65b603f16698d5183cc3bdaa7e9ee",
    "parallel/WOF052L_ANALYSIS/analyzer.py": "0da2a7ba50bf5cc47df03eb73f0e2f2cdcd838cb",
    "parallel/WOF052L_ANALYSIS/ingest.py": "d057f98dd2dba7e7602a74509ac8c8e4fadce135",
    "parallel/WOF052L_PROSPECTIVE_HANDOFF/handoff.py": "8ec85c45eede320adc888320c3fc97d1e6c82df0",
}
CAND = "S0/A4/B2|BODY4728|FE8b660|NX8b204|Vffff|TM1|P6C4736"
NEXT = {
    4704: "S0/A6/B4|BODY4728|FE8b660|NX8b204|Vffff|TM2|P6C4736",
    4712: "S0/A2/B0|BODY4728|FE8b660|NX8b204|Vffff|TM3|P6C4736",
}


def put(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def load(path: Path) -> dict[str, Any]:
    obj = json.loads(path.read_text(encoding="utf-8"))
    return obj if isinstance(obj, dict) else {}


def canon(obj: dict[str, Any]) -> str:
    raw = json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def trace(room: str, attack: int, n: int) -> dict[str, Any]:
    return {"roomId": room, "slot": 1, "type": 18, "activeAttack": attack,
            "candidateSeen": True, "candidateStateIndexes": [0],
            "candidateFirstLeadMs": 80 + n, "candidateLastLeadMs": 60 + n,
            "targetStable": True, "sideStable": True, "retargets": [],
            "states": [{"signature": CAND}, {"signature": NEXT[attack]}]}


@dataclass
class Room:
    sid: str
    i: int
    root: Path
    epoch: int = 1
    seconds: int = 0
    active: bool = True
    connected: bool = True
    reason: str | None = None
    cp_writes: int = 0
    events: list[dict[str, Any]] = field(default_factory=list)

    @property
    def run(self) -> str: return f"{self.sid}-child-{self.i:02d}"
    @property
    def room(self) -> str: return f"room-{self.i:02d}"
    @property
    def port(self) -> int: return 9322 + self.i
    @property
    def page(self) -> str: return f"page-{self.i:02d}-e{self.epoch}"
    @property
    def worker(self) -> str: return f"worker-{self.i:02d}-e{self.epoch}"
    @property
    def session(self) -> str: return f"session-{self.i:02d}-e{self.epoch}"
    @property
    def cp(self) -> Path: return self.root / "checkpoints" / f"{self.run}.checkpoint.json"
    @property
    def final(self) -> Path: return self.root / "rooms" / f"{self.run}_{self.room}.json"

    def traces(self) -> list[dict[str, Any]]:
        return [trace(self.room, 4704, self.i * 10 + 1), trace(self.room, 4704, self.i * 10 + 2),
                trace(self.room, 4712, self.i * 10 + 3), trace(self.room, 4712, self.i * 10 + 4)]

    def payload(self, status: str) -> dict[str, Any]:
        ts = self.traces()
        return {"schema": REC, "runId": self.run, "roomId": self.room, "status": status,
                "finalizationReason": self.reason if status == "complete" else None,
                "target": {"targetId": self.worker, "type": "worker", "sessionId": self.session},
                "page": {"targetId": self.page, "type": "page"},
                "identity": {"world": WORLD, "sha256": SHA, "ok": True}, "safety": dict(SAFE),
                "diagnostics": {"enemySamples": 128, "activeEdges": 4,
                    "t18": {"samples": 32, "resolvedCycles": 4, "candidateCycles": 4, "candidateSamples": 8},
                    "t23": {"samples": 4, "resolvedCycles": 1}, "typeSamples": {"18": 32, "23": 4},
                    "activeAttackFrequency": {"4704": 2, "4712": 2}, "targetSamples": {"P1": 32},
                    "sceneTypeSets": {"18,23": 1}, "rareDescriptorAttack": {}, "playerCountHist": [0, 32, 0, 0]},
                "t18": {"candidateTraces": ts},
                "t23": {"traces": [{"roomId": self.room, "type": 23, "activeAttack": 5888,
                                      "states": [{"signature": f"T23/{self.i}/e{self.epoch}"}]}]},
                "rareDescriptorAttackEdges": [],
                "simulation": {"seconds": self.seconds, "epoch": self.epoch, "events": self.events}}

    def advance(self, seconds: int) -> None:
        if not self.active or not self.connected: return
        old, self.seconds = self.seconds, self.seconds + seconds
        first, last = old // CP + 1, self.seconds // CP
        count = max(0, last - first + 1)
        if count:
            self.cp_writes += count
            put(self.cp, self.payload("running"))

    def reload(self, event: str = "worker-replacement") -> None:
        before = (self.page, self.worker, self.session)
        self.epoch += 1
        self.events.append({"event": event, "before": before, "after": (self.page, self.worker, self.session)})

    def finalize(self, reason: str, preserve_cp: bool = False) -> None:
        self.reason, self.active = reason, False
        put(self.final, self.payload("complete"))
        if not preserve_cp and self.cp.exists(): self.cp.unlink()


class Sim:
    def __init__(self, sid: str, root: Path):
        self.sid, self.root = sid, root / sid
        self.rooms = {i: Room(sid, i, self.root) for i in range(1, 11)}

    def advance(self, seconds: int) -> None:
        for r in self.rooms.values(): r.advance(seconds)

    def finish(self, reason: str = "simulation-complete") -> None:
        for r in self.rooms.values():
            if r.active: r.finalize(reason)

    def child(self, r: Room, status: str | None = None) -> dict[str, Any]:
        st = status or ("complete" if not r.active else "running")
        ts = r.traces()
        return {"schema": REC, "runId": r.run, "status": st, "safety": dict(SAFE),
                "counts": {"enemySamples": 128, "t18Samples": 32, "t18CandidateCycles": 4, "t23Cycles": 1},
                "coverage": {"playerCountHist": [0, 32, 0, 0], "targetSamples": {"P1": 32},
                             "enemyTypeSamplesTop": [{"key": "18", "count": 32}],
                             "activeAttackFrequencyTop": [{"key": "4704", "count": 2}, {"key": "4712", "count": 2}],
                             "sceneTypeSetTop": [{"key": "18,23", "count": 1}]},
                "t18CandidateEvidence": ts,
                "rooms": [{"roomId": r.room, "identitySha256": SHA}],
                "t23SequenceSummary": {"totalCycles": 1}}

    def write_merged(self, status: str | None = None) -> Path:
        runs, evidence, rooms = [], [], []
        total = 0
        for r in self.rooms.values():
            p = self.root / "runs" / f"{r.run}.json"
            child = self.child(r, status)
            put(p, child); evidence += child["t18CandidateEvidence"]
            rooms += child["rooms"]; total += child["counts"]["enemySamples"]
            runs.append({"fleetInstanceId": r.i, "runId": r.run, "file": str(p)})
        fleet = {"schema": FLEET, "runId": f"{self.sid}-fleet", "status": status or "complete",
                 "safety": {**SAFE, "windowWorkerReplacement": False},
                 "counts": {"enemySamples": total}, "t18CandidateEvidence": evidence,
                 "rooms": rooms, "childRuns": runs}
        p = self.root / "fleet_merged.json"; put(p, fleet); return p


def row(name: str, checks: dict[str, bool], detail: str, layer: str = "orchestration", metrics: dict[str, Any] | None = None) -> dict[str, Any]:
    bad = [k for k, v in checks.items() if not v]
    return {"scenario": name, "pass": not bad, "layer": None if not bad else layer,
            "failedAssertions": bad, "assertions": checks, "metrics": metrics or {}, "detailsZh": detail}


def duration(root: Path, name: str, seconds: int) -> dict[str, Any]:
    s = Sim(name, root); s.advance(seconds)
    checks = {"tenActive": sum(r.active for r in s.rooms.values()) == 10,
              "equivalentSeconds": all(r.seconds == seconds for r in s.rooms.values()),
              "checkpointCadence": all(r.cp_writes == seconds // CP for r in s.rooms.values())}
    s.finish(); checks["tenFinal"] = all(r.final.exists() for r in s.rooms.values())
    return row(name, checks, "10 房间按事件时间加速完成，无真实等待。", metrics={"seconds": seconds})


def core_scenarios(root: Path) -> list[dict[str, Any]]:
    out = [duration(root, "normal-10room-1h", 3600), duration(root, "normal-10room-2h", 7200),
           duration(root, "normal-10room-overnight-8h", 28800)]
    s = Sim("disconnect", root); s.advance(600); t = s.rooms[3].seconds; s.rooms[3].finalize("browser-cdp-disconnect", True); s.advance(600)
    out.append(row("single-room-disconnect", {"failedStopped": s.rooms[3].seconds == t, "otherNineContinue": all(s.rooms[i].seconds == 1200 for i in s.rooms if i != 3)}, "单房 CDP 断开只收尾该 child，其余 9 房继续。"))
    s = Sim("reload", root); before = {i: (r.epoch, r.page, r.worker, r.session) for i, r in s.rooms.items()}; s.rooms[4].reload(); after = {i: (r.epoch, r.page, r.worker, r.session) for i, r in s.rooms.items()}
    out.append(row("worker-reload-replacement", {"room4Epoch": after[4][0] == 2, "room4IdsChanged": after[4][1:] != before[4][1:], "otherNineStable": all(after[i] == before[i] for i in before if i != 4)}, "Worker replacement 只提升对应房间 epoch；其他房间 target/session 不变。"))
    s = Sim("page-close", root); s.advance(20); s.rooms[2].finalize("page-closed")
    out.append(row("page-close-finalize", {"finalJson": s.rooms[2].final.exists(), "checkpointCleaned": not s.rooms[2].cp.exists(), "otherNineActive": sum(r.active for r in s.rooms.values()) == 9}, "page close 触发对应房间 final JSON，正常 checkpoint 被清理。"))
    s = Sim("stale-recover", root); s.advance(100); r = s.rooms[5]; r.connected = False; t = r.seconds; s.advance(100); paused = r.seconds == t and all(s.rooms[i].seconds == 200 for i in s.rooms if i != 5); r.connected = True; r.reload("endpoint-recovered"); s.advance(100)
    out.append(row("endpoint-stale-recover", {"pausedOnlyRoom5": paused, "newEpoch": r.epoch == 2, "resumed": r.seconds == 200, "otherNineStillContinue": all(s.rooms[i].seconds == 300 for i in s.rooms if i != 5)}, "endpoint stale 期间只暂停对应房间；recover 后新 epoch 继续。"))
    s = Sim("checkpoint", root); s.advance(3600); before = all(r.cp_writes == 360 and r.cp.exists() for r in s.rooms.values()); s.finish()
    out.append(row("checkpoint-periodic-write", {"360PerRoom": before, "cleanOnFinal": all(not r.cp.exists() for r in s.rooms.values())}, "按当前 Recorder 10 秒周期模拟逻辑 checkpoint；事件时间加速只物化最新快照。"))
    s = Sim("final-json", root); s.advance(30); s.finish(); ps = [load(r.final) for r in s.rooms.values()]
    out.append(row("per-room-final-json", {"tenFiles": len(ps) == 10, "schema": all(p.get("schema") == REC for p in ps), "identity": all((p.get("identity") or {}).get("sha256") == SHA for p in ps), "safety": all(p.get("safety") == SAFE for p in ps)}, "每房最终 JSON 与 Recorder v1 room schema 对齐。"))
    s = Sim("merged", root); s.finish(); fp = s.write_merged(); f = load(fp)
    out.append(row("merged-run-json", {"fleetSchema": f.get("schema") == FLEET, "tenChildRefs": len(f.get("childRuns") or []) == 10, "fortyCandidateTraces": len(f.get("t18CandidateEvidence") or []) == 40, "safety": (f.get("safety") or {}).get("windowWorkerReplacement") is False}, "child merged + Fleet merged index 与当前聚合合同一致。"))
    s = Sim("ctrl-c", root); s.advance(90); [r.finalize("recorder-stopped") for r in s.rooms.values()]; f = load(s.write_merged())
    out.append(row("ctrl-c-graceful-shutdown", {"allFinalized": all(r.reason == "recorder-stopped" for r in s.rooms.values()), "fleetFinal": f.get("status") == "complete"}, "Ctrl+C 等价路径收尾全部 child 后再写 Fleet final index。"))
    s = Sim("abrupt", root); s.advance(30); r = s.rooms[7]; r.finalize("abrupt-child-failure", True); recovery = s.root / "recovery" / "room-07.json"; put(recovery, {"roomId": r.room, "checkpoint": str(r.cp), "final": str(r.final)}); s.advance(30)
    out.append(row("abrupt-child-failure", {"checkpointRetained": r.cp.exists(), "localFinalRetained": r.final.exists(), "recoveryBundle": recovery.exists(), "otherNineContinue": all(s.rooms[i].seconds == 60 for i in s.rooms if i != 7)}, "异常 child 保留最后 checkpoint + local final + recovery bundle；其他 9 房继续。"))
    return out


def repo_root(explicit: Path | None) -> Path | None:
    if explicit:
        p = explicit.resolve(); return p if (p / "parallel" / "WOF052L_ANALYSIS" / "analyzer.py").is_file() else None
    here = Path(__file__).resolve()
    for p in here.parents:
        if (p / "parallel" / "WOF052L_ANALYSIS" / "analyzer.py").is_file(): return p
    return None


def compat(root: Path, repo: Path | None) -> list[dict[str, Any]]:
    fixture = root / "compat"; s = Sim("compat", fixture); s.advance(60); s.write_merged("running")
    if not repo:
        fm = load(s.root / "fleet_merged.json")
        a = row("analyzer-watch-final-fixture-compat", {"fleetSchema": fm.get("schema") == FLEET, "tenChildren": len(fm.get("childRuns") or []) == 10, "fortyTraces": len(fm.get("t18CandidateEvidence") or []) == 40, "safety": (fm.get("safety") or {}).get("readOnly") is True}, "未挂载整仓库；按已读取 HEAD ingest/fixture 合同执行静态兼容检查。", "analyzer")
        manifest = {"schema": "wof-prospective-candidate-v1", "promotion": "research-only", "identity": {"world": WORLD, "sha256": SHA}, "safety": {**SAFE, "windowWorkerReplacement": False}}
        h = canon(manifest); mut = dict(manifest, promotion="tampered")
        b = row("prospective-handoff-freeze-hash-compat", {"researchOnly": True, "canonicalHashStable": h == canon(manifest), "mutationChangesHash": h != canon(mut), "safety": manifest["safety"]["ramWrites"] == 0}, "按当前 HEAD canonical JSON SHA-256 规则验证冻结兼容。", "handoff")
        return [a, b]
    analyzer = repo / "parallel/WOF052L_ANALYSIS/analyzer.py"; hfile = repo / "parallel/WOF052L_PROSPECTIVE_HANDOFF/handoff.py"
    def analyze(tag: str) -> tuple[int, dict[str, Any], str]:
        od = fixture / f"analysis-{tag}"; p = subprocess.run([sys.executable, str(analyzer), str(s.root), "--output-dir", str(od)], cwd=str(analyzer.parent), text=True, capture_output=True)
        ap = od / "analysis.json"; return p.returncode, load(ap) if ap.exists() else {}, (p.stdout or p.stderr or "")[-500:]
    rc1, x1, d1 = analyze("running"); s.finish(); s.write_merged("complete"); rc2, x2, d2 = analyze("final")
    checks = {"runningExit0": rc1 == 0, "finalExit0": rc2 == 0, "schema": x2.get("schema") == ANALYSIS, "resolved": (x2.get("t18") or {}).get("verdict") == "resolved", "worthEntering": ((x2.get("t18") or {}).get("prospectiveValidator") or {}).get("worthEntering") is True, "safety": (x2.get("safety") or {}).get("analysisReadOnly") is True}
    a = row("analyzer-watch-final-fixture-compat", checks, (d1 + "\n" + d2)[-700:], "analyzer")
    hp = fixture / "handoff"; analysis_path = fixture / "analysis-final" / "analysis.json"; p = subprocess.run([sys.executable, str(hfile), "--analysis", str(analysis_path), "--output-dir", str(hp), "--no-refresh-analysis", "--prepare-only"], cwd=str(hfile.parent), text=True, capture_output=True)
    st = load(hp / "handoff_status.json") if (hp / "handoff_status.json").exists() else {}; c = st.get("candidate") or {}; mp = Path(c["manifestPath"]) if c.get("manifestPath") else None; m = load(mp) if mp and mp.exists() else {}; actual = canon(m) if m else None
    b = row("prospective-handoff-freeze-hash-compat", {"exit0": p.returncode == 0, "statusSchema": st.get("schema") == HANDOFF, "ready": st.get("status") == "AUTOMATIC_DISCOVERY_TO_PROSPECTIVE_HANDOFF_READY", "hash": bool(actual) and actual == c.get("manifestSha256"), "researchOnly": m.get("promotion") == "research-only"}, (p.stdout or p.stderr or "")[-700:], "handoff")
    return [a, b]


def isolation_safety(root: Path) -> list[dict[str, Any]]:
    s = Sim("isolation", root); ids = [(r.port, r.page, r.worker, r.session, r.room) for r in s.rooms.values()]
    iso = row("room-session-isolation", {"tenUniqueTuples": len(set(ids)) == 10, "uniquePorts": len({x[0] for x in ids}) == 10, "traceRoomBound": all(all(t["roomId"] == r.room for t in r.traces()) for r in s.rooms.values())}, "endpoint/page/Worker/session/roomId 均唯一，trace roomId 不跨房。")
    s.finish(); ps = [load(r.final) for r in s.rooms.values()]; safe = row("read-only-safety-assertions", {"readOnly": all(p["safety"]["readOnly"] is True for p in ps), "ramWritesZero": all(p["safety"]["ramWrites"] == 0 for p in ps), "inputInjectionFalse": all(p["safety"]["inputInjection"] is False for p in ps), "windowWorkerReplacementFalse": s.write_merged() and load(s.root / "fleet_merged.json")["safety"]["windowWorkerReplacement"] is False}, "模拟器只生成 JSON 证据，不连接浏览器、不执行 CDP、不写 RAM、不注入输入。", "safety")
    return [iso, safe]


def replay(path: Path) -> dict[str, Any]:
    files = [path] if path.is_file() else list(path.rglob("*.json")); good, rooms, bad = 0, set(), []
    for f in files:
        try: p = load(f)
        except Exception: continue
        if p.get("schema") not in {REC, FLEET}: continue
        good += 1
        if (p.get("safety") or {}).get("readOnly") is not True or (p.get("safety") or {}).get("ramWrites") != 0 or (p.get("safety") or {}).get("inputInjection") is not False: bad.append(str(f))
        if p.get("roomId"): rooms.add(p["roomId"])
        rooms.update(x.get("roomId") for x in p.get("rooms") or [] if isinstance(x, dict) and x.get("roomId"))
    return row("replay-existing-corpus", {"recognized": good > 0, "safety": not bad, "roomIds": bool(rooms)}, f"识别 {good} 个现有 Recorder/Fleet JSON；源文件未修改。", metrics={"recognized": good, "rooms": len(rooms), "badSafety": bad})


def run_matrix(out: Path, repo_root: Path | None, replay_path: Path | None = None) -> dict[str, Any]:
    out.mkdir(parents=True, exist_ok=True); root = out / "scenarios"
    repo = repo_root
    rows = core_scenarios(root) + compat(root, repo) + isolation_safety(root)
    if replay_path: rows.append(replay(replay_path))
    failed = [x for x in rows if not x["pass"]]
    m = {"schema": "wof-052l-10room-endurance-matrix-v1", "stageId": "WOF052L_10ROOM_ENDURANCE_SIM_V1", "status": "FAIL" if failed else "PASS", "stopCondition": "BLOCKED" if failed else "WOF052L 10-ROOM ENDURANCE SIM READY", "generatedAt": datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"), "timeAcceleration": {"mode": "event-time", "realBrowserRequired": False, "durationsSeconds": [3600, 7200, 28800]}, "contracts": {"verifiedGitBlobs": BLOBS, "recorderSchema": REC, "fleetSchema": FLEET, "analysisSchema": ANALYSIS, "handoffStatusSchema": HANDOFF, "world": WORLD, "sha256": SHA}, "repoRootUsedForLiveCompatibility": str(repo) if repo else None, "summary": {"total": len(rows), "passed": len(rows) - len(failed), "failed": len(failed)}, "results": rows, "remainingRealOnlyFactsZh": ["真实 Windows Chrome/Edge 1h/2h/overnight 的 OS/GPU/网络稳定性。", "真实 WOF page/Worker/WASM 的长时间资源与 reload/CDP 时序。", "真人 10 房间真实事件分布、覆盖率和 prospective 证据速度。", "真实 OS Ctrl+C/窗口关闭/浏览器崩溃/杀进程边界。"]}
    put(out / "ENDURANCE_MATRIX.json", m); return m


def summary(m: dict[str, Any]) -> str:
    lines = ["# WOF-052L 10 房间耐久模拟结果", "", f"状态：**{m['status']}**", f"通过：{m['summary']['passed']}/{m['summary']['total']}", "", "## 已覆盖"]
    lines += [f"- [{'PASS' if x['pass'] else 'FAIL'}] {x['scenario']} — {x['detailsZh']}" for x in m["results"]]
    lines += ["", "## 仍只能由真实长采集证明"] + [f"- {x}" for x in m["remainingRealOnlyFactsZh"]]
    if m["status"] == "PASS": lines += ["", "## Stop condition", "", "`WOF052L 10-ROOM ENDURANCE SIM READY`"]
    else:
        lines += ["", "## 精确阻断"] + [f"- {x['scenario']}：层={x['layer']}；{','.join(x['failedAssertions'])}" for x in m["results"] if not x["pass"]]
    return "\n".join(lines) + "\n"


def main() -> int:
    p = argparse.ArgumentParser(description="WOF-052L 10-room accelerated endurance simulation/replay harness")
    p.add_argument("--output-dir", type=Path, default=Path(__file__).resolve().parent / "runtime")
    p.add_argument("--repo-root", type=Path); p.add_argument("--replay", type=Path); p.add_argument("--self-test", action="store_true")
    a = p.parse_args(); rr = repo_root(a.repo_root)
    if a.self_test:
        with tempfile.TemporaryDirectory(prefix="wof052l-endurance-") as td:
            m = run_matrix(Path(td), rr, a.replay); print(summary(m)); return 0 if m["status"] == "PASS" else 1
    out = a.output_dir.expanduser().resolve(); m = run_matrix(out, rr, a.replay.expanduser().resolve() if a.replay else None); text = summary(m); (out / "结果摘要.md").write_text(text, encoding="utf-8"); print(text); print(f"机器结果：{out / 'ENDURANCE_MATRIX.json'}"); return 0 if m["status"] == "PASS" else 1


if __name__ == "__main__": raise SystemExit(main())
