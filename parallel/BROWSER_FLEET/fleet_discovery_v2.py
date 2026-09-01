from __future__ import annotations

import re
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
PYLAUNCH_DIR = HERE.parent / "PYLAUNCH"
if str(PYLAUNCH_DIR) not in sys.path:
    sys.path.insert(0, str(PYLAUNCH_DIR))

from wof_launcher.cdp import CdpClient, CdpError, CdpSession


WORKER_TYPES = {"worker", "shared_worker", "service_worker"}
RECURSE_TARGET_TYPES = {"iframe", "worker", "shared_worker", "service_worker"}
WOF_HINT_RE = re.compile(r"\bwof\b|warriors.?of.?fate|gstyphoon", re.I)

# Cheap indicator only: this checks Emscripten heap shape and never hashes ROM data.
LIGHT_RUNTIME_PROBE = r"""(()=>{
'use strict';
const good=v=>!!(v&&v.HEAPU8 instanceof Uint8Array&&v.HEAPU32 instanceof Uint32Array&&v.HEAPU8.buffer===v.HEAPU32.buffer);
let mod=null,key=null;
try{if(good(self._0x515056)){mod=self._0x515056;key='_0x515056';}}catch(_){}
if(!mod){
  for(const k of Object.getOwnPropertyNames(self)){
    let v;try{v=self[k];}catch(_){continue;}
    if(good(v)){mod=v;key=k;break;}
  }
}
return {
  moduleOk:!!mod,
  moduleKey:key,
  heapOk:!!(mod&&mod.HEAPU8 instanceof Uint8Array),
  heapBytes:mod&&mod.HEAPU8?mod.HEAPU8.length:null,
  href:(()=>{try{return String(self.location&&self.location.href||'');}catch(_){return '';}})(),
  readOnly:true,
  ramWrites:0,
  inputInjection:false
};
})()"""

PAGE_PROBE = r"""(()=>({
  href:String(location.href),
  title:String(document.title||''),
  gameSurface:!!(window.I_GF1TC&&window.I_fdC8Q&&typeof window.I_fdC8Q.drawArrays==='function'),
  alphaBootstrap:!!(window.__WOF_ALPHA_BOOTSTRAP_RC5||window.__WOF_ALPHA_BOOTSTRAP_RC3),
  readOnly:true,
  ramWrites:0,
  inputInjection:false
}))()"""


@dataclass(frozen=True)
class FleetDiscoveryResult:
    page_ok: bool
    page_count: int
    worker_ok: bool
    worker_count: int
    path: str
    reason: str | None = None
    topology_count: int = 0


def _target_id(target: dict[str, Any]) -> str:
    return str(target.get("targetId") or "")


def _url(target: dict[str, Any]) -> str:
    return str(target.get("url") or "")


def _is_page(target: dict[str, Any]) -> bool:
    return target.get("type") == "page" and _url(target) not in {"", "about:blank"}


def _has_wof_hint(target: dict[str, Any]) -> bool:
    text = f"{target.get('url') or ''} {target.get('title') or ''} {target.get('name') or ''}"
    return bool(WOF_HINT_RE.search(text))


def _worker_like(target: dict[str, Any]) -> bool:
    return target.get("type") in WORKER_TYPES


def _evaluate(session: CdpSession, expression: str) -> dict[str, Any]:
    session.request("Runtime.enable")
    value = session.evaluate(expression, timeout=2.0)
    return value if isinstance(value, dict) else {}


def _probe_page(client: CdpClient, target: dict[str, Any]) -> dict[str, Any]:
    target_id = _target_id(target)
    if not target_id:
        return {}
    session: CdpSession | None = None
    try:
        session = client.attach(target_id)
        return _evaluate(session, PAGE_PROBE)
    except CdpError:
        return {}
    finally:
        if session:
            session.close()


def _probe_worker_session(session: CdpSession) -> dict[str, Any]:
    try:
        return _evaluate(session, LIGHT_RUNTIME_PROBE)
    except CdpError as exc:
        return {
            "moduleOk": False,
            "reason": str(exc),
            "readOnly": True,
            "ramWrites": 0,
            "inputInjection": False,
        }


def _candidate_is_positive(target: dict[str, Any], probe: dict[str, Any], *, related: bool) -> bool:
    if probe.get("moduleOk") is True:
        return True
    if _has_wof_hint(target) and _worker_like(target):
        return True
    return False


def _page_is_positive(target: dict[str, Any], probe: dict[str, Any]) -> bool:
    if probe.get("gameSurface") is True or probe.get("alphaBootstrap") is True:
        return True
    href = str(probe.get("href") or "")
    title = str(probe.get("title") or "")
    return _has_wof_hint(target) or bool(WOF_HINT_RE.search(f"{href} {title}"))


