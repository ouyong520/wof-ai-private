from __future__ import annotations

import json
import re
import threading
import time
from dataclasses import dataclass, field
from typing import Any, Callable

DISCOVERY_VERSION = "wof-prospective-discovery-v2"
WORKER_TYPES = {"worker", "shared_worker", "service_worker"}
RELATED_CONTAINER_TYPES = {"iframe", "worker", "shared_worker", "service_worker"}
WOF_URL_HINT_RE = re.compile(r"gstyphoon|\bwof\b|warriors.?of.?fate", re.I)
AUTOATTACH_WINDOW_SECONDS = 0.9
MAX_RELATED_SESSIONS = 48
MAX_RELATED_DEPTH = 3
MAX_EVENT_ROWS = 512
DISCOVERY_CDP_METHODS = {
    "Target.getTargets",
    "Target.attachToTarget",
    "Target.detachFromTarget",
    "Target.setAutoAttach",
    "Runtime.enable",
    "Runtime.evaluate",
}


@dataclass
class Candidate:
    page: dict[str, Any]
    target: dict[str, Any]
    session: Any
    owner_sessions: list[Any] = field(default_factory=list)
    path: str = "page-autoattach"
    light: dict[str, Any] = field(default_factory=dict)
    identity: dict[str, Any] = field(default_factory=dict)

    def close(self) -> None:
        seen: set[int] = set()
        for session in [self.session, *reversed(self.owner_sessions)]:
            if session is None or id(session) in seen:
                continue
            seen.add(id(session))
            try:
                session.close()
            except Exception:
                pass


class OwnedSession:
    """Keep a discovered Worker and the auto-attach ancestry alive as one room session."""

    def __init__(self, worker_session: Any, owner_sessions: list[Any] | None = None) -> None:
        self._worker = worker_session
        self._owners = list(owner_sessions or [])
        self.target_id = getattr(worker_session, "target_id", "")
        self.session_id = getattr(worker_session, "session_id", "")
        self.client = getattr(worker_session, "client", None)

    def request(self, *args: Any, **kwargs: Any) -> Any:
        return self._worker.request(*args, **kwargs)

    def evaluate(self, *args: Any, **kwargs: Any) -> Any:
        return self._worker.evaluate(*args, **kwargs)

    def close(self) -> None:
        seen: set[int] = set()
        for session in [self._worker, *reversed(self._owners)]:
            if session is None or id(session) in seen:
                continue
            seen.add(id(session))
            try:
                session.close()
            except Exception:
                pass
        self._owners.clear()


