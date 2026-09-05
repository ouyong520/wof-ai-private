from __future__ import annotations

import re
import time
from dataclasses import dataclass
from typing import Any
from urllib.parse import urlsplit

from .cdp import CdpClient, CdpError, CdpSession
from .probe import GSTYPHOON_RE, LIGHT_WORKER_PROBE, PAGE_PROBE
from .probe_v2 import IDENTITY_PROBE

WORKER_TYPES = {"worker", "shared_worker", "service_worker"}
WOF_HINT_RE = re.compile(r"\bwof\b|warriors.?of.?fate", re.I)
_TARGET_IDENTITY_KEYS = (
    "targetId",
    "type",
    "url",
    "title",
    "attached",
    "parentId",
    "openerId",
    "parentFrameId",
    "browserContextId",
    "subtype",
)


@dataclass(frozen=True)
class TargetChoice:
    page: dict[str, Any] | None
    worker: dict[str, Any] | None
    worker_probe: dict[str, Any] | None
    identity: dict[str, Any] | None
    reason: str | None = None
    diagnostics: dict[str, Any] | None = None


def _summary(t: dict[str, Any]) -> dict[str, Any]:
    return {k: t.get(k) for k in _TARGET_IDENTITY_KEYS if t.get(k) not in (None, "")}


def _url_scheme_hint(t: dict[str, Any]) -> str:
    url = str(t.get("url") or "")
    try:
        scheme = urlsplit(url).scheme.lower()
    except ValueError:
        scheme = ""
    return scheme or "none"


def _worker_compatible(t: dict[str, Any], *, related: bool = False) -> bool:
    # Discovery V2 observes already-existing attachable Worker targets. URL shape is
    # diagnostic only; runtime readiness + exact World identity are the authority.
    if t.get("type") in WORKER_TYPES:
        return True
    return related and bool(GSTYPHOON_RE.search(str(t.get("url") or "")))


