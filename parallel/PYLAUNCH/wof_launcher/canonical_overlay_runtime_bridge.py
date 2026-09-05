from __future__ import annotations

import json
import math
import re
from collections.abc import Mapping, Sequence
from typing import Any

from .production_p1_overlay import HUD_SOURCES
from .render_object_anchor import (
    SCHEMA as ANCHOR_SCHEMA,
    AuthorityBinding,
    DeterministicRenderObjectAnchor,
)

SCHEMA = "wof-alpha-canonical-overlay-runtime-bridge-v1"
TRANSPORT_SCHEMA = "wof-alpha-canonical-anchor-runtime-envelope-input-v1"
MAX_RECORDS = 23
SAFETY = {"readOnly": True, "ramWrites": 0, "inputInjection": False}

_P9_SOURCE = "product/alpha/wof_alpha_canonical_anchor_envelope.js"
_P8_SOURCE = "product/alpha/wof_alpha_canonical_overlay_plan.js"
_HUD_SOURCE = "product/alpha/wof_alpha_hud.js"
_PLAYER_ACTORS = frozenset({"P1", "P2", "P3"})
_ENEMY_ACTOR_RE = re.compile(r"^enemy-slot-(?:[0-9]|1[0-9])$")


def _canonical_hud_sources() -> tuple[str, ...]:
    """Preserve the maintained HUD stack and insert P9/P8 immediately before the HUD."""
    out: list[str] = []
    for rel in HUD_SOURCES:
        if rel == _HUD_SOURCE:
            for required in (_P9_SOURCE, _P8_SOURCE):
                if required not in out:
                    out.append(required)
        if rel not in out:
            out.append(rel)
    if _HUD_SOURCE not in out:
        out.extend(rel for rel in (_P9_SOURCE, _P8_SOURCE, _HUD_SOURCE) if rel not in out)

    required_order = (
        "product/alpha/wof_alpha_enemy_target_labels.js",
        "product/alpha/wof_alpha_player_head_warning.js",
        _P9_SOURCE,
        _P8_SOURCE,
        _HUD_SOURCE,
    )
    positions = [out.index(rel) for rel in required_order]
    if positions != sorted(positions):
        raise RuntimeError("canonical maintained-HUD source order is invalid")
    return tuple(out)


CANONICAL_HUD_SOURCES = _canonical_hud_sources()


class CanonicalOverlayRuntimeBridgeError(RuntimeError):
    pass