def install_cdp_event_support(recorder_module: Any) -> None:
    """Patch only the recorder CDP transport used by this live validator.

    The base recorder deliberately had a command-only receiver. Discovery V2 needs
    Target.attachedToTarget events, but still permits only a read-only CDP allowlist.
    """
    if getattr(recorder_module, "_PROSPECTIVE_DISCOVERY_V2_CDP", False):
        return

    recorder_module.READ_ONLY_METHODS.add("Target.setAutoAttach")
    if any(method.startswith("Input.") for method in recorder_module.READ_ONLY_METHODS):
        raise RuntimeError("read-only CDP allowlist unexpectedly contains Input.*")
    if "Runtime.callFunctionOn" in recorder_module.READ_ONLY_METHODS:
        raise RuntimeError("read-only CDP allowlist unexpectedly contains Runtime.callFunctionOn")

    base_client = recorder_module.CdpClient
    websocket_module = recorder_module.websocket

    class ProspectiveV2CdpClient(base_client):
        def __init__(self, websocket_url: str, timeout: float = 5.0) -> None:
            super().__init__(websocket_url, timeout)
            self._event_cv = threading.Condition()
            self._event_seq = 0
            self._events: list[tuple[int, dict[str, Any]]] = []

        def _receiver(self) -> None:
            ws = self._ws
            if ws is None:
                return
            try:
                while not self._closed.is_set():
                    try:
                        raw = ws.recv()
                    except websocket_module.WebSocketTimeoutException:
                        continue
                    if not raw:
                        break
                    try:
                        message = json.loads(raw)
                    except ValueError:
                        continue
                    message_id = message.get("id")
                    if isinstance(message_id, int):
                        with self._pending_lock:
                            pending = self._pending.pop(message_id, None)
                        if pending:
                            pending.put(message)
                        continue
                    if isinstance(message.get("method"), str):
                        with self._event_cv:
                            self._event_seq += 1
                            self._events.append((self._event_seq, message))
                            if len(self._events) > MAX_EVENT_ROWS:
                                del self._events[: len(self._events) - MAX_EVENT_ROWS]
                            self._event_cv.notify_all()
            except Exception:
                pass
            finally:
                self._closed.set()
                with self._event_cv:
                    self._event_cv.notify_all()

        def event_cursor(self) -> int:
            with self._event_cv:
                return self._event_seq

        def wait_for_events(
            self,
            cursor: int,
            *,
            timeout: float,
            predicate: Callable[[dict[str, Any]], bool] | None = None,
        ) -> tuple[int, list[dict[str, Any]]]:
            deadline = time.monotonic() + max(0.0, timeout)
            newest = cursor
            found: list[dict[str, Any]] = []
            with self._event_cv:
                while True:
                    rows = [(seq, msg) for seq, msg in self._events if seq > cursor]
                    if rows:
                        newest = max(seq for seq, _ in rows)
                        found = [msg for _, msg in rows if predicate is None or predicate(msg)]
                        if found:
                            return newest, found
                        cursor = newest
                    remaining = deadline - time.monotonic()
                    if remaining <= 0 or self._closed.is_set():
                        return newest, found
                    self._event_cv.wait(remaining)

        def close(self) -> None:
            super().close()
            with self._event_cv:
                self._event_cv.notify_all()

    recorder_module.CdpClient = ProspectiveV2CdpClient
    recorder_module._PROSPECTIVE_DISCOVERY_V2_CDP = True


def _summary(target: dict[str, Any]) -> dict[str, Any]:
    keys = (
        "targetId", "type", "url", "title", "name", "attached",
        "parentId", "openerId", "parentFrameId", "browserContextId", "subtype",
    )
    return {k: target.get(k) for k in keys if target.get(k) not in (None, "")}


def _worker_compatible(target: dict[str, Any], *, related: bool) -> bool:
    # URL is intentionally not a gate for real worker-like targets. Exact runtime +
    # World identity is the gate. This safely supports hashed, blob, or changed URLs.
    if target.get("type") in WORKER_TYPES:
        return True
    return related and bool(WOF_URL_HINT_RE.search(str(target.get("url") or "")))


def _identity_payload(payload: Any) -> dict[str, Any]:
    if not isinstance(payload, dict):
        return {}
    inner = payload.get("identity")
    return inner if isinstance(inner, dict) else payload


def _identity_ok(payload: Any, expected_sha256: str) -> bool:
    if not isinstance(payload, dict) or payload.get("ok") is not True:
        return False
    identity = _identity_payload(payload)
    return (
        identity.get("sha256") == expected_sha256
        and identity.get("readOnly", payload.get("readOnly")) is True
        and int(identity.get("ramWrites", payload.get("ramWrites", 0)) or 0) == 0
        and identity.get("inputInjection", payload.get("inputInjection", False)) is False
    )


