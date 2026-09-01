from __future__ import annotations

from typing import Any

import hardening_v2_base as _base


for _name in dir(_base):
    if not _name.startswith("__"):
        globals()[_name] = getattr(_base, _name)

_BASE_INSTALL_DISCOVERY_HARDENING = _base._install_discovery_hardening
LIVE_TOPOLOGY_REPROOF_FAILED = "live-topology-reproof-failed"


def _supported_topology_pairs(topology: dict[str, Any]) -> set[tuple[str, str]]:
    """Extract uniquely supported (workerTargetId, pageTargetId) proofs."""
    pairs: set[tuple[str, str]] = set()
    ambiguous_pages = cross_page_ambiguous_pages(topology)

    for row in topology.get("relatedPages", []):
        if not isinstance(row, dict) or row.get("ambiguous") is True:
            continue
        page = row.get("page")
        page_id = str(page.get("targetId") or "") if isinstance(page, dict) else ""
        if not page_id or page_id in ambiguous_pages:
            continue
        supported: set[str] = set()
        for probed in row.get("probedWorkers", []):
            if not isinstance(probed, dict) or probed.get("status") != "supported":
                continue
            target = probed.get("target")
            worker_id = str(target.get("targetId") or "") if isinstance(target, dict) else ""
            if worker_id:
                supported.add(worker_id)
        if len(supported) == 1:
            pairs.add((next(iter(supported)), page_id))

    for row in topology.get("directWorkers", []):
        if not isinstance(row, dict) or row.get("status") != "supported":
            continue
        target = row.get("target")
        page = row.get("page")
        worker_id = str(target.get("targetId") or "") if isinstance(target, dict) else ""
        page_id = str(page.get("targetId") or "") if isinstance(page, dict) else ""
        if worker_id and page_id and page_id not in ambiguous_pages:
            pairs.add((worker_id, page_id))

    return pairs


def _finalize_unproven_live(manager: Any, topology: dict[str, Any]) -> list[str]:
    proven = _supported_topology_pairs(topology)
    finalized: list[str] = []
    for target_id, room in list(getattr(manager, "live", {}).items()):
        page = getattr(room, "page", None)
        page_id = str(page.get("targetId") or "") if isinstance(page, dict) else ""
        worker_id = str(target_id or "")
        if not worker_id or not page_id or (worker_id, page_id) not in proven:
            manager._finalize_target(target_id, LIVE_TOPOLOGY_REPROOF_FAILED, try_remote=False)
            finalized.append(worker_id)
    return finalized


def _finalize_all_live_reproof_failure(manager: Any) -> list[str]:
    finalized: list[str] = []
    for target_id in list(getattr(manager, "live", {})):
        manager._finalize_target(target_id, LIVE_TOPOLOGY_REPROOF_FAILED, try_remote=False)
        finalized.append(str(target_id))
    return finalized


def _install_discovery_hardening(recorder_module: Any, discovery_module: Any) -> None:
    """Install base hardening plus fresh-live-topology evidence gating."""
    _BASE_INSTALL_DISCOVERY_HARDENING(recorder_module, discovery_module)

    sync = getattr(discovery_module, "_sync_base_overrides", None)
    if callable(sync):
        sync()

    manager_cls = recorder_module.RecorderManager
    installed_discover = manager_cls.discover
    if getattr(installed_discover, "_WOF052L_FRESH_LIVE_TOPOLOGY_GUARD", False):
        return
    installed_poll_rooms = manager_cls.poll_rooms

    def discover(self: Any, now: float) -> None:
        # Evidence from this loop iteration is disabled until a fresh full-page
        # ownership proof succeeds. Force the base 10-second live audit branch
        # whenever discovery itself is due.
        self._wof052l_live_topology_reproof_token = None
        self._wof052l_last_live_topology_audit = float("-inf")

        last_discovery = float(getattr(self, "_last_discovery", 0.0) or 0.0)
        discovery_due = bool(getattr(self, "client", None)) and (
            now - last_discovery >= recorder_module.DISCOVERY_INTERVAL
        )
        if not discovery_due:
            installed_discover(self, now)
            return

        self._wof052l_last_topology = {}
        try:
            installed_discover(self, now)
        except Exception as exc:
            finalized = _finalize_all_live_reproof_failure(self)
            if finalized:
                announce = getattr(discovery_module, "_announce", None)
                if callable(announce):
                    announce(
                        self,
                        "\n实时拓扑复核失败；相关房间已先完成并停止继续收证据。"
                        f"\n技术详情：{LIVE_TOPOLOGY_REPROOF_FAILED}: {exc}",
                    )
            return

        topology = getattr(self, "_wof052l_last_topology", None)
        if not isinstance(topology, dict):
            topology = {}
        finalized = _finalize_unproven_live(self, topology)
        if finalized:
            announce = getattr(discovery_module, "_announce", None)
            if callable(announce):
                announce(
                    self,
                    "\n实时拓扑无法重新证明唯一 Worker↔页面归属；相关房间已先完成并停止继续收证据。"
                    f"\n技术详情：{LIVE_TOPOLOGY_REPROOF_FAILED}",
                )

        # Remaining live rooms, plus any newly admitted room, have a proof from
        # this exact discovery epoch. poll_rooms(now) may now collect evidence.
        self._wof052l_live_topology_reproof_token = now

    def poll_rooms(self: Any, now: float) -> Any:
        if getattr(self, "live", {}) and getattr(
            self, "_wof052l_live_topology_reproof_token", None
        ) != now:
            return None
        return installed_poll_rooms(self, now)

    discover._WOF052L_FRESH_LIVE_TOPOLOGY_GUARD = True
    poll_rooms._WOF052L_FRESH_LIVE_TOPOLOGY_GUARD = True
    manager_cls.discover = discover
    manager_cls.poll_rooms = poll_rooms


# hardening_v2_base.install resolves this name in its own module globals.
_base._install_discovery_hardening = _install_discovery_hardening