def _related_workers(
    client: CdpClient,
    page: dict[str, Any],
    *,
    settle_seconds: float,
    max_depth: int = 3,
) -> tuple[list[tuple[dict[str, Any], dict[str, Any]]], int]:
    root: CdpSession | None = None
    sessions: dict[str, tuple[CdpSession, int]] = {}
    rows: list[tuple[dict[str, Any], dict[str, Any]]] = []
    seen: set[str] = set()
    topology_count = 0
    try:
        root = client.attach(_target_id(page))
        sessions[root.session_id] = (root, 0)
        cursor = client.event_cursor()
        root.request(
            "Target.setAutoAttach",
            {"autoAttach": True, "waitForDebuggerOnStart": False, "flatten": True},
        )
        deadline = time.monotonic() + max(0.0, settle_seconds)
        while time.monotonic() < deadline and len(sessions) < 48:
            cursor, events = client.wait_for_events(
                cursor,
                timeout=min(0.08, max(0.0, deadline - time.monotonic())),
                predicate=lambda event: event.get("method") == "Target.attachedToTarget",
            )
            if not events:
                continue
            for event in events:
                parent_sid = str(event.get("sessionId") or "")
                parent = sessions.get(parent_sid)
                params = event.get("params") if isinstance(event.get("params"), dict) else {}
                child_sid = str(params.get("sessionId") or "")
                info = params.get("targetInfo")
                if not parent or not child_sid or not isinstance(info, dict):
                    continue
                depth = parent[1] + 1
                target_id = _target_id(info)
                child = CdpSession(client, target_id, child_sid)
                sessions[child_sid] = (child, depth)
                topology_count += 1
                if _worker_like(info) and target_id and target_id not in seen:
                    seen.add(target_id)
                    rows.append((dict(info), _probe_worker_session(child)))
                if depth < max_depth and info.get("type") in RECURSE_TARGET_TYPES:
                    try:
                        child.request(
                            "Target.setAutoAttach",
                            {"autoAttach": True, "waitForDebuggerOnStart": False, "flatten": True},
                        )
                    except CdpError:
                        pass
        return rows, topology_count
    finally:
        if root:
            root.close()


def discover_fleet_status(
    client: CdpClient,
    *,
    settle_seconds: float = 0.24,
) -> FleetDiscoveryResult:
    raw = client.request("Target.getTargets").get("targetInfos") or []
    if not isinstance(raw, list):
        raise CdpError("Target.getTargets returned malformed targetInfos")
    targets = [dict(item) for item in raw if isinstance(item, dict)]
    pages = [target for target in targets if _is_page(target)]

    positive_page_ids: set[str] = set()
    for page in pages:
        probe = _probe_page(client, page)
        if _page_is_positive(page, probe):
            positive_page_ids.add(_target_id(page))

    related_positive: dict[str, tuple[dict[str, Any], dict[str, Any]]] = {}
    topology_count = 0
    for page in pages:
        try:
            rows, count = _related_workers(client, page, settle_seconds=settle_seconds)
        except CdpError:
            continue
        topology_count += count
        for target, probe in rows:
            target_id = _target_id(target)
            if target_id and _candidate_is_positive(target, probe, related=True):
                related_positive[target_id] = (target, probe)
                positive_page_ids.add(_target_id(page))

    if related_positive:
        module_count = sum(1 for _, probe in related_positive.values() if probe.get("moduleOk") is True)
        path = "page-autoattach-module" if module_count else "page-autoattach-url-hint"
        return FleetDiscoveryResult(
            page_ok=True,
            page_count=max(1, len(positive_page_ids)),
            worker_ok=True,
            worker_count=len(related_positive),
            path=path,
            topology_count=topology_count,
        )

    direct_positive: dict[str, tuple[dict[str, Any], dict[str, Any]]] = {}
    for target in targets:
        if not _worker_like(target):
            continue
        target_id = _target_id(target)
        if not target_id:
            continue
        session: CdpSession | None = None
        try:
            session = client.attach(target_id)
            probe = _probe_worker_session(session)
        except CdpError:
            probe = {}
        finally:
            if session:
                session.close()
        if _candidate_is_positive(target, probe, related=False):
            direct_positive[target_id] = (target, probe)

    if direct_positive:
        page_count = len(positive_page_ids)
        if page_count == 0 and len(pages) == 1:
            page_count = 1
        if page_count:
            module_count = sum(1 for _, probe in direct_positive.values() if probe.get("moduleOk") is True)
            path = "direct-worker-module" if module_count else "direct-worker-url-hint"
            return FleetDiscoveryResult(
                page_ok=True,
                page_count=page_count,
                worker_ok=True,
                worker_count=len(direct_positive),
                path=path,
                topology_count=topology_count,
            )

    page_count = len(positive_page_ids)
    if page_count == 0 and len(pages) == 1:
        page_count = 1
    if page_count:
        return FleetDiscoveryResult(
            page_ok=True,
            page_count=page_count,
            worker_ok=False,
            worker_count=0,
            path="page-only",
            reason="WOF 页面已找到；相关 Worker 尚未发现。",
            topology_count=topology_count,
        )
    return FleetDiscoveryResult(
        page_ok=False,
        page_count=0,
        worker_ok=False,
        worker_count=0,
        path="no-page",
        reason="尚未发现 WOF 页面或相关 Worker。",
        topology_count=topology_count,
    )