def _probe_session(
    session: Any,
    target: dict[str, Any],
    *,
    light_probe_js: str,
    identity_probe_js: str,
    expected_sha256: str,
) -> tuple[dict[str, Any], dict[str, Any] | None, str]:
    try:
        session.request("Runtime.enable", timeout=5.0)
        light = session.evaluate(light_probe_js, timeout=5.0)
    except Exception as exc:
        return {"moduleOk": False, "reason": str(exc), "readOnly": True, "ramWrites": 0, "inputInjection": False}, None, "probe-error"
    if not isinstance(light, dict):
        return {"moduleOk": False, "reason": "light probe malformed", "readOnly": True, "ramWrites": 0, "inputInjection": False}, None, "wasm-not-ready"
    if light.get("moduleOk") is not True or light.get("heapOk") is not True or light.get("ramWithinHeap") is not True:
        return light, None, "wasm-not-ready"
    try:
        identity = session.evaluate(identity_probe_js, await_promise=True, timeout=45.0)
    except Exception as exc:
        identity = {"ok": False, "reason": str(exc), "readOnly": True, "ramWrites": 0, "inputInjection": False}
    if not _identity_ok(identity, expected_sha256):
        return light, identity if isinstance(identity, dict) else None, "wrong-identity"
    return light, identity, "supported"


def _child_session(session_factory: Callable[[Any, str, str], Any], client: Any, info: dict[str, Any], child_sid: str) -> Any:
    return session_factory(client, str(info.get("targetId") or ""), child_sid)


def _ancestry_session_ids(candidate_sid: str, parent_by_sid: dict[str, str], root_sid: str) -> set[str]:
    keep = {candidate_sid}
    sid = candidate_sid
    while sid in parent_by_sid:
        sid = parent_by_sid[sid]
        keep.add(sid)
        if sid == root_sid:
            break
    keep.add(root_sid)
    return keep


