from __future__ import annotations

import json
import re
import threading
import time
from dataclasses import dataclass, field
from typing import Any, Callable

import websocket

WORKER_TYPES = {"worker", "shared_worker", "service_worker"}
RELATED_CONTAINER_TYPES = {"iframe", "worker", "shared_worker", "service_worker"}
BAD_WORKER_URL_PREFIXES = ("blob:", "data:", "javascript:")
MAX_EVENT_ROWS = 512
AUTOATTACH_WINDOW_SECONDS = 0.9
MAX_RELATED_SESSIONS = 24
MAX_RELATED_DEPTH = 2


@dataclass
class Candidate:
    page: dict[str, Any]
    target: dict[str, Any]
    session: Any
    owner_session: Any | None
    path: str
    light: dict[str, Any]
    identity: dict[str, Any]
    topology: list[dict[str, Any]] = field(default_factory=list)

    def close(self) -> None:
        try:
            self.session.close()
        except Exception:
            pass
        if self.owner_session is not None and self.owner_session is not self.session:
            try:
                self.owner_session.close()
            except Exception:
                pass


class OwnedSession:
    """Worker session plus its page auto-attach owner session."""

    def __init__(self, worker_session: Any, owner_session: Any | None = None) -> None:
        self._worker = worker_session
        self._owner = owner_session
        self.target_id = getattr(worker_session, "target_id", "")
        self.session_id = getattr(worker_session, "session_id", "")
        self.client = getattr(worker_session, "client", None)

    def request(self, *args: Any, **kwargs: Any) -> Any:
        return self._worker.request(*args, **kwargs)

    def evaluate(self, *args: Any, **kwargs: Any) -> Any:
        return self._worker.evaluate(*args, **kwargs)

    def close(self) -> None:
        try:
            self._worker.close()
        except Exception:
            pass
        if self._owner is not None and self._owner is not self._worker:
            try:
                self._owner.close()
            except Exception:
                pass


def _summary(target: dict[str, Any]) -> dict[str, Any]:
    keys = (
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
    return {k: target.get(k) for k in keys if target.get(k) not in (None, "")}


def _worker_compatible(target: dict[str, Any], *, related: bool) -> bool:
    url = str(target.get("url") or "")
    if url.lower().startswith(BAD_WORKER_URL_PREFIXES):
        return False
    if target.get("type") in WORKER_TYPES:
        return True
    return related and bool(re.search(r"gstyphoon", url, re.I))


def _identity_ok(recorder_module: Any, payload: Any) -> bool:
    if not isinstance(payload, dict) or payload.get("ok") is not True:
        return False
    identity = payload.get("identity") if isinstance(payload.get("identity"), dict) else payload
    return identity.get("sha256") == recorder_module.WORLD_SHA256


def _probe_session(manager: Any, session: Any, target: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any] | None, str]:
    recorder_module = manager._wof052l_recorder_module
    try:
        session.request("Runtime.enable", timeout=5.0)
        light = session.evaluate(recorder_module.LIGHT_PROBE, timeout=5.0)
    except Exception as exc:
        return {"moduleOk": False, "reason": str(exc)}, None, "probe-error"
    if not isinstance(light, dict):
        return {"moduleOk": False, "reason": "light probe malformed"}, None, "wasm-not-ready"
    if light.get("moduleOk") is not True or light.get("heapOk") is not True or light.get("ramWithinHeap") is not True:
        return light, None, "wasm-not-ready"

    target_id = str(target.get("targetId") or "")
    cache = manager._wof052l_identity_cache
    identity = cache.get(target_id)
    if not isinstance(identity, dict):
        try:
            identity = session.evaluate(manager._wof052l_identity_probe_js, await_promise=True, timeout=35.0)
        except Exception as exc:
            identity = {"ok": False, "reason": str(exc), "readOnly": True, "ramWrites": 0, "inputInjection": False}
        if isinstance(identity, dict):
            inner = identity.get("identity") if isinstance(identity.get("identity"), dict) else identity
            sha = inner.get("sha256")
            if isinstance(sha, str) and re.fullmatch(r"[0-9a-f]{64}", sha):
                cache[target_id] = identity
    if not _identity_ok(recorder_module, identity):
        return light, identity if isinstance(identity, dict) else None, "wrong-identity"
    return light, identity, "supported"


def _child_session(recorder_module: Any, client: Any, info: dict[str, Any], child_sid: str) -> Any:
    return recorder_module.CdpSession(client, str(info.get("targetId") or ""), child_sid)