class CanonicalOverlayRuntimeBridge:
    """Canonical W3-frame -> deterministic anchor -> P9 transport -> maintained HUD bridge.

    The bridge never creates spatial coordinates. Every point originates from
    DeterministicRenderObjectAnchor under one exact World/runtime/renderer binding.
    """

    def __init__(self, verified_text, *, resolver: DeterministicRenderObjectAnchor | None = None) -> None:
        self._verified_text = verified_text
        self._resolver = resolver or DeterministicRenderObjectAnchor()
        self._session: Any | None = None
        self._binding: AuthorityBinding | None = None
        self._page_target_id: str | None = None
        self._install_mode = "UNBOUND"
        self._last_payload: dict[str, Any] | None = None
        self._last_hud: dict[str, Any] | None = None
        self._last_reason = "NOT_BOUND"
        self._last_error: str | None = None

    @staticmethod
    def _binding_payload(binding: AuthorityBinding) -> dict[str, Any]:
        return {
            "authorityKey": binding.authority_key,
            "runtimeEpoch": binding.runtime_epoch,
            "rendererEpoch": binding.renderer_epoch,
            "worldSha256": binding.world_sha256,
        }

    @staticmethod
    def _validate_sample_at(sample_at: Any) -> float:
        if isinstance(sample_at, bool) or not isinstance(sample_at, (int, float)):
            raise ValueError("sampleAt must be an explicit finite millisecond timestamp")
        value = float(sample_at)
        if not math.isfinite(value) or value < 0:
            raise ValueError("sampleAt must be an explicit finite millisecond timestamp")
        return value

    @staticmethod
    def _normalize_actor_descriptors(actor_descriptors: Any) -> list[dict[str, Any]]:
        if isinstance(actor_descriptors, Mapping):
            rows = list(actor_descriptors.values())
        elif isinstance(actor_descriptors, Sequence) and not isinstance(actor_descriptors, (str, bytes, bytearray)):
            rows = list(actor_descriptors)
        else:
            raise ValueError("actor descriptors must be an explicit list or map")

        if len(rows) > MAX_RECORDS:
            raise ValueError(f"actor descriptor count exceeds {MAX_RECORDS}")

        normalized: list[dict[str, Any]] = []
        seen: set[tuple[str, int]] = set()
        for row in rows:
            if not isinstance(row, Mapping):
                raise ValueError("every actor descriptor must be an object")
            kind = row.get("kind")
            actor = row.get("actor")
            generation = row.get("generation")
            if kind not in {"player", "enemy"}:
                raise ValueError("actor descriptor kind must be player or enemy")
            if not isinstance(actor, str) or not actor:
                raise ValueError("actor descriptor must carry an explicit actor")
            if isinstance(generation, bool) or not isinstance(generation, int) or generation < 0:
                raise ValueError("actor descriptor must carry an explicit non-negative generation")
            if kind == "player" and actor not in _PLAYER_ACTORS:
                raise ValueError("player descriptor actor must be P1, P2, or P3")
            if kind == "enemy" and _ENEMY_ACTOR_RE.fullmatch(actor) is None:
                raise ValueError("enemy descriptor actor must be enemy-slot-N")
            identity = (actor, generation)
            if identity in seen:
                raise ValueError("duplicate actor/generation descriptor")
            seen.add(identity)
            normalized.append({"kind": kind, "actor": actor, "generation": generation})
        return normalized

    @staticmethod
    def _capability_expr() -> str:
        return """(()=>!!(
window.WOFAlphaCanonicalAnchorEnvelope?.normalizeEnvelope&&
window.WOFAlphaCanonicalOverlayPlan?.buildCanonicalPlan&&
window.WOFALPHAHUD&&
typeof window.WOFALPHAHUD.bindCanonicalOverlayAuthority==='function'&&
typeof window.WOFALPHAHUD.ingestCanonicalAnchorEnvelope==='function'&&
typeof window.WOFALPHAHUD.clearCanonicalOverlayAuthority==='function'&&
typeof window.WOFALPHAHUD.canonicalOverlayStatus==='function'
))()"""

    @staticmethod
    def _validate_hud_status(remote: Any, binding: AuthorityBinding, *, expect_bound: bool = True) -> dict[str, Any]:
        if not isinstance(remote, dict):
            raise CanonicalOverlayRuntimeBridgeError("maintained HUD canonical status is malformed")
        if remote.get("readOnly") is not True or remote.get("ramWrites") != 0 or remote.get("inputInjection") is not False:
            raise CanonicalOverlayRuntimeBridgeError("maintained HUD canonical safety boundary mismatch")
        if remote.get("fallback") != "NONE":
            raise CanonicalOverlayRuntimeBridgeError("maintained HUD canonical fallback boundary mismatch")
        if expect_bound and remote.get("bound") is not True:
            raise CanonicalOverlayRuntimeBridgeError("maintained HUD canonical authority unexpectedly unbound")
        authority = remote.get("authority")
        wanted = CanonicalOverlayRuntimeBridge._binding_payload(binding)
        if expect_bound:
            if not isinstance(authority, dict):
                raise CanonicalOverlayRuntimeBridgeError("maintained HUD canonical authority status missing")
            for key in ("authorityKey", "runtimeEpoch", "rendererEpoch", "worldSha256"):
                if authority.get(key) != wanted.get(key):
                    raise CanonicalOverlayRuntimeBridgeError(
                        f"maintained HUD canonical authority mismatch: {key}"
                    )
        return dict(remote)

    def _remote_clear(self, reason: str) -> None:
        if not self._session:
            return
        try:
            self._session.evaluate(
                "/*WOF_P10_CLEAR*/(()=>{const h=window.WOFALPHAHUD;"
                "if(!h||typeof h.clearCanonicalOverlayAuthority!=='function')return null;"
                f"return h.clearCanonicalOverlayAuthority({json.dumps(str(reason or 'AUTHORITY_REVOKED'))});}})()",
                timeout=5.0,
            )
        except Exception:
            pass

    def bind(
        self,
        client: Any,
        page_target_id: str,
        binding: AuthorityBinding,
    ) -> dict[str, Any]:
        if not isinstance(binding, AuthorityBinding) or not binding.valid():
            raise ValueError("invalid exact World/runtime/renderer authority binding")
        if not isinstance(page_target_id, str) or not page_target_id:
            raise ValueError("explicit page target id is required")

        self.revoke("CANONICAL_REBIND")
        session = client.attach(page_target_id)
        self._session = session
        try:
            session.request("Runtime.enable")
            capable = session.evaluate(self._capability_expr(), timeout=5.0)
            if capable is not True:
                runtime_epoch = binding.runtime_epoch
                prep = (
                    "(()=>{const c=window.__WOF_ALPHA_CONFIG,t=window.__WOF_ALPHA_TRANSPORT_V1;"
                    "const ok=!!(c&&c.release==='wof-alpha-rc3'&&typeof c.session==='string'&&c.session.length>=16&&"
                    "typeof c.channel==='string'&&t&&t.version==='wof-alpha-safe-transport-v1'&&typeof t.matches==='function');"
                    "if(ok)return 'PRESERVED_CONFIG';"
                    f"const session={json.dumps(runtime_epoch)},channel={json.dumps('wof-alpha-canonical-direct-'+runtime_epoch)};"
                    "window.__WOF_ALPHA_CONFIG={release:'wof-alpha-rc3',session,channel};"
                    "window.__WOF_ALPHA_TRANSPORT_V1={version:'wof-alpha-safe-transport-v1',matches:m=>!!m&&m.session===session};"
                    "return 'DIRECT_CONFIG';})()"
                )
                self._install_mode = str(session.evaluate(prep, timeout=5.0) or "DIRECT_CONFIG")
                for rel in CANONICAL_HUD_SOURCES:
                    source = self._verified_text(rel)
                    session.evaluate(f"(0,eval)({json.dumps(source)});true", timeout=15.0)
                capable = session.evaluate(self._capability_expr(), timeout=5.0)
            else:
                self._install_mode = "EXISTING_PRODUCTION_HUD"

            if capable is not True:
                raise CanonicalOverlayRuntimeBridgeError("maintained HUD canonical API missing after source injection")

            binding_payload = self._binding_payload(binding)
            remote = session.evaluate(
                "/*WOF_P10_BIND*/(()=>{const h=window.WOFALPHAHUD;"
                "if(!h||typeof h.bindCanonicalOverlayAuthority!=='function')return null;"
                f"return h.bindCanonicalOverlayAuthority({json.dumps(binding_payload, separators=(',', ':'))});}})()",
                timeout=5.0,
            )
            self._validate_hud_status(remote, binding)
            self._resolver.bind(binding)
        except Exception as exc:
            self._remote_clear("CANONICAL_BIND_FAILED")
            self._resolver.revoke()
            try:
                session.close()
            except Exception:
                pass
            self._session = None
            self._binding = None
            self._page_target_id = None
            self._last_payload = None
            self._last_hud = None
            self._last_reason = "CANONICAL_BIND_FAILED"
            self._last_error = str(exc)
            if isinstance(exc, CanonicalOverlayRuntimeBridgeError):
                raise
            raise CanonicalOverlayRuntimeBridgeError(f"canonical overlay bind failed: {exc}") from exc

        self._binding = binding
        self._page_target_id = page_target_id
        self._last_payload = None
        self._last_hud = dict(remote)
        self._last_reason = "BOUND_WAITING_FOR_FRAME"
        self._last_error = None
        return self.status()

    def ingest_frame(
        self,
        frame: dict[str, Any],
        actor_descriptors: Any,
        *,
        sample_at: int | float,
    ) -> dict[str, Any]:
        binding = self._binding
        if binding is None or self._session is None:
            self._last_reason = "NO_AUTHORITY_BINDING"
            return self.status()

        try:
            sample_at_value = self._validate_sample_at(sample_at)
            descriptors = self._normalize_actor_descriptors(actor_descriptors)
        except ValueError as exc:
            self.revoke("INVALID_CANONICAL_TRANSPORT_INPUT")
            self._last_error = str(exc)
            return self.status()

        records: list[dict[str, Any]] = []
        binding_payload = self._binding_payload(binding)
        for descriptor in descriptors:
            resolved = self._resolver.resolve(
                frame,
                actor=descriptor["actor"],
                generation=descriptor["generation"],
            )
            state = resolved.get("state")
            if state not in {"READY", "SUPPRESSED"}:
                self.revoke("CANONICAL_RESOLVER_INVALID_STATE")
                self._last_error = "canonical resolver returned neither READY nor SUPPRESSED"
                return self.status()
            if state == "SUPPRESSED" and isinstance(resolved.get("anchor"), dict):
                self.revoke("SUPPRESSED_FALLBACK_POSITION_FORBIDDEN")
                self._last_error = "suppressed canonical resolver output carried coordinates"
                return self.status()
            records.append(
                {
                    **descriptor,
                    "sampleAt": sample_at_value,
                    **binding_payload,
                    "canonicalAnchor": dict(resolved),
                }
            )

        payload = {
            "schema": TRANSPORT_SCHEMA,
            "authorityBinding": binding_payload,
            "records": records,
        }
        try:
            remote = self._session.evaluate(
                "/*WOF_P10_INGEST*/(()=>{const h=window.WOFALPHAHUD;"
                "if(!h||typeof h.ingestCanonicalAnchorEnvelope!=='function')return null;"
                f"return h.ingestCanonicalAnchorEnvelope({json.dumps(payload, separators=(',', ':'))});}})()",
                timeout=5.0,
            )
            remote = self._validate_hud_status(remote, binding)
        except Exception as exc:
            self._remote_clear("CANONICAL_HUD_INGEST_FAILED")
            self._resolver.revoke()
            try:
                self._session.close()
            except Exception:
                pass
            self._session = None
            self._binding = None
            self._page_target_id = None
            self._last_payload = None
            self._last_hud = None
            self._last_reason = "CANONICAL_HUD_INGEST_FAILED"
            self._last_error = str(exc)
            return self.status()

        self._last_payload = payload
        self._last_hud = remote
        self._last_reason = str(remote.get("reason") or remote.get("state") or "CANONICAL_TRANSPORT_ACCEPTED")
        self._last_error = None
        return self.status()

    def revoke(self, reason: str = "CANONICAL_AUTHORITY_REVOKED") -> dict[str, Any]:
        self._remote_clear(reason)
        self._resolver.revoke()
        if self._session:
            try:
                self._session.close()
            except Exception:
                pass
        self._session = None
        self._binding = None
        self._page_target_id = None
        self._last_payload = None
        self._last_hud = None
        self._install_mode = "UNBOUND"
        self._last_reason = str(reason or "CANONICAL_AUTHORITY_REVOKED")
        self._last_error = None
        return self.status()

    def status(self) -> dict[str, Any]:
        binding = self._binding
        payload = self._last_payload
        records = payload.get("records") if isinstance(payload, dict) else []
        ready_count = sum(
            1
            for row in records or []
            if isinstance(row, dict) and isinstance(row.get("canonicalAnchor"), dict)
            and row["canonicalAnchor"].get("state") == "READY"
        )
        suppressed_count = sum(
            1
            for row in records or []
            if isinstance(row, dict) and isinstance(row.get("canonicalAnchor"), dict)
            and row["canonicalAnchor"].get("state") == "SUPPRESSED"
        )
        remote_state = self._last_hud.get("state") if isinstance(self._last_hud, dict) else None
        return {
            "schema": SCHEMA,
            "state": remote_state if remote_state in {"READY", "SUPPRESSED"} else "SUPPRESSED",
            "reason": self._last_reason,
            "error": self._last_error,
            "bound": binding is not None and self._session is not None,
            "pageTargetId": self._page_target_id,
            "authorityBinding": self._binding_payload(binding) if binding else None,
            "installMode": self._install_mode,
            "recordCount": len(records or []),
            "readyRecordCount": ready_count,
            "suppressedRecordCount": suppressed_count,
            "lastPayload": payload,
            "hud": dict(self._last_hud) if isinstance(self._last_hud, dict) else None,
            "positionAuthority": ANCHOR_SCHEMA,
            "legacyPositionFallback": False,
            **SAFETY,
        }

    def dispose(self) -> None:
        self.revoke("CANONICAL_BRIDGE_DISPOSED")
