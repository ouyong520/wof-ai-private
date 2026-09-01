from __future__ import annotations

import argparse
import json
import os
import queue
import re
import statistics
import subprocess
import tempfile
import threading
import time
import urllib.error
import urllib.request
import uuid
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import websocket

APP_NAME = "WOF052LRecorder"
SCHEMA_VERSION = "wof-052l-recorder-v1"
PROBE_VERSION = "wof-052l-event-recorder-probe-v1"
WORLD_SHA256 = "5c369ce2de4f53d8cef87eca5623a1f0d39a779e885532d6f185b81357878f62"
CANDIDATE_SIG = "S0/A4/B2|BODY4728|FE8b660|NX8b204|Vffff|TM1|P6C4736"
GSTYPHOON_RE = re.compile(r"(?:^|[/\\])gstyphoon[^/?#]*\.js(?:[?#].*)?$", re.I)

DRAIN_INTERVAL = 1.0
CHECKPOINT_INTERVAL = 10.0
DISCOVERY_INTERVAL = 1.0
ROLLING_MERGE_INTERVAL = 15.0
MAX_T18_CANDIDATE_TRACES = 1000
MAX_T18_OTHER_TRACES = 300
MAX_T23_TRACES = 400
MAX_RARE_EDGES = 300

READ_ONLY_METHODS = {
    "Target.getTargets",
    "Target.attachToTarget",
    "Target.detachFromTarget",
    "Runtime.enable",
    "Runtime.evaluate",
}

LIGHT_PROBE = r"""(()=>{
'use strict';
const good=v=>!!(v&&v.HEAPU8 instanceof Uint8Array&&v.HEAPU32 instanceof Uint32Array&&v.HEAPU8.buffer===v.HEAPU32.buffer);
let mod=null,key=null;
try{if(good(globalThis._0x515056)){mod=globalThis._0x515056;key='_0x515056';}}catch(_){}
if(!mod){for(const k of Object.getOwnPropertyNames(globalThis)){let v;try{v=globalThis[k];}catch(_){continue;}if(good(v)){mod=v;key=k;break;}}}
if(!mod)return {moduleOk:false,heapOk:false,readOnly:true,ramWrites:0,inputInjection:false};
const heap=mod.HEAPU8;let ramBase=null,ramWithinHeap=false;
try{ramBase=mod.HEAPU32[0x2e39e4>>>2]>>>0;ramWithinHeap=!!ramBase&&ramBase+0x10000<=heap.length;}catch(_){}
return {moduleOk:true,moduleKey:key,heapOk:heap instanceof Uint8Array,heapBytes:heap.length,ramBase,ramWithinHeap,readOnly:true,ramWrites:0,inputInjection:false};
})()"""


def utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def local_stamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def safe_name(value: str, max_len: int = 80) -> str:
    clean = re.sub(r"[^A-Za-z0-9._-]+", "-", value).strip("-._")
    return (clean or "room")[:max_len]


def atomic_write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + f".tmp-{os.getpid()}-{uuid.uuid4().hex[:6]}")
    with tmp.open("w", encoding="utf-8", newline="\n") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
        f.write("\n")
    os.replace(tmp, path)


def app_state_dir() -> Path:
    root = os.environ.get("LOCALAPPDATA") or str(Path.home() / ".local" / "share")
    return Path(root) / APP_NAME


def settings_path() -> Path:
    return app_state_dir() / "settings.json"


def load_settings() -> dict[str, Any]:
    p = settings_path()
    if not p.is_file():
        return {}
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def save_settings(data: dict[str, Any]) -> None:
    atomic_write_json(settings_path(), data)


def choose_output_dir() -> Path:
    chosen = ""
    try:
        import tkinter as tk
        from tkinter import filedialog
        root = tk.Tk(); root.withdraw(); root.attributes("-topmost", True)
        chosen = filedialog.askdirectory(title="Choose WOF-052L capture folder")
        root.destroy()
    except Exception:
        pass
    if not chosen:
        print("First run: choose a folder for WOF-052L JSON output.")
        chosen = input("Save folder: ").strip().strip('"')
    if not chosen:
        raise SystemExit("No save folder selected.")
    return Path(chosen).expanduser().resolve()


def resolve_output_dir(cli_value: str | None, reset: bool) -> Path:
    settings = load_settings()
    if reset:
        settings.pop("outputDir", None)
    if cli_value:
        out = Path(cli_value).expanduser().resolve(); settings["outputDir"] = str(out); save_settings(settings)
    elif settings.get("outputDir"):
        out = Path(str(settings["outputDir"])).expanduser().resolve()
    else:
        out = choose_output_dir(); settings["outputDir"] = str(out); save_settings(settings)
    out.mkdir(parents=True, exist_ok=True)
    for child in ("rooms", "checkpoints", "runs"):
        (out / child).mkdir(parents=True, exist_ok=True)
    return out