def _scan_related_page(manager: Any, page: dict[str, Any]) -> tuple[list[Candidate], dict[str, Any]]:
    client = manager.client
    recorder_module = manager._wof052l_recorder_module
    assert client is not None
    root = None
    sessions: dict[str, tuple[Any, int]] = {}
    topology: list[dict[str, Any]] = []
    probed: list[dict[str, Any]] = []
    candidates: list[Candidate] = []
    seen_targets: set[str] = set()
    retain_root = False
    try:
        root = client.attach(str(page.get("targetId") or ""))
        sessions[root.session_id] = (root, 0)
        cursor = client.event_cursor()
        root.request("Target.setAutoAttach", {"autoAttach": True, "waitForDebuggerOnStart": False, "flatten": True})
        deadline = time.monotonic() + AUTOATTACH_WINDOW_SECONDS
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
                params = event.get("params") or {}
                child_sid = str(params.get("sessionId") or "")
                info = params.get("targetInfo")
                if not parent or not child_sid or not isinstance(info, dict):
                    continue
                depth = parent[1] + 1
                target_id = str(info.get("targetId") or "")
                topology.append({**_summary(info), "depth": depth, "attachedFromTargetId": getattr(parent[0], "target_id", None)})
                child = _child_session(recorder_module, client, info, child_sid)
                sessions[child_sid] = (child, depth)

                if _worker_compatible(info, related=True) and target_id and target_id not in seen_targets:
                    seen_targets.add(target_id)
                    light, identity, status = _probe_session(manager, child, info)
                    probed.append({"target": _summary(info), "status": status, "light": light, "identity": identity})
                    if status == "supported" and identity is not None:
                        candidates.append(Candidate(dict(page), dict(info), child, root, "page-autoattach", light, identity, topology))
                        retain_root = True

                if depth < MAX_RELATED_DEPTH and info.get("type") in RELATED_CONTAINER_TYPES:
                    try:
                        child.request("Target.setAutoAttach", {"autoAttach": True, "waitForDebuggerOnStart": False, "flatten": True})
                    except Exception:
                        pass

        supported_observed = len(candidates)
        if supported_observed != 1:
            for candidate in candidates:
                candidate.owner_session = None
            retain_root = False
            candidates.clear()
        return candidates, {
            "page": _summary(page),
            "path": "page-autoattach",
            "relatedTopology": topology,
            "probedWorkers": probed,
            "supportedObserved": supported_observed,
            "supportedCount": len(candidates),
            "ambiguous": supported_observed > 1,
        }
    finally:
        if root is not None and not retain_root:
            try:
                root.close()
            except Exception:
                pass


def _page_for_direct(worker: dict[str, Any], pages: list[dict[str, Any]]) -> dict[str, Any] | None:
    for key in ("parentId", "openerId"):
        relation = worker.get(key)
        if relation:
            linked = [page for page in pages if page.get("targetId") == relation]
            if len(linked) == 1:
                return linked[0]
    if len(pages) == 1:
        return pages[0]
    return None


def _scan_direct(
    manager: Any,
    targets: list[dict[str, Any]],
    pages: list[dict[str, Any]],
    related_target_ids: set[str],
    skip_page_ids: set[str],
) -> tuple[list[Candidate], list[dict[str, Any]]]:
    client = manager.client
    assert client is not None
    raw: list[Candidate] = []
    diag: list[dict[str, Any]] = []
    for worker in targets:
        target_id = str(worker.get("targetId") or "")
        if target_id in related_target_ids or not target_id or not _worker_compatible(worker, related=False):
            continue
        page = _page_for_direct(worker, pages)
        if page is None:
            diag.append({"target": _summary(worker), "status": "page-association-ambiguous"})
            continue
        if str(page.get("targetId") or "") in skip_page_ids:
            continue
        session = None
        try:
            session = client.attach(target_id)
            light, identity, status = _probe_session(manager, session, worker)
            diag.append({"target": _summary(worker), "page": _summary(page), "status": status, "light": light, "identity": identity})
            if status == "supported" and identity is not None:
                raw.append(Candidate(dict(page), dict(worker), session, None, "direct-worker", light, identity, []))
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
    manager: Any,
    targets: list[dict[str, Any]],
    *,
    skip_page_ids: set[str] | None = None,
) -> tuple[list[Candidate], dict[str, Any]]:
    skip_page_ids = skip_page_ids or set()
    pages = [dict(target) for target in targets if target.get("type") == "page" and target.get("targetId")]
    related_candidates: list[Candidate] = []
    related_diag: list[dict[str, Any]] = []
    related_target_ids: set[str] = set()
    for page in pages:
        if str(page.get("targetId") or "") in skip_page_ids:
            continue
        rows, diag = _scan_related_page(manager, page)
        related_diag.append(diag)
        for probed in diag.get("probedWorkers", []):
            target = probed.get("target") if isinstance(probed, dict) else None
            if isinstance(target, dict) and target.get("targetId"):
                related_target_ids.add(str(target["targetId"]))
        related_candidates.extend(rows)

    direct_candidates, direct_diag = _scan_direct(manager, targets, pages, related_target_ids, skip_page_ids)
    candidates = related_candidates + direct_candidates
    return candidates, {
        "version": "wof-052l-discovery-v2",
        "targetCount": len(targets),
        "pageCount": len(pages),
        "browserTargets": [_summary(target) for target in targets[:32]],
        "relatedPages": related_diag,
        "directWorkers": direct_diag,
        "candidateCount": len(candidates),
        "endpoint": {
            "host": getattr(getattr(manager, "endpoint", None), "host", None),
            "port": getattr(getattr(manager, "endpoint", None), "port", None),
        },
        "readOnly": True,
        "ramWrites": 0,
        "inputInjection": False,
    }