def _scan_related_page(
    client: Any,
    page: dict[str, Any],
    *,
    session_factory: Callable[[Any, str, str], Any],
    light_probe_js: str,
    identity_probe_js: str,
    expected_sha256: str,
    settle_seconds: float,
) -> tuple[list[Candidate], dict[str, Any]]:
    root = None
    sessions: dict[str, tuple[Any, int]] = {}
    parent_by_sid: dict[str, str] = {}
    topology: list[dict[str, Any]] = []
    probed: list[dict[str, Any]] = []
    supported: list[tuple[dict[str, Any], Any, str, dict[str, Any], dict[str, Any]]] = []
    seen_targets: set[str] = set()
    retained: set[str] = set()
    try:
        root = client.attach(str(page.get("targetId") or ""))
        sessions[root.session_id] = (root, 0)
        cursor = client.event_cursor()
        root.request("Target.setAutoAttach", {"autoAttach": True, "waitForDebuggerOnStart": False, "flatten": True})
        deadline = time.monotonic() + max(0.0, settle_seconds)
        while time.monotonic() < deadline and len(sessions) < MAX_RELATED_SESSIONS:
            cursor, events = client.wait_for_events(
                cursor,
                timeout=min(0.18, max(0.0, deadline - time.monotonic())),
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
                tid = str(info.get("targetId") or "")
                child = _child_session(session_factory, client, info, child_sid)
                sessions[child_sid] = (child, depth)
                parent_by_sid[child_sid] = parent_sid
                topology.append({**_summary(info), "depth": depth, "attachedFromTargetId": getattr(parent[0], "target_id", None)})

                if _worker_compatible(info, related=True) and tid and tid not in seen_targets:
                    seen_targets.add(tid)
                    light, identity, status = _probe_session(
                        child,
                        info,
                        light_probe_js=light_probe_js,
                        identity_probe_js=identity_probe_js,
                        expected_sha256=expected_sha256,
                    )
                    probed.append({"target": _summary(info), "status": status, "light": light, "identity": identity})
                    if status == "supported" and identity is not None:
                        supported.append((dict(info), child, child_sid, light, identity))

                if depth < MAX_RELATED_DEPTH and info.get("type") in RELATED_CONTAINER_TYPES:
                    try:
                        child.request("Target.setAutoAttach", {"autoAttach": True, "waitForDebuggerOnStart": False, "flatten": True})
                    except Exception:
                        pass

        candidates: list[Candidate] = []
        if len(supported) == 1 and root is not None:
            info, worker_session, worker_sid, light, identity = supported[0]
            retained = _ancestry_session_ids(worker_sid, parent_by_sid, root.session_id)
            owners = [session for sid, (session, _depth) in sessions.items() if sid in retained and sid != worker_sid]
            candidates.append(Candidate(dict(page), info, worker_session, owners, "page-autoattach", light, identity))
        return candidates, {
            "page": _summary(page),
            "path": "page-autoattach",
            "relatedTopology": topology,
            "probedWorkers": probed,
            "supportedObserved": len(supported),
            "supportedCount": len(candidates),
            "ambiguous": len(supported) > 1,
            "readOnly": True,
            "ramWrites": 0,
            "inputInjection": False,
        }
    finally:
        for sid, (session, _depth) in list(sessions.items())[::-1]:
            if sid in retained:
                continue
            try:
                session.close()
            except Exception:
                pass


def _page_for_direct(worker: dict[str, Any], pages: list[dict[str, Any]]) -> dict[str, Any] | None:
    for key in ("parentId", "openerId"):
        relation = worker.get(key)
        if relation:
            linked = [page for page in pages if page.get("targetId") == relation]
            if len(linked) == 1:
                return linked[0]
    context_id = worker.get("browserContextId")
    if context_id:
        linked = [page for page in pages if page.get("browserContextId") == context_id]
        if len(linked) == 1:
            return linked[0]
    return pages[0] if len(pages) == 1 else None


def _scan_direct(
    client: Any,
    targets: list[dict[str, Any]],
    pages: list[dict[str, Any]],
    *,
    related_target_ids: set[str],
    skip_page_ids: set[str],
    light_probe_js: str,
    identity_probe_js: str,
    expected_sha256: str,
) -> tuple[list[Candidate], list[dict[str, Any]]]:
    raw: list[Candidate] = []
    diag: list[dict[str, Any]] = []
    for worker in targets:
        target_id = str(worker.get("targetId") or "")
        if not target_id or target_id in related_target_ids or not _worker_compatible(worker, related=False):
            continue
        page = _page_for_direct(worker, pages)
        if page is None:
            diag.append({"target": _summary(worker), "status": "page-association-ambiguous"})
            continue
        page_id = str(page.get("targetId") or "")
        if page_id in skip_page_ids:
            continue
        session = None
        try:
            session = client.attach(target_id)
            light, identity, status = _probe_session(
                session,
                worker,
                light_probe_js=light_probe_js,
                identity_probe_js=identity_probe_js,
                expected_sha256=expected_sha256,
            )
            diag.append({"target": _summary(worker), "page": _summary(page), "status": status, "light": light, "identity": identity})
            if status == "supported" and identity is not None:
                raw.append(Candidate(dict(page), dict(worker), session, [], "direct-worker", light, identity))
                session = None
        except Exception as exc:
            diag.append({"target": _summary(worker), "status": "probe-error", "reason": str(exc)})
        finally:
            if session is not None:
                try:
                    session.close()
                except Exception:
                    pass

    by_page: dict[str, list[Candidate]] = {}
    for candidate in raw:
        by_page.setdefault(str(candidate.page.get("targetId") or ""), []).append(candidate)
    out: list[Candidate] = []
    for page_id, rows in by_page.items():
        if len(rows) == 1:
            out.append(rows[0])
        else:
            for row in rows:
                row.close()
            diag.append({"pageTargetId": page_id, "status": "ambiguous-supported-workers", "count": len(rows)})
    return out, diag


def discover_candidates(
    client: Any,
    targets: list[dict[str, Any]],
    *,
    session_factory: Callable[[Any, str, str], Any],
    light_probe_js: str,
    identity_probe_js: str,
    expected_sha256: str,
    skip_page_ids: set[str] | None = None,
    settle_seconds: float = AUTOATTACH_WINDOW_SECONDS,
    endpoint_label: str | None = None,
) -> tuple[list[Candidate], dict[str, Any]]:
    skip_page_ids = set(skip_page_ids or set())
    pages = [dict(target) for target in targets if target.get("type") == "page" and target.get("targetId")]
    related_candidates: list[Candidate] = []
    related_diag: list[dict[str, Any]] = []
    related_target_ids: set[str] = set()

    for page in pages:
        page_id = str(page.get("targetId") or "")
        if page_id in skip_page_ids:
            continue
        rows, diag = _scan_related_page(
            client,
            page,
            session_factory=session_factory,
            light_probe_js=light_probe_js,
            identity_probe_js=identity_probe_js,
            expected_sha256=expected_sha256,
            settle_seconds=settle_seconds,
        )
        related_diag.append(diag)
        for probed in diag.get("probedWorkers", []):
            target = probed.get("target") if isinstance(probed, dict) else None
            if isinstance(target, dict) and target.get("targetId"):
                related_target_ids.add(str(target["targetId"]))
        related_candidates.extend(rows)

    direct_candidates, direct_diag = _scan_direct(
        client,
        targets,
        pages,
        related_target_ids=related_target_ids,
        skip_page_ids=skip_page_ids,
        light_probe_js=light_probe_js,
        identity_probe_js=identity_probe_js,
        expected_sha256=expected_sha256,
    )
    candidates = related_candidates + direct_candidates
    return candidates, {
        "version": DISCOVERY_VERSION,
        "endpointLabel": endpoint_label,
        "targetCount": len(targets),
        "pageCount": len(pages),
        "browserTargets": [_summary(target) for target in targets[:32]],
        "relatedPages": related_diag,
        "directWorkers": direct_diag,
        "candidateCount": len(candidates),
        "readOnly": True,
        "ramWrites": 0,
        "inputInjection": False,
        "evidenceClass": "discovery-only",
    }


def ambiguous_page_ids(diag: dict[str, Any]) -> set[str]:
    out = {
        str((row.get("page") or {}).get("targetId") or "")
        for row in diag.get("relatedPages", [])
        if isinstance(row, dict) and row.get("ambiguous") is True
    }
    out.update(
        str(row.get("pageTargetId") or "")
        for row in diag.get("directWorkers", [])
        if isinstance(row, dict) and row.get("status") == "ambiguous-supported-workers"
    )
    out.discard("")
    return out


def discovery_status_zh(diag: dict[str, Any]) -> str:
    probed: list[dict[str, Any]] = []
    for page in diag.get("relatedPages", []):
        if isinstance(page, dict):
            probed.extend([row for row in page.get("probedWorkers", []) if isinstance(row, dict)])
    probed.extend([row for row in diag.get("directWorkers", []) if isinstance(row, dict)])
    statuses = {str(row.get("status") or "") for row in probed}
    if "wrong-identity" in statuses:
        return "已找到 Worker/WASM，但游戏版本不是精确 World 921031；已安全拒绝准入。"
    if "wasm-not-ready" in statuses:
        return "已找到相关 Worker，WASM / 内存尚未就绪；会自动继续重试。"
    if ambiguous_page_ids(diag) or "page-association-ambiguous" in statuses:
        return "发现多个页面/Worker 且关联不唯一；为避免跨房间串证据，已安全拒绝准入。"
    if diag.get("pageCount"):
        return "已找到页面，正在通过 page / iframe topology 自动发现游戏 Worker。"
    return "尚未找到可验证的 WOF 页面；游戏本身不受影响，会自动继续等待。"


def room_liveness_reason(
    *,
    discovery_path: str,
    target_id: str,
    page_id: str,
    current_target_ids: set[str],
    current_page_ids: set[str],
) -> str | None:
    if discovery_path == "direct-worker" and target_id not in current_target_ids:
        return "worker-closed-or-reloaded"
    if discovery_path == "page-autoattach" and page_id and page_id not in current_page_ids:
        return "page-closed-or-reloaded"
    return None