def _deduplicate_targets(raw: list[Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[str]]:
    by_id: dict[str, dict[str, Any]] = {}
    rejected: list[dict[str, Any]] = []
    conflicts: set[str] = set()
    for item in raw:
        if not isinstance(item, dict):
            rejected.append({"reason": "malformed-target-info"})
            continue
        target = dict(item)
        tid = str(target.get("targetId") or "")
        if not tid:
            rejected.append({"reason": "missing-targetId", "target": _summary(target)})
            continue
        if tid in conflicts:
            rejected.append({"targetId": tid, "reason": "conflicting-duplicate-targetId", "target": _summary(target)})
            continue
        previous = by_id.get(tid)
        if previous is None:
            by_id[tid] = target
            continue
        if _summary(previous) == _summary(target):
            rejected.append({"targetId": tid, "reason": "duplicate-targetId-identical"})
            continue
        conflicts.add(tid)
        by_id.pop(tid, None)
        rejected.append(
            {
                "targetId": tid,
                "reason": "conflicting-duplicate-targetId",
                "first": _summary(previous),
                "second": _summary(target),
            }
        )
    targets = sorted(by_id.values(), key=lambda t: (str(t.get("type") or ""), str(t.get("targetId") or "")))
    return targets, rejected, sorted(conflicts)


def _eval(session: CdpSession, expression: str, *, await_promise: bool = False, timeout: float = 8.0) -> Any:
    session.request("Runtime.enable")
    return session.evaluate(expression, await_promise=await_promise, timeout=timeout)


def _probe_target(client: CdpClient, target_id: str, expression: str, *, await_promise: bool = False, timeout: float = 8.0) -> Any:
    session = client.attach(target_id)
    try:
        return _eval(session, expression, await_promise=await_promise, timeout=timeout)
    finally:
        session.close()


def _frame_ids_from_tree(result: dict[str, Any]) -> list[str]:
    frame_ids: set[str] = set()

    def walk(node: Any) -> None:
        if not isinstance(node, dict):
            return
        frame = node.get("frame")
        if isinstance(frame, dict):
            frame_id = frame.get("id")
            if isinstance(frame_id, str) and frame_id:
                frame_ids.add(frame_id)
        children = node.get("childFrames")
        if isinstance(children, list):
            for child in children:
                walk(child)

    walk(result.get("frameTree"))
    return sorted(frame_ids)


def _probe_page(client: CdpClient, t: dict[str, Any]) -> dict[str, Any]:
    out = dict(t)
    session: CdpSession | None = None
    try:
        session = client.attach(str(t.get("targetId") or ""))
        out["cdpPageReachable"] = True
        try:
            value = _eval(session, PAGE_PROBE)
            if isinstance(value, dict):
                out["wofPageProbe"] = value
        except CdpError as exc:
            out["pageProbeError"] = str(exc)
        try:
            frame_ids = _frame_ids_from_tree(session.request("Page.getFrameTree"))
            if frame_ids:
                out["cdpFrameIds"] = frame_ids
        except CdpError as exc:
            out["frameIdentityError"] = str(exc)
    except CdpError as exc:
        out["cdpPageReachable"] = False
        out["pageProbeError"] = str(exc)
        out["frameIdentityError"] = str(exc)
    finally:
        if session:
            session.close()
    return out


def _page_score(p: dict[str, Any]) -> int:
    q = p.get("wofPageProbe") if isinstance(p.get("wofPageProbe"), dict) else {}
    if q.get("gameSurface") is True:
        return 100
    text = f"{p.get('url') or ''} {p.get('title') or ''} {q.get('href') or ''} {q.get('title') or ''}"
    if WOF_HINT_RE.search(text):
        return 50
    if q.get("alphaBootstrap") is True:
        return 25
    return 0


def _unique_page(pages: list[dict[str, Any]]) -> dict[str, Any] | None:
    if len(pages) == 1:
        return pages[0]
    # With multiple live pages, only the runtime page probe is selection authority.
    # URL/title/alpha-bootstrap hints remain diagnostics and must never break a tie.
    game_pages = [
        page
        for page in pages
        if isinstance(page.get("wofPageProbe"), dict) and page["wofPageProbe"].get("gameSurface") is True
    ]
    return game_pages[0] if len(game_pages) == 1 else None


def _unique_wof_page(pages: list[dict[str, Any]]) -> dict[str, Any] | None:
    # Backward-compatible helper name with strict P31 semantics.
    return _unique_page(pages)


def _identity_on_session(session: CdpSession, target_id: str, *, timeout: float, cache: dict[str, dict[str, Any]] | None) -> dict[str, Any]:
    cached = cache.get(target_id) if cache else None
    if isinstance(cached, dict):
        return cached
    try:
        value = _eval(session, IDENTITY_PROBE, await_promise=True, timeout=timeout)
        identity = value if isinstance(value, dict) else {"ok": False, "reason": "identity probe returned malformed value"}
    except CdpError as exc:
        identity = {"ok": False, "reason": str(exc)}
    identity.setdefault("readOnly", True)
    identity.setdefault("ramWrites", 0)
    identity.setdefault("inputInjection", False)
    sha = identity.get("sha256")
    if cache is not None and isinstance(sha, str) and re.fullmatch(r"[0-9a-f]{64}", sha):
        cache[target_id] = identity
    return identity


def _probe_worker_session(session: CdpSession, t: dict[str, Any], *, identity_timeout: float, cache: dict[str, dict[str, Any]] | None) -> tuple[dict[str, Any], dict[str, Any] | None]:
    try:
        value = _eval(session, LIGHT_WORKER_PROBE)
        light = value if isinstance(value, dict) else {}
    except CdpError as exc:
        light = {"moduleOk": False, "reason": str(exc), "readOnly": True, "ramWrites": 0, "inputInjection": False}
    identity = None
    if light.get("moduleOk") is True:
        identity = _identity_on_session(session, str(t.get("targetId") or ""), timeout=identity_timeout, cache=cache)
    return light, identity


def _related_rows(client: CdpClient, page: dict[str, Any], *, identity_timeout: float, cache: dict[str, dict[str, Any]] | None) -> tuple[list[tuple[dict[str, Any], dict[str, Any], dict[str, Any] | None]], list[dict[str, Any]]]:
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
        deadline = time.monotonic() + 0.9
        while time.monotonic() < deadline and len(sessions) < 24:
            cursor, events = client.wait_for_events(cursor, timeout=min(0.18, max(0.0, deadline - time.monotonic())), predicate=lambda e: e.get("method") == "Target.attachedToTarget")
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
                topology.append({**_summary(info), "depth": depth, "attachedFromTargetId": parent[0].target_id, "urlSchemeHint": _url_scheme_hint(info)})
                child = CdpSession(client, tid, child_sid)
                sessions[child_sid] = (child, depth)
                if _worker_compatible(info, related=True) and tid and tid not in seen_targets:
                    seen_targets.add(tid)
                    light, identity = _probe_worker_session(child, info, identity_timeout=identity_timeout, cache=cache)
                    rows.append((dict(info), light, identity))
                if depth < 2 and info.get("type") in {"iframe", "worker", "shared_worker"}:
                    try:
                        child.request("Target.setAutoAttach", {"autoAttach": True, "waitForDebuggerOnStart": False, "flatten": True})
                    except CdpError:
                        pass
        return rows, topology
    finally:
        if root:
            root.close()


def _page_frame_ids(page: dict[str, Any]) -> set[str]:
    frame_ids: set[str] = set()
    probe = page.get("wofPageProbe") if isinstance(page.get("wofPageProbe"), dict) else {}
    for candidate in (page.get("frameId"), probe.get("frameId")):
        if isinstance(candidate, str) and candidate:
            frame_ids.add(candidate)
    cdp_frame_ids = page.get("cdpFrameIds")
    if isinstance(cdp_frame_ids, (list, tuple, set)):
        frame_ids.update(frame_id for frame_id in cdp_frame_ids if isinstance(frame_id, str) and frame_id)
    return frame_ids


def _direct_page(worker: dict[str, Any], pages: list[dict[str, Any]]) -> dict[str, Any] | None:
    explicit_links: list[dict[str, Any]] = []

    parent_id = worker.get("parentId")
    if parent_id:
        linked = [p for p in pages if p.get("targetId") == parent_id]
        if len(linked) != 1:
            return None
        explicit_links.append(linked[0])

    parent_frame_id = worker.get("parentFrameId")
    if parent_frame_id:
        linked = [page for page in pages if parent_frame_id in _page_frame_ids(page)]
        if len(linked) != 1:
            return None
        explicit_links.append(linked[0])

    if explicit_links:
        linked_ids = {str(page.get("targetId") or "") for page in explicit_links}
        return explicit_links[0] if len(linked_ids) == 1 else None

    # Browser context is runtime scoping evidence. It may narrow the candidate set,
    # but if more than one page remains only the gameSurface probe may select one.
    browser_context_id = worker.get("browserContextId")
    if browser_context_id:
        contextual = [page for page in pages if page.get("browserContextId") == browser_context_id]
        if not contextual:
            return None
        return _unique_page(contextual)

    # openerId is intentionally not parent authority for Worker targets.
    return _unique_page(pages)


def _diag(
    targets: list[dict[str, Any]],
    pages: list[dict[str, Any]],
    *,
    path: str,
    topology: list[dict[str, Any]] | None = None,
    rejected: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    counts: dict[str, int] = {}
    for t in targets:
        kind = str(t.get("type") or "unknown")
        counts[kind] = counts.get(kind, 0) + 1
    workers = [t for t in targets if t.get("type") in WORKER_TYPES]
    return {
        "path": path,
        "targetCount": len(targets),
        "typeCounts": counts,
        "targets": [_summary(t) for t in targets[:32]],
        "workerUrlHints": [{"targetId": t.get("targetId"), "scheme": _url_scheme_hint(t), "url": t.get("url")} for t in workers[:32]],
        "pageSignals": [
            {
                "targetId": p.get("targetId"),
                "score": _page_score(p),
                "url": p.get("url"),
                "probe": p.get("wofPageProbe"),
                "frameIds": sorted(_page_frame_ids(p)),
                "frameIdentityError": p.get("frameIdentityError"),
                "cdpPageReachable": p.get("cdpPageReachable"),
            }
            for p in pages
        ],
        "rejectedTargets": rejected or [],
        "relatedTopology": topology or [],
        "readOnly": True,
        "ramWrites": 0,
        "inputInjection": False,
        "workerReplacement": False,
        "urlRewrite": False,
    }


def discover(client: CdpClient, *, identity_timeout: float = 20.0, identity_cache: dict[str, dict[str, Any]] | None = None) -> TargetChoice:
    # Exact identity authority is valid only inside this discovery generation. A
    # targetId is not a browser/runtime/execution-context generation token, so an
    # external cache may retain this generation's result for diagnostics but must
    # never carry accepted identity authority into the next discover() call.
    if identity_cache is not None:
        identity_cache.clear()

    raw = client.request("Target.getTargets").get("targetInfos") or []
    if not isinstance(raw, list):
        raise CdpError("Target.getTargets returned malformed targetInfos")

    targets, rejected, conflicts = _deduplicate_targets(raw)
    if conflicts:
        reason = f"conflicting duplicate CDP target identities: {', '.join(conflicts)}"
        return TargetChoice(None, None, None, None, reason, _diag(targets, [], path="target-identity-conflict", rejected=rejected))

    probed_pages = [_probe_page(client, t) for t in targets if t.get("type") == "page"]
    pages: list[dict[str, Any]] = []
    for page in probed_pages:
        if page.get("cdpPageReachable") is True:
            pages.append(page)
        else:
            rejected.append(
                {
                    "targetId": page.get("targetId"),
                    "type": "page",
                    "reason": "stale-or-unattachable-page-target",
                    "detail": page.get("pageProbeError"),
                }
            )

    supported: list[tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]] = []
    incomplete: list[tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any] | None]] = []
    all_topology: list[dict[str, Any]] = []
    for page in pages:
        rows, topology = _related_rows(client, page, identity_timeout=identity_timeout, cache=identity_cache)
        all_topology.extend(topology)
        if len(rows) == 1:
            w, light, identity = rows[0]
            incomplete.append((page, w, light, identity))
        for w, light, identity in rows:
            if light.get("moduleOk") is True and identity and identity.get("ok") is True:
                supported.append((page, w, light, identity))

    if len(supported) == 1:
        p, w, light, identity = supported[0]
        return TargetChoice(p, w, light, identity, None, _diag(targets, pages, path="page-autoattach", topology=all_topology, rejected=rejected))
    if len(supported) > 1:
        return TargetChoice(None, None, None, None, f"ambiguous page/Worker World 921031 pairs: {len(supported)}", _diag(targets, pages, path="page-autoattach-ambiguous", topology=all_topology, rejected=rejected))
    if len(incomplete) == 1:
        p, w, light, identity = incomplete[0]
        reason = "related WOF Worker found; WASM module/heap not ready" if light.get("moduleOk") is not True else str((identity or {}).get("reason") or "World 921031 identity not accepted")
        return TargetChoice(p, w, light, identity, reason, _diag(targets, pages, path="page-autoattach-incomplete", topology=all_topology, rejected=rejected))

    direct_rows: list[tuple[dict[str, Any], dict[str, Any], dict[str, Any] | None]] = []
    for worker in [t for t in targets if _worker_compatible(t)]:
        tid = str(worker.get("targetId") or "")
        if not tid:
            continue
        try:
            session = client.attach(tid)
            try:
                light, identity = _probe_worker_session(session, worker, identity_timeout=identity_timeout, cache=identity_cache)
            finally:
                session.close()
        except CdpError as exc:
            rejected.append(
                {
                    "targetId": tid,
                    "type": worker.get("type"),
                    "reason": "stale-or-unattachable-worker-target",
                    "detail": str(exc),
                }
            )
            continue
        direct_rows.append((worker, light, identity))

    good = [(w, l, i) for w, l, i in direct_rows if l.get("moduleOk") is True and i and i.get("ok") is True]
    if len(good) == 1:
        w, light, identity = good[0]
        p = _direct_page(w, pages)
        if p:
            return TargetChoice(p, w, light, identity, None, _diag(targets, pages, path="direct-worker", topology=all_topology, rejected=rejected))
        return TargetChoice(None, None, None, None, "supported direct Worker found but WOF page association is ambiguous or lacks authoritative runtime linkage", _diag(targets, pages, path="direct-worker-page-ambiguous", topology=all_topology, rejected=rejected))
    if len(good) > 1:
        return TargetChoice(None, None, None, None, f"ambiguous supported WOF workers: {len(good)}", _diag(targets, pages, path="direct-worker-ambiguous", topology=all_topology, rejected=rejected))

    page = _unique_page(pages)
    if page and len(direct_rows) == 1:
        w, light, identity = direct_rows[0]
        reason = "direct Worker found; WASM module/heap not ready" if light.get("moduleOk") is not True else str((identity or {}).get("reason") or "World 921031 identity not accepted")
        return TargetChoice(page, w, light, identity, reason, _diag(targets, pages, path="direct-worker-incomplete", topology=all_topology, rejected=rejected))
    if page:
        return TargetChoice(page, None, None, None, "WOF page found; related game Worker not yet discovered", _diag(targets, pages, path="page-only", topology=all_topology, rejected=rejected))
    if pages:
        return TargetChoice(None, None, None, None, f"WOF page association ambiguous: {len(pages)} live page targets; no unique runtime authority", _diag(targets, pages, path="page-ambiguous", topology=all_topology, rejected=rejected))
    return TargetChoice(None, None, None, None, "no live WOF page target discovered", _diag(targets, pages, path="no-page", topology=all_topology, rejected=rejected))