def _announce(manager: Any, message: str) -> None:
    if getattr(manager, "_wof052l_last_discovery_message", None) == message:
        return
    manager._wof052l_last_discovery_message = message
    print(message)


def _attach_candidate(manager: Any, candidate: Candidate, now: float, topology: dict[str, Any]) -> None:
    recorder_module = manager._wof052l_recorder_module
    target_id = str(candidate.target.get("targetId") or "")
    page_id = str(candidate.page.get("targetId") or "")
    if not target_id or target_id in manager.live or now < manager.retry_after.get(target_id, 0):
        candidate.close()
        return
    if any(str(room.page.get("targetId") or "") == page_id for room in manager.live.values() if room.page):
        candidate.close()
        return

    session = OwnedSession(candidate.session, candidate.owner_session)
    candidate.owner_session = None
    try:
        bootstrap = session.evaluate(manager.probe_js, await_promise=True, timeout=45.0)
        if not isinstance(bootstrap, dict) or bootstrap.get("ok") is not True:
            reason = str((bootstrap or {}).get("reason") if isinstance(bootstrap, dict) else "malformed bootstrap")
            manager.retry_after[target_id] = now + 30.0
            _announce(manager, f"\nWorker 已发现，但未通过 WOF-052L 采集准入；游戏本身不受影响。\n技术详情：{reason}")
            session.close()
            return
        identity = bootstrap.get("identity") or {}
        if identity.get("sha256") != recorder_module.WORLD_SHA256:
            manager.retry_after[target_id] = now + 60.0
            _announce(manager, "\nWorker 已发现，但 World 921031 身份不匹配；已安全拒绝采集。")
            session.close()
            return

        bootstrap = dict(bootstrap)
        bootstrap["topologyDiagnostics"] = {
            "discoveryPath": candidate.path,
            "page": _summary(candidate.page),
            "worker": _summary(candidate.target),
            "snapshot": topology,
        }
        target = dict(candidate.target)
        target["discoveryPath"] = candidate.path
        room_id = f"room-{recorder_module.local_stamp()}-{recorder_module.safe_name(target_id[:10])}"
        room = recorder_module.RoomCapture(
            run_id=manager.run_id,
            room_id=room_id,
            target=target,
            page=dict(candidate.page),
            session=session,
            output_dir=manager.output_dir,
            bootstrap=bootstrap,
            latest_status=bootstrap,
        )
        manager.live[target_id] = room
        manager.retry_after.pop(target_id, None)
        manager._wof052l_last_discovery_message = None
        print(f"\n+ 房间 {room_id} 已连接 — World 921031 已确认 / Discovery V2 / 只读模式")
    except Exception as exc:
        manager.retry_after[target_id] = now + 3.0
        session.close()
        _announce(manager, f"\n连接 Worker {target_id[:8]} 失败；其他房间继续运行，游戏本身不受影响。\n技术详情：{exc}")


def _discovery_status(diag: dict[str, Any]) -> str:
    probed: list[dict[str, Any]] = []
    for page in diag.get("relatedPages", []):
        if isinstance(page, dict):
            probed.extend([x for x in page.get("probedWorkers", []) if isinstance(x, dict)])
    probed.extend([x for x in diag.get("directWorkers", []) if isinstance(x, dict)])
    statuses = {str(row.get("status") or "") for row in probed}
    if "wrong-identity" in statuses:
        return "\n已找到 Worker/WASM，但游戏版本不是精确 World 921031；已安全拒绝采集。"
    if "wasm-not-ready" in statuses:
        return "\n已找到相关 Worker，WASM / 内存尚未就绪；采集器会自动继续重试。"
    if any(status in statuses for status in {"page-association-ambiguous", "ambiguous-supported-workers"}):
        return "\n发现多个页面/Worker，但关联不唯一；为避免跨房间串采，当前已安全停止准入。"
    if diag.get("pageCount"):
        return "\n已找到页面，正在通过 page/iframe topology 自动发现游戏 Worker。"
    return "\n尚未找到可采集的 WOF 页面；游戏本身不受影响，采集器会继续等待。"