def http_json(url: str, timeout: float = 0.7) -> dict[str, Any] | None:
    req = urllib.request.Request(url, headers={"User-Agent": f"{APP_NAME}/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as res:
            data = json.loads(res.read().decode("utf-8")); return data if isinstance(data, dict) else None
    except (OSError, ValueError, urllib.error.URLError):
        return None


@dataclass(frozen=True)
class BrowserEndpoint:
    host: str
    port: int
    browser: str
    websocket_url: str
    @property
    def label(self) -> str:
        return f"{self.browser} @ {self.host}:{self.port}"


def probe_endpoint(host: str, port: int) -> BrowserEndpoint | None:
    data = http_json(f"http://{host}:{port}/json/version")
    if not data:
        return None
    ws = data.get("webSocketDebuggerUrl")
    if not isinstance(ws, str) or not ws.startswith("ws"):
        return None
    return BrowserEndpoint(host, port, str(data.get("Browser") or "Chromium"), ws)


def candidate_ports(explicit: int | None) -> list[int]:
    ports: list[int] = []
    if explicit:
        ports.append(explicit)
    for p in [9223, 9222, *range(9224, 9236)]:
        if p not in ports:
            ports.append(p)
    return ports


def find_endpoint(host: str, explicit_port: int | None) -> BrowserEndpoint | None:
    for port in candidate_ports(explicit_port):
        ep = probe_endpoint(host, port)
        if ep:
            return ep
    return None


def browser_candidates(preference: str = "auto") -> list[Path]:
    env = os.environ; local = Path(env.get("LOCALAPPDATA", "")); pf = Path(env.get("PROGRAMFILES", r"C:\Program Files")); pfx86 = Path(env.get("PROGRAMFILES(X86)", r"C:\Program Files (x86)"))
    chrome = [local / "Google/Chrome/Application/chrome.exe", pf / "Google/Chrome/Application/chrome.exe", pfx86 / "Google/Chrome/Application/chrome.exe"]
    edge = [pf / "Microsoft/Edge/Application/msedge.exe", pfx86 / "Microsoft/Edge/Application/msedge.exe", local / "Microsoft/Edge/Application/msedge.exe"]
    order = edge + chrome if preference == "edge" else chrome + edge
    if preference == "chrome": order = chrome + edge
    seen: set[str] = set(); out: list[Path] = []
    for p in order:
        k = str(p).lower()
        if k not in seen: seen.add(k); out.append(p)
    return out


def find_browser(preference: str) -> Path | None:
    for p in browser_candidates(preference):
        if p.is_file(): return p
    return None


def launch_debug_browser(preference: str, host: str, port: int, game_url: str | None) -> subprocess.Popen[Any] | None:
    exe = find_browser(preference)
    if not exe: return None
    profile = app_state_dir() / "BrowserProfile"; profile.mkdir(parents=True, exist_ok=True)
    args = [str(exe), f"--remote-debugging-address={host}", f"--remote-debugging-port={port}", f"--user-data-dir={profile}", "--no-first-run", "--no-default-browser-check", game_url or "about:blank"]
    return subprocess.Popen(args, close_fds=True)


class CdpError(RuntimeError):
    pass


class CdpClient:
    def __init__(self, websocket_url: str, timeout: float = 5.0):
        self.websocket_url = websocket_url; self.timeout = timeout; self._ws: websocket.WebSocket | None = None; self._rx: threading.Thread | None = None; self._closed = threading.Event(); self._id_lock = threading.Lock(); self._pending_lock = threading.Lock(); self._next_id = 1; self._pending: dict[int, queue.Queue[dict[str, Any]]] = {}
    def connect(self) -> None:
        self._ws = websocket.create_connection(self.websocket_url, timeout=self.timeout, suppress_origin=True); self._ws.settimeout(1.0); self._closed.clear(); self._rx = threading.Thread(target=self._receiver, name="wof052l-cdp-rx", daemon=True); self._rx.start()
    @property
    def closed(self) -> bool:
        return self._closed.is_set() or self._ws is None
    def _receiver(self) -> None:
        ws = self._ws
        if ws is None: return
        try:
            while not self._closed.is_set():
                try: raw = ws.recv()
                except websocket.WebSocketTimeoutException: continue
                if not raw: break
                try: msg = json.loads(raw)
                except ValueError: continue
                mid = msg.get("id")
                if isinstance(mid, int):
                    with self._pending_lock: q = self._pending.pop(mid, None)
                    if q: q.put(msg)
        except Exception: pass
        finally: self._closed.set()
    def close(self) -> None:
        self._closed.set(); ws, self._ws = self._ws, None
        if ws:
            try: ws.close()
            except Exception: pass
        with self._pending_lock: pending = list(self._pending.values()); self._pending.clear()
        for q in pending:
            try: q.put_nowait({"error": {"message": "CDP connection closed"}})
            except Exception: pass
    def request(self, method: str, params: dict[str, Any] | None = None, *, session_id: str | None = None, timeout: float | None = None) -> dict[str, Any]:
        if method not in READ_ONLY_METHODS: raise CdpError(f"read-only policy blocks CDP method: {method}")
        if self.closed: raise CdpError("CDP is not connected")
        with self._id_lock: mid = self._next_id; self._next_id += 1
        q: queue.Queue[dict[str, Any]] = queue.Queue(maxsize=1)
        with self._pending_lock: self._pending[mid] = q
        payload: dict[str, Any] = {"id": mid, "method": method, "params": params or {}}
        if session_id: payload["sessionId"] = session_id
        try:
            assert self._ws is not None; self._ws.send(json.dumps(payload, separators=(",", ":"))); res = q.get(timeout=timeout or self.timeout)
        except Exception as exc:
            with self._pending_lock: self._pending.pop(mid, None)
            raise CdpError(f"CDP {method} failed: {exc}") from exc
        if "error" in res: raise CdpError(f"CDP {method}: {res['error']}")
        result = res.get("result")
        if not isinstance(result, dict): raise CdpError(f"CDP {method}: malformed result")
        return result
    def targets(self) -> list[dict[str, Any]]:
        rows = self.request("Target.getTargets").get("targetInfos") or []; return [x for x in rows if isinstance(x, dict)]
    def attach(self, target_id: str) -> "CdpSession":
        result = self.request("Target.attachToTarget", {"targetId": target_id, "flatten": True}, timeout=8.0); sid = result.get("sessionId")
        if not isinstance(sid, str): raise CdpError("Target.attachToTarget returned no sessionId")
        return CdpSession(self, target_id, sid)


@dataclass
class CdpSession:
    client: CdpClient
    target_id: str
    session_id: str
    def request(self, method: str, params: dict[str, Any] | None = None, timeout: float | None = None) -> dict[str, Any]:
        return self.client.request(method, params, session_id=self.session_id, timeout=timeout)
    def evaluate(self, expression: str, *, await_promise: bool = False, timeout: float = 8.0) -> Any:
        result = self.request("Runtime.evaluate", {"expression": expression, "returnByValue": True, "awaitPromise": await_promise, "silent": True}, timeout=timeout)
        if result.get("exceptionDetails"): raise CdpError(f"Runtime.evaluate exception: {result['exceptionDetails']}")
        remote = result.get("result") or {}
        if "value" in remote: return remote["value"]
        if remote.get("subtype") == "null": return None
        raise CdpError(f"Runtime.evaluate did not return by value: {remote}")
    def close(self) -> None:
        try: self.client.request("Target.detachFromTarget", {"sessionId": self.session_id}, timeout=3.0)
        except Exception: pass


def top_map(mapping: dict[str, int] | Counter[str], n: int = 80) -> list[dict[str, Any]]:
    return [{"key": k, "count": int(v)} for k, v in sorted(mapping.items(), key=lambda kv: (-int(kv[1]), kv[0]))[:n]]


def family_signature(sig: str) -> str:
    return re.sub(r"\|TM[^|]*", "|TM*", str(sig or ""))


def _summary_for_traces(traces: list[dict[str, Any]], candidate_only: bool) -> dict[str, Any]:
    summary: dict[str, Any] = {"totalCycles": 0, "byAttack": {}}
    for tr in traces:
        if candidate_only and not tr.get("candidateSeen"): continue
        attack = str(tr.get("activeAttack", "unknown"))
        b = summary["byAttack"].setdefault(attack, {"cycles":0,"targetStable":0,"sideStable":0,"candidateFirstLeadSamples":[],"candidateLastLeadSamples":[],"_finalExact":Counter(),"_tail2Exact":Counter(),"_tail3Exact":Counter(),"_finalFamily":Counter(),"_tail2Family":Counter(),"_tail3Family":Counter(),"_transitions":Counter(),"_triples":Counter()})
        b["cycles"] += 1; summary["totalCycles"] += 1; b["targetStable"] += int(bool(tr.get("targetStable"))); b["sideStable"] += int(bool(tr.get("sideStable")))
        if tr.get("candidateFirstLeadMs") is not None: b["candidateFirstLeadSamples"].append(float(tr["candidateFirstLeadMs"]))
        if tr.get("candidateLastLeadMs") is not None: b["candidateLastLeadSamples"].append(float(tr["candidateLastLeadMs"]))
        states = tr.get("states") or []; exact = [str(x.get("signature") or "") for x in states if isinstance(x, dict) and x.get("signature")]
        if candidate_only:
            indexes = tr.get("candidateStateIndexes") or []
            if indexes:
                try: exact = exact[int(indexes[0]):]
                except Exception: pass
        if exact:
            b["_finalExact"][exact[-1]] += 1
            if len(exact)>=2: b["_tail2Exact"][" -> ".join(exact[-2:])] += 1
            if len(exact)>=3: b["_tail3Exact"][" -> ".join(exact[-3:])] += 1
        fams: list[str] = []
        for sig in exact:
            f = family_signature(sig)
            if not fams or fams[-1] != f: fams.append(f)
        if fams:
            b["_finalFamily"][fams[-1]] += 1
            if len(fams)>=2: b["_tail2Family"][" -> ".join(fams[-2:])] += 1
            if len(fams)>=3: b["_tail3Family"][" -> ".join(fams[-3:])] += 1
        for i in range(1,len(fams)): b["_transitions"][f"{fams[i-1]} -> {fams[i]}"] += 1
        for i in range(2,len(fams)): b["_triples"][f"{fams[i-2]} -> {fams[i-1]} -> {fams[i]}"] += 1
    for b in summary["byAttack"].values():
        cycles = int(b["cycles"]); b["targetStableRate"] = round(b["targetStable"]/cycles,3) if cycles else None; b["sideStableRate"] = round(b["sideStable"]/cycles,3) if cycles else None
        for prefix in ("candidateFirstLead","candidateLastLead"):
            vals = b.pop(prefix+"Samples"); b[prefix+"Min"] = min(vals) if vals else None; b[prefix+"Median"] = statistics.median(vals) if vals else None; b[prefix+"Max"] = max(vals) if vals else None
        for src,dst,limit in [("_finalExact","finalExactTop",60),("_tail2Exact","tail2ExactTop",60),("_tail3Exact","tail3ExactTop",60),("_finalFamily","finalFamilyTop",60),("_tail2Family","tail2FamilyTop",60),("_tail3Family","tail3FamilyTop",60),("_transitions","transitionTop",100),("_triples","tripleTop",100)]: b[dst] = top_map(b.pop(src),limit)
    return summary


def t18_sequence_summary(traces: list[dict[str, Any]]) -> dict[str, Any]:
    out = _summary_for_traces(traces, True); out["candidateSignature"] = CANDIDATE_SIG; return out


def t23_sequence_summary(traces: list[dict[str, Any]]) -> dict[str, Any]:
    return _summary_for_traces(traces, False)


@dataclass
class RoomCapture:
    run_id: str
    room_id: str
    target: dict[str, Any]
    page: dict[str, Any] | None
    session: CdpSession
    output_dir: Path
    bootstrap: dict[str, Any]
    started_at: str = field(default_factory=utc_iso)
    started_monotonic: float = field(default_factory=time.monotonic)
    last_drain: float = 0.0
    last_checkpoint: float = 0.0
    latest_status: dict[str, Any] = field(default_factory=dict)
    t18_candidate_traces: list[dict[str, Any]] = field(default_factory=list)
    t18_other_traces: list[dict[str, Any]] = field(default_factory=list)
    t23_traces: list[dict[str, Any]] = field(default_factory=list)
    rare_edges: list[dict[str, Any]] = field(default_factory=list)
    event_counts: Counter[str] = field(default_factory=Counter)
    finalized: bool = False
    final_file: Path | None = None
    error: str | None = None
    @property
    def checkpoint_file(self) -> Path:
        return self.output_dir / "checkpoints" / f"{safe_name(self.run_id)}_{safe_name(self.room_id)}.checkpoint.json"
    def ingest(self, payload: dict[str, Any]) -> None:
        status = payload.get("status")
        if isinstance(status, dict): self.latest_status = status
        events = payload.get("events") or []
        if not isinstance(events, list): return
        for ev in events:
            if not isinstance(ev, dict): continue
            kind = str(ev.get("kind") or "unknown"); self.event_counts[kind] += 1
            if kind == "t18_candidate_cycle" and len(self.t18_candidate_traces)<MAX_T18_CANDIDATE_TRACES: self.t18_candidate_traces.append(ev)
            elif kind == "t18_cycle" and len(self.t18_other_traces)<MAX_T18_OTHER_TRACES: self.t18_other_traces.append(ev)
            elif kind in ("t23_cycle","t23_a5888_cycle") and len(self.t23_traces)<MAX_T23_TRACES: self.t23_traces.append(ev)
            elif kind == "descriptor_attack_edge" and len(self.rare_edges)<MAX_RARE_EDGES: self.rare_edges.append(ev)
    def poll(self, now: float) -> None:
        if self.finalized or now-self.last_drain<DRAIN_INTERVAL: return
        self.last_drain = now; payload = self.session.evaluate("globalThis.__WOF052L_RECORDER ? globalThis.__WOF052L_RECORDER.drain() : null",timeout=5.0)
        if not isinstance(payload, dict) or payload.get("ok") is not True: raise CdpError("probe drain returned malformed/not-ok payload")
        self.ingest(payload)
    def checkpoint(self, now: float) -> None:
        if self.finalized or now-self.last_checkpoint<CHECKPOINT_INTERVAL: return
        self.last_checkpoint = now
        try:
            status = self.session.evaluate("globalThis.__WOF052L_RECORDER ? globalThis.__WOF052L_RECORDER.status() : null",timeout=5.0)
            if isinstance(status, dict): self.latest_status = status
        except CdpError: pass
        atomic_write_json(self.checkpoint_file,self.to_json(final=False,reason="checkpoint"))
    def to_json(self, *, final: bool, reason: str) -> dict[str, Any]:
        diag = self.latest_status.get("diagnostics") if isinstance(self.latest_status,dict) else {}
        return {"schema":SCHEMA_VERSION,"probeVersion":PROBE_VERSION,"runId":self.run_id,"roomId":self.room_id,"status":"complete" if final else "running","finalizationReason":reason if final else None,"startedAt":self.started_at,"finalizedAt":utc_iso() if final else None,"durationSeconds":round(time.monotonic()-self.started_monotonic,1),"target":{"targetId":self.target.get("targetId"),"type":self.target.get("type"),"url":self.target.get("url"),"openerId":self.target.get("openerId")},"page":{"targetId":self.page.get("targetId"),"url":self.page.get("url"),"title":self.page.get("title")} if self.page else None,"identity":self.bootstrap.get("identity") or self.latest_status.get("identity"),"safety":{"readOnly":True,"ramWrites":0,"inputInjection":False},"eventCounts":dict(self.event_counts),"diagnostics":diag or {},"t18":{"candidateSignature":CANDIDATE_SIG,"candidateTraces":self.t18_candidate_traces,"otherTraces":self.t18_other_traces,"candidateSequenceSummary":t18_sequence_summary(self.t18_candidate_traces),"traceCaps":{"candidate":MAX_T18_CANDIDATE_TRACES,"other":MAX_T18_OTHER_TRACES}},"t23":{"traces":self.t23_traces,"sequenceSummary":t23_sequence_summary(self.t23_traces),"knownA5888ResearchNote":"Preserve ordered T23 cycles, especially A5888 BODY4936 branch/tails; research-only.","traceCap":MAX_T23_TRACES},"rareDescriptorAttackEdges":self.rare_edges,"error":self.error}
    def finalize(self, reason: str, try_remote: bool = True) -> dict[str, Any]:
        if self.finalized: return self.to_json(final=True,reason=reason)
        if try_remote:
            try:
                payload = self.session.evaluate("globalThis.__WOF052L_RECORDER ? ({events:globalThis.__WOF052L_RECORDER.drain().events,status:globalThis.__WOF052L_RECORDER.stop()}) : null",timeout=6.0)
                if isinstance(payload,dict): self.ingest(payload)
            except Exception as exc: self.error = self.error or f"final remote drain unavailable: {exc}"
        data = self.to_json(final=True,reason=reason); filename = f"{local_stamp()}_{safe_name(self.room_id)}.json"; self.final_file = self.output_dir/"rooms"/filename; atomic_write_json(self.final_file,data); self.finalized = True
        try: self.checkpoint_file.unlink(missing_ok=True)
        except Exception: pass
        try: self.session.close()
        except Exception: pass
        return data


class RecorderManager:
    def __init__(self, output_dir: Path, args: argparse.Namespace):
        self.output_dir=output_dir; self.args=args; self.run_id=f"run-{local_stamp()}-{uuid.uuid4().hex[:8]}"; self.run_file=output_dir/"runs"/f"{safe_name(self.run_id)}_merged.json"; self.probe_js=Path(__file__).with_name("worker_probe.js").read_text(encoding="utf-8"); self.endpoint:BrowserEndpoint|None=None; self.client:CdpClient|None=None; self.live:dict[str,RoomCapture]={}; self.completed:list[dict[str,Any]]=[]; self.room_files:list[dict[str,Any]]=[]; self.retry_after:dict[str,float]={}; self.browser_process:subprocess.Popen[Any]|None=None; self._last_discovery=0.0; self._last_merge=0.0; self._announced_wait=False
    def ensure_browser(self) -> bool:
        if self.client and not self.client.closed: return True
        if self.client: self._browser_lost()
        ep = find_endpoint(self.args.cdp_host,self.args.cdp_port)
        if self.browser_process is not None and self.browser_process.poll() is not None: self.browser_process=None
        if not ep and not self.args.no_launch_browser and self.browser_process is None:
            port=self.args.cdp_port or 9223; proc=launch_debug_browser(self.args.browser,self.args.cdp_host,port,self.args.game_url)
            if proc:
                self.browser_process=proc; print(f"\nLaunched debug browser on {self.args.cdp_host}:{port}. Open WOF rooms in that browser."); deadline=time.monotonic()+8.0
                while time.monotonic()<deadline and not ep:
                    ep=probe_endpoint(self.args.cdp_host,port)
                    if not ep: time.sleep(0.2)
        if not ep:
            if not self._announced_wait: print("\nBrowser: WAITING for Chrome/Edge CDP. Recorder remains fail-open; game is untouched."); self._announced_wait=True
            return False
        client: CdpClient | None = None
        try:
            client=CdpClient(ep.websocket_url); client.connect(); client.targets()
        except Exception as exc:
            print(f"\nCDP connect failed: {exc}")
            if client: client.close()
            return False
        self.endpoint=ep; self.client=client; self._announced_wait=False; print(f"\nBrowser: OK — {ep.label}"); return True
    def _browser_lost(self) -> None:
        for tid in list(self.live): self._finalize_target(tid,"browser-cdp-disconnect",try_remote=False)
        if self.client: self.client.close()
        self.client=None; self.endpoint=None
    @staticmethod
    def _page_for_worker(worker:dict[str,Any],targets:list[dict[str,Any]])->dict[str,Any]|None:
        opener=worker.get("openerId")
        if not opener:return None
        return next((t for t in targets if t.get("targetId")==opener and t.get("type")=="page"),None)
    @staticmethod
    def _supported_worker(target:dict[str,Any])->bool:
        return target.get("type")=="worker" and bool(GSTYPHOON_RE.search(str(target.get("url") or "")))
    def _attach_new(self,target:dict[str,Any],targets:list[dict[str,Any]],now:float)->None:
        assert self.client is not None
        tid=str(target.get("targetId") or "")
        if not tid or tid in self.live or now<self.retry_after.get(tid,0):return
        opener=target.get("openerId")
        if opener and any(r.target.get("openerId")==opener for r in self.live.values()):self.retry_after[tid]=now+1.0;return
        session:CdpSession|None=None
        try:
            session=self.client.attach(tid);session.request("Runtime.enable",timeout=5.0);light=session.evaluate(LIGHT_PROBE,timeout=5.0)
            if not isinstance(light,dict) or light.get("moduleOk") is not True or light.get("ramWithinHeap") is not True:self.retry_after[tid]=now+2.0;session.close();return
            bootstrap=session.evaluate(self.probe_js,await_promise=True,timeout=45.0)
            if not isinstance(bootstrap,dict) or bootstrap.get("ok") is not True:
                reason=str((bootstrap or {}).get("reason") if isinstance(bootstrap,dict) else "malformed bootstrap");print(f"\nSkip worker {tid[:8]}: {reason}");self.retry_after[tid]=now+30.0;session.close();return
            ident=bootstrap.get("identity") or {}
            if ident.get("sha256")!=WORLD_SHA256:print(f"\nSkip worker {tid[:8]}: World SHA mismatch");self.retry_after[tid]=now+60.0;session.close();return
            room_id=f"room-{local_stamp()}-{safe_name(tid[:10])}";room=RoomCapture(run_id=self.run_id,room_id=room_id,target=dict(target),page=self._page_for_worker(target,targets),session=session,output_dir=self.output_dir,bootstrap=bootstrap,latest_status=bootstrap);self.live[tid]=room;print(f"\n+ Room {room_id} attached — exact World 921031 / READ ONLY")
        except Exception as exc:
            self.retry_after[tid]=now+3.0
            if session:session.close()
            print(f"\nAttach {tid[:8]} failed safely: {exc}")
    def discover(self,now:float)->None:
        if not self.client or now-self._last_discovery<DISCOVERY_INTERVAL:return
        self._last_discovery=now
        try:targets=self.client.targets()
        except Exception:self._browser_lost();return
        current={str(t.get("targetId")):t for t in targets if t.get("targetId")}
        for tid in list(self.live):
            if tid not in current:self._finalize_target(tid,"worker-closed-or-reloaded",try_remote=False)
        for target in targets:
            if self._supported_worker(target):self._attach_new(target,targets,now)
    def _finalize_target(self,tid:str,reason:str,try_remote:bool)->None:
        room=self.live.pop(tid,None)
        if not room:return
        data=room.finalize(reason,try_remote=try_remote);self.completed.append(data);self.room_files.append({"roomId":room.room_id,"file":str(room.final_file.relative_to(self.output_dir)) if room.final_file else None,"reason":reason,"startedAt":data["startedAt"],"finalizedAt":data["finalizedAt"]});diag=data.get("diagnostics") or {};print(f"\n- Room {room.room_id} finalized ({reason}) T18cand={((diag.get('t18') or {}).get('candidateCycles') or 0)}")
    def poll_rooms(self,now:float)->None:
        for tid,room in list(self.live.items()):
            try:room.poll(now);room.checkpoint(now)
            except Exception as exc:room.error=str(exc);self._finalize_target(tid,"worker-cdp-error",try_remote=False)
    def _all_records_for_merge(self)->list[dict[str,Any]]:
        return list(self.completed)+[r.to_json(final=False,reason="rolling-merge") for r in self.live.values()]
    def merged_payload(self,final:bool)->dict[str,Any]:
        records=self._all_records_for_merge();candidate_traces:list[dict[str,Any]]=[];t23_traces:list[dict[str,Any]]=[];type_samples:Counter[str]=Counter();active_freq:Counter[str]=Counter();player_hist=[0,0,0,0];target_samples:Counter[str]=Counter();scene_sets:Counter[str]=Counter();totals=Counter();room_rows=[]
        for rec in records:
            diag=rec.get("diagnostics") or {};t18=diag.get("t18") or {};t23=diag.get("t23") or {};totals["enemySamples"]+=int(diag.get("enemySamples") or 0);totals["activeEdges"]+=int(diag.get("activeEdges") or 0);totals["t18Samples"]+=int(t18.get("samples") or 0);totals["t18Cycles"]+=int(t18.get("resolvedCycles") or 0);totals["t18CandidateCycles"]+=int(t18.get("candidateCycles") or 0);totals["t18A4704"]+=int((t18.get("candidateAttackCounts") or {}).get("A4704") or 0);totals["t18A4712"]+=int((t18.get("candidateAttackCounts") or {}).get("A4712") or 0);totals["t23Samples"]+=int(t23.get("samples") or 0);totals["t23Cycles"]+=int(t23.get("resolvedCycles") or 0);totals["t23A5888"]+=int(t23.get("a5888Cycles") or 0);type_samples.update({k:int(v) for k,v in (diag.get("typeSamples") or {}).items()});active_freq.update({k:int(v) for k,v in (diag.get("activeAttackFrequency") or {}).items()});target_samples.update({k:int(v) for k,v in (diag.get("targetSamples") or {}).items()});scene_sets.update({k:int(v) for k,v in (diag.get("sceneTypeSets") or {}).items()});ph=diag.get("playerCountHist") or []
            for i in range(min(4,len(ph))):player_hist[i]+=int(ph[i] or 0)
            for tr in ((rec.get("t18") or {}).get("candidateTraces") or []):
                if len(candidate_traces)<2500:candidate_traces.append({"roomId":rec.get("roomId"),**tr})
            for tr in ((rec.get("t23") or {}).get("traces") or []):
                if len(t23_traces)<1200:t23_traces.append({"roomId":rec.get("roomId"),**tr})
            room_rows.append({"roomId":rec.get("roomId"),"status":rec.get("status"),"startedAt":rec.get("startedAt"),"finalizedAt":rec.get("finalizedAt"),"durationSeconds":rec.get("durationSeconds"),"finalizationReason":rec.get("finalizationReason"),"identitySha256":(rec.get("identity") or {}).get("sha256"),"t18Samples":int(t18.get("samples") or 0),"t18CandidateCycles":int(t18.get("candidateCycles") or 0),"t18CandidateAttacks":t18.get("candidateAttackCounts") or {},"t23Cycles":int(t23.get("resolvedCycles") or 0)})
        return {"schema":SCHEMA_VERSION,"runId":self.run_id,"status":"complete" if final else "running","updatedAt":utc_iso(),"saveFolder":str(self.output_dir),"browser":self.endpoint.label if self.endpoint else None,"safety":{"readOnly":True,"ramWrites":0,"inputInjection":False},"identityPolicy":{"required":"Warriors of Fate (World 921031)","sha256":WORLD_SHA256},"counts":{"liveRooms":len(self.live),"completedRooms":len(self.completed),**{k:int(v) for k,v in totals.items()}},"coverage":{"playerCountHist":player_hist,"targetSamples":dict(target_samples),"enemyTypeSamplesTop":top_map(type_samples,80),"activeAttackFrequencyTop":top_map(active_freq,120),"sceneTypeSetTop":top_map(scene_sets,100)},"t18CandidateSequenceSummary":t18_sequence_summary(candidate_traces),"t18CandidateEvidence":candidate_traces,"t23SequenceSummary":t23_sequence_summary(t23_traces),"roomFiles":list(self.room_files),"rooms":room_rows,"notes":{"t18":"BODY4728/A4/B2/TM1 is attack-ambiguous in WOF-051; ordered evidence remains research-only.","t23":"T23 ordered traces are opportunistic research evidence; no automatic product-rule promotion.","storage":"No full-frame long-duration RAM history is stored."}}
    def write_merged(self,final:bool=False)->None:atomic_write_json(self.run_file,self.merged_payload(final));self._last_merge=time.monotonic()
    def status_line(self)->str:
        records=self._all_records_for_merge();t18_samples=t18_candidates=a4704=a4712=t23=0
        for rec in records:
            diag=rec.get("diagnostics") or {};d18=diag.get("t18") or {};d23=diag.get("t23") or {};t18_samples+=int(d18.get("samples") or 0);t18_candidates+=int(d18.get("candidateCycles") or 0);a4704+=int((d18.get("candidateAttackCounts") or {}).get("A4704") or 0);a4712+=int((d18.get("candidateAttackCounts") or {}).get("A4712") or 0);t23+=int(d23.get("resolvedCycles") or 0)
        browser="OK" if self.client and not self.client.closed else "WAIT";return f"Browser {browser} | Live rooms {len(self.live)} | Completed {len(self.completed)} | T18 samples {t18_samples} | Candidate {t18_candidates} | A4704 {a4704} | A4712 {a4712} | T23 {t23} | READ ONLY / RAM writes 0"
    def shutdown(self)->None:
        for tid in list(self.live):self._finalize_target(tid,"recorder-stopped",try_remote=True)
        self.write_merged(final=True)
        if self.client:self.client.close()
        print(f"\nFinal merged JSON: {self.run_file}")
    def run(self)->None:
        print("WOF-052L Automatic Multi-Room Event Recorder");print(f"Save folder: {self.output_dir}");print(f"Run: {self.run_id}");print("Safety: READ ONLY / RAM writes 0 / no input injection");print("Press Ctrl+C to stop and write final merged JSON.\n");self.write_merged(False)
        try:
            while True:
                now=time.monotonic()
                if self.ensure_browser():self.discover(now);self.poll_rooms(now)
                if now-self._last_merge>=ROLLING_MERGE_INTERVAL:self.write_merged(False)
                print("\r"+self.status_line()[:180].ljust(180),end="",flush=True);time.sleep(0.15)
        except KeyboardInterrupt:print("\nStopping recorder...")
        finally:self.shutdown()


def run_self_test()->int:
    sig1=CANDIDATE_SIG;sig2a="S0/A6/B4|BODY4728|FE8b660|NX8b204|Vffff|TM2|P6C4736";sig2b="S0/A2/B0|BODY4728|FE8b660|NX8b204|Vffff|TM3|P6C4736";traces=[{"candidateSeen":True,"activeAttack":4704,"targetStable":True,"sideStable":True,"candidateFirstLeadMs":40.0,"candidateLastLeadMs":20.0,"candidateStateIndexes":[0],"states":[{"signature":sig1},{"signature":sig2a}]},{"candidateSeen":True,"activeAttack":4712,"targetStable":True,"sideStable":False,"candidateFirstLeadMs":120.0,"candidateLastLeadMs":100.0,"candidateStateIndexes":[0],"states":[{"signature":sig1},{"signature":sig2b}]}];summary=t18_sequence_summary(traces);assert summary["totalCycles"]==2;assert summary["byAttack"]["4704"]["cycles"]==1;assert summary["byAttack"]["4712"]["cycles"]==1;assert family_signature(sig2a).endswith("|TM*|P6C4736")
    with tempfile.TemporaryDirectory() as td:
        p=Path(td)/"x"/"test.json";atomic_write_json(p,{"readOnly":True,"ramWrites":0});assert json.loads(p.read_text(encoding="utf-8"))["ramWrites"]==0
    methods=set(READ_ONLY_METHODS);assert not any(x in methods for x in ("Input.dispatchKeyEvent","Runtime.callFunctionOn","Page.addScriptToEvaluateOnNewDocument"));probe=Path(__file__).with_name("worker_probe.js").read_text(encoding="utf-8");assert "HEAPU8[" not in probe and "HEAPU16[" not in probe;assert not re.search(r"HEAPU32\s*\[[^\]]+\]\s*=",probe);assert "setInterval(tick,INTERVAL_MS)" in probe;assert "DURATION=" not in probe;print("SELF-TEST PASS — WOF-052L recorder invariants and sequence aggregation");return 0


def build_parser()->argparse.ArgumentParser:
    p=argparse.ArgumentParser(description="WOF-052L automatic multi-room read-only event recorder");p.add_argument("--output-dir",help="Set and remember the JSON output directory");p.add_argument("--reset-output",action="store_true",help="Forget the remembered output directory and ask again");p.add_argument("--cdp-host",default="127.0.0.1");p.add_argument("--cdp-port",type=int,help="Preferred Chrome/Edge remote-debugging port (auto-scans common ports if omitted)");p.add_argument("--browser",choices=["auto","edge","chrome"],default="auto");p.add_argument("--no-launch-browser",action="store_true",help="Only attach to an already-running CDP browser");p.add_argument("--game-url",help="Optional URL to open if Recorder must launch a debug browser");p.add_argument("--self-test",action="store_true");return p


def main()->int:
    args=build_parser().parse_args()
    if args.self_test:return run_self_test()
    output_dir=resolve_output_dir(args.output_dir,args.reset_output);RecorderManager(output_dir,args).run();return 0


if __name__=="__main__":raise SystemExit(main())
