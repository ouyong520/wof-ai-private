from __future__ import annotations

import time
from typing import Any

from .cdp import CdpClient, CdpError, CdpSession
from .discovery_v2 import (
    TargetChoice,
    _diag,
    _probe_page,
    _probe_worker_session,
    _summary,
    _url_scheme_hint,
    _worker_compatible,
)


MAX_DEPTH = 6
MAX_SESSIONS = 48
ATTACH_WINDOW_SECONDS = 1.4


def _deep_related_rows(client: CdpClient, page: dict[str, Any], *, identity_timeout: float, cache: dict[str, dict[str, Any]] | None) -> tuple[list[tuple[dict[str, Any], dict[str, Any], dict[str, Any] | None]], list[dict[str, Any]]]:
    root: CdpSession | None = None
    rows: list[tuple[dict[str, Any], dict[str, Any], dict[str, Any] | None]] = []
    topology: list[dict[str, Any]] = []
    sessions: dict[str, tuple[CdpSession, int]] = {}
    seen_targets: set[str] = set()
    try:
        root = client.attach(str(page.get("targetId") or ""))
        sessions[root.session_id] = (root, 0)
        cursor = client.event_cursor()
        root.request("Target.setAutoAttach", {"autoAttach": True, "waitForDebuggerOnStart": False, "flatten": True})
        deadline = time.monotonic() + ATTACH_WINDOW_SECONDS
        while time.monotonic() < deadline and len(sessions) < MAX_SESSIONS:
            cursor, events = client.wait_for_events(
                cursor,
                timeout=min(0.18, max(0.0, deadline - time.monotonic())),
                predicate=lambda e: e.get("method") == "Target.attachedToTarget",
            )
            if not events:
                continue
            for event in events:
                parent_sid = str(event.get("sessionId") or "")
                parent = sessions.get(parent_sid)
                params = event.get("params") or {}
                child_sid = str(params.get("sessionId") or "")
                info = params.get("targetInfo")
                if not parent or not child_sid or not isinstance(info, dict):
                    continue
                depth = parent[1] + 1
                tid = str(info.get("targetId") or "")
                topology.append({
                    **_summary(info),
                    "depth": depth,
                    "attachedFromTargetId": parent[0].target_id,
                    "urlSchemeHint": _url_scheme_hint(info),
                    "reentryTraversal": True,
                })
                child = CdpSession(client, tid, child_sid)
                sessions[child_sid] = (child, depth)
                if _worker_compatible(info, related=True) and tid and tid not in seen_targets:
                    seen_targets.add(tid)
                    light, identity = _probe_worker_session(child, info, identity_timeout=identity_timeout, cache=cache)
                    rows.append((dict(info), light, identity))
                if depth < MAX_DEPTH and info.get("type") in {"iframe", "worker", "shared_worker", "service_worker"}:
                    try:
                        child.request("Target.setAutoAttach", {"autoAttach": True, "waitForDebuggerOnStart": False, "flatten": True})
                    except CdpError:
                        pass
        return rows, topology
    finally:
        if root:
            root.close()


def recover_page_only(client: CdpClient, base: TargetChoice, *, identity_timeout: float = 20.0, identity_cache: dict[str, dict[str, Any]] | None = None) -> TargetChoice:
    diag = base.diagnostics if isinstance(base.diagnostics, dict) else {}
    if diag.get("path") not in {"page-only", "page-autoattach-incomplete", "direct-worker-incomplete"}:
        return base
    raw = client.request("Target.getTargets").get("targetInfos") or []
    if not isinstance(raw, list):
        return base
    targets = [dict(t) for t in raw if isinstance(t, dict)]
    pages = [_probe_page(client, t) for t in targets if t.get("type") == "page"]
    supported: list[tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]] = []
    incomplete: list[tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any] | None]] = []
    topology: list[dict[str, Any]] = []
    for page in pages:
        rows, rows_topology = _deep_related_rows(client, page, identity_timeout=identity_timeout, cache=identity_cache)
        topology.extend(rows_topology)
        for worker, light, identity in rows:
            if light.get("moduleOk") is True and identity and identity.get("ok") is True:
                supported.append((page, worker, light, identity))
            else:
                incomplete.append((page, worker, light, identity))
    if len(supported) == 1:
        page, worker, light, identity = supported[0]
        out_diag = _diag(targets, pages, path="reentry-deep-autoattach", topology=topology)
        out_diag.update({"reentryRecovery": True, "maxDepth": MAX_DEPTH, "maxSessions": MAX_SESSIONS, "attachWindowSeconds": ATTACH_WINDOW_SECONDS, "fullIdentityScan": True})
        return TargetChoice(page, worker, light, identity, None, out_diag)
    if len(supported) > 1:
        out_diag = _diag(targets, pages, path="reentry-deep-ambiguous", topology=topology)
        out_diag.update({"reentryRecovery": True, "maxDepth": MAX_DEPTH})
        return TargetChoice(None, None, None, None, f"ambiguous re-entry page/Worker World 921031 pairs: {len(supported)}", out_diag)
    if len(incomplete) == 1:
        page, worker, light, identity = incomplete[0]
        reason = "re-entry Worker found; WASM module/heap not ready" if light.get("moduleOk") is not True else str((identity or {}).get("reason") or "World 921031 identity not accepted")
        out_diag = _diag(targets, pages, path="reentry-deep-incomplete", topology=topology)
        out_diag.update({"reentryRecovery": True, "maxDepth": MAX_DEPTH})
        return TargetChoice(page, worker, light, identity, reason, out_diag)
    out_diag = dict(diag)
    out_diag.update({"reentryRecoveryAttempted": True, "reentryRecoveryFound": False, "maxDepth": MAX_DEPTH, "maxSessions": MAX_SESSIONS})
    return TargetChoice(base.page, base.worker, base.worker_probe, base.identity, base.reason, out_diag)