def install(recorder_module: Any) -> None:
    if getattr(recorder_module, "_WOF052L_DISCOVERY_V2_INSTALLED", False):
        return

    recorder_module.READ_ONLY_METHODS.add("Target.setAutoAttach")
    base_client = recorder_module.CdpClient

    class V2CdpClient(base_client):
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
                    except websocket.WebSocketTimeoutException:
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

    recorder_module.CdpClient = V2CdpClient

    original_init = recorder_module.RecorderManager.__init__
    original_to_json = recorder_module.RoomCapture.to_json

    def manager_init(self: Any, output_dir: Any, args: Any) -> None:
        original_init(self, output_dir, args)
        self._wof052l_recorder_module = recorder_module
        self._wof052l_identity_probe_js = __import__("pathlib").Path(__file__).with_name("identity_probe.js").read_text(encoding="utf-8")
        self._wof052l_identity_cache: dict[str, dict[str, Any]] = {}
        self._wof052l_last_discovery_message: str | None = None
        self._wof052l_last_topology: dict[str, Any] = {}
        self._wof052l_last_live_topology_audit = 0.0

    def room_to_json(self: Any, *, final: bool, reason: str) -> dict[str, Any]:
        payload = original_to_json(self, final=final, reason=reason)
        topology = self.bootstrap.get("topologyDiagnostics") if isinstance(self.bootstrap, dict) else None
        if isinstance(topology, dict):
            payload["topologyDiagnostics"] = topology
        if isinstance(self.target, dict) and self.target.get("discoveryPath"):
            payload.setdefault("target", {})["discoveryPath"] = self.target.get("discoveryPath")
        return payload

    def discover(self: Any, now: float) -> None:
        if not self.client or now - self._last_discovery < recorder_module.DISCOVERY_INTERVAL:
            return
        self._last_discovery = now
        try:
            targets = self.client.targets()
        except Exception:
            self._browser_lost()
            return

        current_ids = {str(target.get("targetId")) for target in targets if target.get("targetId")}
        page_ids = {str(target.get("targetId")) for target in targets if target.get("type") == "page" and target.get("targetId")}
        for target_id, room in list(self.live.items()):
            path = str(room.target.get("discoveryPath") or "direct-worker") if isinstance(room.target, dict) else "direct-worker"
            page_id = str(room.page.get("targetId") or "") if room.page else ""
            if path == "direct-worker" and target_id not in current_ids:
                self._finalize_target(target_id, "worker-closed-or-reloaded", try_remote=False)
            elif path == "page-autoattach" and page_id and page_id not in page_ids:
                self._finalize_target(target_id, "page-closed-or-reloaded", try_remote=False)

        live_page_ids = {
            str(room.page.get("targetId") or "")
            for room in self.live.values()
            if room.page and room.page.get("targetId")
        }
        audit_live = now - self._wof052l_last_live_topology_audit >= 10.0
        if audit_live:
            self._wof052l_last_live_topology_audit = now
        candidates, topology = discover_candidates(
            self,
            targets,
            skip_page_ids=set() if audit_live else live_page_ids,
        )
        self._wof052l_last_topology = topology

        ambiguous_pages = {
            str((row.get("page") or {}).get("targetId") or "")
            for row in topology.get("relatedPages", [])
            if isinstance(row, dict) and row.get("ambiguous") is True
        }
        ambiguous_pages.update(
            str(row.get("pageTargetId") or "")
            for row in topology.get("directWorkers", [])
            if isinstance(row, dict) and row.get("status") == "ambiguous-supported-workers"
        )
        if ambiguous_pages:
            for target_id, room in list(self.live.items()):
                page_id = str(room.page.get("targetId") or "") if room.page else ""
                if page_id in ambiguous_pages:
                    self._finalize_target(target_id, "worker-association-ambiguous", try_remote=False)

        if not candidates:
            _announce(self, _discovery_status(topology))
            return
        for candidate in candidates:
            _attach_candidate(self, candidate, now, topology)

    recorder_module.RecorderManager.__init__ = manager_init
    recorder_module.RecorderManager.discover = discover
    recorder_module.RoomCapture.to_json = room_to_json
    recorder_module._WOF052L_DISCOVERY_V2_INSTALLED = True
