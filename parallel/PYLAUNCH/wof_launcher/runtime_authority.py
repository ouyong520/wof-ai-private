from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .cdp import CdpClient, CdpError, CdpSession
from .discovery_v2 import TargetChoice
from .probe import LIGHT_WORKER_PROBE, PAGE_PROBE


@dataclass(frozen=True)
class RuntimeFingerprint:
    page_target_id: str
    page_isolate_id: str
    worker_target_id: str
    worker_isolate_id: str
    module_key: str
    heap_bytes: int
    ram_base: int

    def key(self) -> str:
        return "|".join(
            (
                self.page_target_id,
                self.page_isolate_id,
                self.worker_target_id,
                self.worker_isolate_id,
                self.module_key,
                str(self.heap_bytes),
                str(self.ram_base),
            )
        )


def _isolate(session: CdpSession) -> str:
    result = session.request("Runtime.getIsolateId")
    isolate_id = result.get("id")
    if not isinstance(isolate_id, str) or not isolate_id:
        raise CdpError("Runtime.getIsolateId returned no stable isolate id")
    return isolate_id


def _target_map(client: CdpClient) -> dict[str, dict[str, Any]]:
    raw = client.request("Target.getTargets").get("targetInfos")
    if not isinstance(raw, list):
        raise CdpError("Target.getTargets returned malformed targetInfos")
    return {
        str(row.get("targetId")): dict(row)
        for row in raw
        if isinstance(row, dict) and isinstance(row.get("targetId"), str) and row.get("targetId")
    }


def capture_runtime_fingerprint(client: CdpClient, choice: TargetChoice) -> tuple[RuntimeFingerprint, dict[str, Any]]:
    if not choice.page or not choice.worker or not choice.identity or choice.identity.get("ok") is not True:
        raise CdpError("cannot fingerprint an unaccepted WOF authority")
    page_id = str(choice.page.get("targetId") or "")
    worker_id = str(choice.worker.get("targetId") or "")
    if not page_id or not worker_id:
        raise CdpError("accepted WOF authority is missing target ids")

    targets = _target_map(client)
    if page_id not in targets or worker_id not in targets:
        raise CdpError("accepted page/Worker target disappeared")

    page_session = client.attach(page_id)
    try:
        page_isolate = _isolate(page_session)
        page_probe = page_session.evaluate(PAGE_PROBE)
    finally:
        page_session.close()
    if not isinstance(page_probe, dict) or page_probe.get("gameSurface") is not True:
        raise CdpError("accepted WOF page no longer exposes the game surface")

    worker_session = client.attach(worker_id)
    try:
        worker_isolate = _isolate(worker_session)
        light = worker_session.evaluate(LIGHT_WORKER_PROBE)
    finally:
        worker_session.close()
    if not isinstance(light, dict) or light.get("moduleOk") is not True or light.get("heapOk") is not True:
        raise CdpError("accepted WOF Worker runtime is no longer module/heap ready")
    module_key = light.get("moduleKey")
    heap_bytes = light.get("heapBytes")
    ram_base = light.get("ramBase")
    if not isinstance(module_key, str) or not module_key:
        raise CdpError("accepted WOF Worker has no stable module key")
    if not isinstance(heap_bytes, int) or heap_bytes <= 0:
        raise CdpError("accepted WOF Worker has malformed heap size")
    if not isinstance(ram_base, int) or ram_base <= 0 or light.get("ramWithinHeap") is not True:
        raise CdpError("accepted WOF Worker has malformed RAM window")

    fingerprint = RuntimeFingerprint(
        page_target_id=page_id,
        page_isolate_id=page_isolate,
        worker_target_id=worker_id,
        worker_isolate_id=worker_isolate,
        module_key=module_key,
        heap_bytes=heap_bytes,
        ram_base=ram_base,
    )
    return fingerprint, light


class RuntimeAuthorityGuard:
    """Keeps exact ROM identity only while cheap browser/runtime generation evidence is unchanged."""

    def __init__(self) -> None:
        self._fingerprint: RuntimeFingerprint | None = None
        self.full_attestations = 0
        self.cheap_health_checks = 0
        self.invalidations = 0

    def clear(self) -> None:
        self._fingerprint = None

    def accept(self, client: CdpClient, choice: TargetChoice) -> RuntimeFingerprint:
        fp, _ = capture_runtime_fingerprint(client, choice)
        self._fingerprint = fp
        self.full_attestations += 1
        return fp

    def healthy(self, client: CdpClient, choice: TargetChoice) -> tuple[bool, str | None, dict[str, Any] | None]:
        previous = self._fingerprint
        if previous is None:
            return False, "no accepted runtime fingerprint", None
        self.cheap_health_checks += 1
        try:
            current, light = capture_runtime_fingerprint(client, choice)
        except (CdpError, OSError, ValueError) as exc:
            self.invalidations += 1
            self._fingerprint = None
            return False, str(exc), None
        if current != previous:
            self.invalidations += 1
            self._fingerprint = None
            return False, "browser/page/Worker/runtime generation changed", {"previous": previous.key(), "current": current.key()}
        return True, None, {
            "path": "cached-runtime-health",
            "identityMode": "cached-exact-world-921031",
            "fullIdentityScan": False,
            "runtimeFingerprint": current.key(),
            "moduleKey": light.get("moduleKey"),
            "heapBytes": light.get("heapBytes"),
            "ramBase": light.get("ramBase"),
            "readOnly": True,
            "ramWrites": 0,
            "inputInjection": False,
        }

    def diagnostics(self) -> dict[str, Any]:
        return {
            "accepted": self._fingerprint is not None,
            "runtimeFingerprint": self._fingerprint.key() if self._fingerprint else None,
            "fullAttestations": self.full_attestations,
            "cheapHealthChecks": self.cheap_health_checks,
            "invalidations": self.invalidations,
            "readOnly": True,
            "ramWrites": 0,
            "inputInjection": False,
        }
