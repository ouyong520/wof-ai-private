from __future__ import annotations

import ipaddress
from collections import defaultdict
from typing import Any, Callable
from urllib.parse import urlparse

import discovery_v2 as discovery

CROSS_PAGE_STATUS = "cross-page-worker-association-ambiguous"


def _page_hint(page: dict[str, Any]) -> bool:
    text = " ".join(str(page.get(k) or "") for k in ("url", "title", "name"))
    return bool(discovery.WOF_URL_HINT_RE.search(text))


def safe_page_for_direct(worker: dict[str, Any], pages: list[dict[str, Any]]) -> dict[str, Any] | None:
    """Direct compatibility fallback without treating Worker openerId as parent authority."""
    parent_id = worker.get("parentId")
    if parent_id:
        linked = [page for page in pages if page.get("targetId") == parent_id]
        if len(linked) == 1:
            return linked[0]

    parent_frame_id = worker.get("parentFrameId")
    if parent_frame_id:
        linked = [
            page for page in pages
            if page.get("frameId") == parent_frame_id or page.get("targetId") == parent_frame_id
        ]
        if len(linked) == 1:
            return linked[0]

    wof_pages = [page for page in pages if _page_hint(page)]
    return wof_pages[0] if len(wof_pages) == 1 else None


def install_direct_fallback_guard() -> None:
    discovery._page_for_direct = safe_page_for_direct


def harden_relation_graph(candidates: list[Any], diag: dict[str, Any]) -> tuple[list[Any], dict[str, Any]]:
    by_worker: dict[str, list[Any]] = defaultdict(list)
    for candidate in candidates:
        worker_id = str(candidate.target.get("targetId") or "")
        if worker_id:
            by_worker[worker_id].append(candidate)

    rejected_ids: set[int] = set()
    ambiguous_rows: list[dict[str, Any]] = []
    for worker_id, rows in by_worker.items():
        page_ids = sorted({str(row.page.get("targetId") or "") for row in rows if row.page.get("targetId")})
        if len(page_ids) <= 1:
            continue
        ambiguous_rows.append({
            "status": CROSS_PAGE_STATUS,
            "workerTargetId": worker_id,
            "pageTargetIds": page_ids,
            "relationCount": len(rows),
            "evidenceClass": "discovery-only",
        })
        for row in rows:
            rejected_ids.add(id(row))
            row.close()

    kept = [candidate for candidate in candidates if id(candidate) not in rejected_ids]
    out_diag = dict(diag)
    out_diag["crossPageAmbiguities"] = ambiguous_rows
    out_diag["candidateCount"] = len(kept)
    out_diag["evidenceClass"] = "discovery-only"
    return kept, out_diag


def discover_candidates(*args: Any, **kwargs: Any) -> tuple[list[Any], dict[str, Any]]:
    install_direct_fallback_guard()
    candidates, diag = discovery.discover_candidates(*args, **kwargs)
    return harden_relation_graph(candidates, diag)


def ambiguous_page_ids(diag: dict[str, Any]) -> set[str]:
    out = set(discovery.ambiguous_page_ids(diag))
    for row in diag.get("crossPageAmbiguities", []):
        if not isinstance(row, dict) or row.get("status") != CROSS_PAGE_STATUS:
            continue
        out.update(str(page_id) for page_id in row.get("pageTargetIds", []) if page_id)
    return out


def is_loopback_host(host: str) -> bool:
    raw = str(host or "").strip().lower().strip("[]")
    if raw == "localhost":
        return True
    try:
        return ipaddress.ip_address(raw).is_loopback
    except ValueError:
        return False


def websocket_matches_endpoint(websocket_url: str, host: str, port: int) -> bool:
    if not is_loopback_host(host):
        return False
    try:
        parsed = urlparse(str(websocket_url or ""))
        if parsed.scheme not in {"ws", "wss"} or not parsed.hostname or parsed.port is None:
            return False
        return is_loopback_host(parsed.hostname) and int(parsed.port) == int(port)
    except (TypeError, ValueError):
        return False


def install_endpoint_guard(core_module: Any) -> None:
    endpoint_cls = core_module.Endpoint
    if getattr(endpoint_cls, "_PROSPECTIVE_V2_HARDENED", False):
        return

    def guarded_connect(self: Any) -> bool:
        if not is_loopback_host(self.host):
            self.close_client()
            return False
        ep = core_module.recorder_core.probe_endpoint(self.host, self.port)
        if not ep or not websocket_matches_endpoint(getattr(ep, "websocket_url", ""), self.host, self.port):
            self.close_client()
            return False
        if self.client is not None and not self.client.closed:
            return True
        self.close_client()
        try:
            self.client = core_module.recorder_core.CdpClient(ep.websocket_url)
            self.client.connect()
            self.client.targets()
            return True
        except Exception:
            self.close_client()
            return False

    endpoint_cls.connect = guarded_connect
    endpoint_cls._PROSPECTIVE_V2_HARDENED = True


def install_live_hardening(live_v2_module: Any) -> None:
    install_direct_fallback_guard()
    install_endpoint_guard(live_v2_module.core)
    live_v2_module.discover_candidates = discover_candidates
    live_v2_module.ambiguous_page_ids = ambiguous_page_ids
