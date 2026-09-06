from __future__ import annotations

import copy
import hashlib
import json
import os
import secrets
from pathlib import Path
from typing import Any, Callable, Mapping

from .alpha_runtime import AlphaRuntimeManager
from .auto_baseline_hud import AutoBaselineHud, AutoBaselineHudError
from .cdp import CdpClient, CdpSession

SCHEMA = "wof-alpha-p45-live-diagnostic-staging-v1"
GATE_ENV = "WOF_ALPHA_P45_LIVE_DIAGNOSTIC_STAGING"
P39_CLASSIFICATION = "UNVERIFIED_AUTO_BASELINE"
P42_CLASSIFICATION = "BOUNDED_LIVE_DIAGNOSTIC_MAPPING_ONLY"
P39_TESTED_COMMIT = "ac5387f00d8c2382dcf3ed435ffcfa0acc1a2f05"
P42_TESTED_COMMIT = "7b523187a955179b04155b758847c82aaf569a0d"
P42_SOURCE = "parallel/RENDER_AUTHORITY_V2/gstyphoon_renderer_submit_correlation_probe.js"
P39_RUNTIME_SOURCE = "parallel/PYLAUNCH/wof_launcher/auto_baseline_hud.py"
INJECTION_ORDER = ("P39_AUTO_BASELINE_HUD", "P42_RAW_CORRELATION_PROBE")
SAFETY = {"readOnly": True, "ramWrites": 0, "inputInjection": False}
AUTHORITY_ELIGIBILITY = {
    "p29Pass": False,
    "p32NativeMarkerQualification": False,
    "p36RendererSourceTrace": False,
    "retry": False,
    "promotion": False,
}

# Git blob ids are pinned to the exact bytes accepted by the P39/P42 terminal
# results. The staging gate refuses to inject a checkout that has drifted.
ACCEPTED_BLOBS = {
    P39_RUNTIME_SOURCE: "05a1a6e8632f62dac6ff9bedf8897b3f2df6e685",
    "parallel/AUTO_MARKER_BASELINE/native_marker_auto_acquisition_baseline.js": "2a0094b3588d4a27c8c7a6f9940b8a3b1941f8c4",
    "product/alpha/wof_alpha_auto_baseline_hud_adapter.js": "933f35389bfbd3337bde31906707919fd7a3f626",
    "product/alpha/wof_alpha_auto_baseline_visible_hud.js": "97b1ed594722a8539f21c76f7e44ec01e460ef26",
    P42_SOURCE: "32b9c50e8a72de1a097b8ce5dc91b69bdcef0219",
}


class LiveDiagnosticStagingError(RuntimeError):
    pass


def _git_blob_sha(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def _binding_valid(binding: Mapping[str, Any] | None) -> bool:
    if not isinstance(binding, Mapping):
        return False
    return all(isinstance(binding.get(key), str) and bool(binding.get(key)) for key in ("runtimeEpoch", "rendererEpoch", "authorityKey"))


def _same_binding(a: Mapping[str, Any] | None, b: Mapping[str, Any] | None) -> bool:
    return _binding_valid(a) and _binding_valid(b) and all(a.get(key) == b.get(key) for key in ("runtimeEpoch", "rendererEpoch", "authorityKey"))


class P45LiveDiagnosticStagingRuntime:
    """Default-off P39/P42 staging wrapper around the maintained Alpha runtime.

    The wrapped AlphaRuntimeManager remains the sole production runtime/authority
    implementation. When the explicit P45 gate is off every public lifecycle call
    simply delegates to that runtime and no diagnostic source is read or injected.

    When enabled, P39 is installed first and P42 second. P42 receives a dedicated
    diagnostic renderer epoch bound to the current runtimeEpoch/authorityKey. This
    epoch is correlation identity only and is never written into canonical W3/P36
    authority state.
    """

    def __init__(
        self,
        root: Path,
        *,
        enabled: bool = False,
        runtime: AlphaRuntimeManager | None = None,
        hud_factory: Callable[[Callable[[str], str]], AutoBaselineHud] = AutoBaselineHud,
        renderer_epoch_factory: Callable[[], str] | None = None,
    ) -> None:
        self.root = Path(root).resolve()
        self.enabled = bool(enabled)
        self.runtime = runtime or AlphaRuntimeManager(self.root)
        self._hud_factory = hud_factory
        self._renderer_epoch_factory = renderer_epoch_factory or (lambda: secrets.token_hex(16))
        self._hud: AutoBaselineHud | None = None
        self._p42_session: CdpSession | None = None
        self._page_target_id: str | None = None
        self._binding: dict[str, str] | None = None
        self._last_readout: dict[str, Any] | None = None
        self._state = "GATE_OFF" if not self.enabled else "WAITING_FOR_ALPHA_RUNTIME"
        self._reason = "STAGING_GATE_CLOSED" if not self.enabled else "WAITING_FOR_ACCEPTED_RUNTIME"

    @classmethod
    def from_env(cls, root: Path, **kwargs: Any) -> "P45LiveDiagnosticStagingRuntime":
        return cls(root, enabled=os.environ.get(GATE_ENV) == "1", **kwargs)

    def _accepted_text(self, rel: str) -> str:
        wanted = ACCEPTED_BLOBS.get(rel)
        if not wanted:
            raise LiveDiagnosticStagingError(f"P45 source is not accepted/pinned: {rel}")
        path = self.root / rel
        try:
            data = path.read_bytes()
        except OSError as exc:
            raise LiveDiagnosticStagingError(f"P45 accepted source missing: {rel}") from exc
        actual = _git_blob_sha(data)
        if actual != wanted:
            raise LiveDiagnosticStagingError(
                f"P45 accepted source byte drift: {rel} expected={wanted} actual={actual}"
            )
        try:
            return data.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise LiveDiagnosticStagingError(f"P45 accepted source is not UTF-8: {rel}") from exc

    def _verify_p39_runtime_module(self) -> None:
        # AutoBaselineHud is imported Python, so verify its checked-out implementation
        # separately before using it. Its injected dependencies are verified by the
        # reader supplied to AutoBaselineHud.
        self._accepted_text(P39_RUNTIME_SOURCE)

    @staticmethod
    def _page_id(choice: Any) -> str:
        page = getattr(choice, "page", None)
        return str(page.get("targetId") or "") if isinstance(page, dict) else ""

    @staticmethod
    def _validate_runtime_status(status: Any, authority_key: str) -> tuple[str, str]:
        if not isinstance(status, dict) or status.get("running") is not True:
            raise LiveDiagnosticStagingError("P45 requires maintained Alpha runtime running=true")
        runtime_epoch = status.get("runtimeEpoch")
        if not isinstance(runtime_epoch, str) or len(runtime_epoch) < 16:
            raise LiveDiagnosticStagingError("P45 runtimeEpoch missing/invalid")
        if status.get("authorityKey") != authority_key:
            raise LiveDiagnosticStagingError("P45 authorityKey does not match maintained Alpha runtime")
        return runtime_epoch, authority_key

    def _p42_eval(self, expression: str, *, timeout: float = 8.0) -> Any:
        if self._p42_session is None:
            raise LiveDiagnosticStagingError("P42 diagnostic session is not bound")
        return self._p42_session.evaluate(expression, timeout=timeout)

    def _install(self, client: CdpClient, page_target_id: str, runtime_epoch: str, authority_key: str) -> None:
        self._teardown_diagnostics("P45_DIAGNOSTIC_REBOUND", preserve=True)
        self._verify_p39_runtime_module()
        renderer_epoch = self._renderer_epoch_factory()
        binding = {
            "runtimeEpoch": runtime_epoch,
            "rendererEpoch": renderer_epoch,
            "authorityKey": authority_key,
        }
        if not _binding_valid(binding) or len(renderer_epoch) < 16:
            raise LiveDiagnosticStagingError("P45 diagnostic rendererEpoch factory returned invalid identity")

        hud = self._hud_factory(self._accepted_text)
        session: CdpSession | None = None
        try:
            # Deterministic order is contract-significant: P42's default correlation
            # provider reads P39's status, so P39 must exist before P42 starts.
            hud.bind(client, page_target_id)
            session = client.attach(page_target_id)
            session.request("Runtime.enable")
            p42_source = self._accepted_text(P42_SOURCE)
            session.evaluate(
                "(()=>{try{window.__WOF_P45_P42_PROBE_V1?.stop?.('P45_REBIND');}catch(_){}"
                "try{delete window.__WOF_P45_P42_PROBE_V1;}catch(_){}"
                "try{delete window.__WOF_P45_LIVE_DIAGNOSTIC_BINDING_V1;}catch(_){}return true;})()",
                timeout=4.0,
            )
            session.evaluate(f"(0,eval)({json.dumps(p42_source)});true", timeout=15.0)
            remote = session.evaluate(
                "(()=>{"
                f"const binding={json.dumps(binding)};"
                "window.__WOF_P45_LIVE_DIAGNOSTIC_BINDING_V1=Object.freeze({...binding});"
                "const api=window.WOFGStyphoonRendererCorrelationProbeP42;"
                "if(!api||typeof api.createProbe!=='function')throw new Error('P42 accepted probe API missing');"
                "const probe=api.createProbe({"
                "bindingProvider:()=>window.__WOF_P45_LIVE_DIAGNOSTIC_BINDING_V1,"
                "baselineProvider:()=>window.WOFALPHAAUTOBASELINEHUD?.status?.()||null"
                "});"
                "window.__WOF_P45_P42_PROBE_V1=probe;"
                "return probe.start(binding);"
                "})()",
                timeout=8.0,
            )
            self._validate_p42_status(remote, binding)
        except Exception as exc:
            try:
                if session is not None:
                    session.evaluate("window.__WOF_P45_P42_PROBE_V1?.stop?.('P45_INSTALL_FAILED');true", timeout=3.0)
            except Exception:
                pass
            try:
                if session is not None:
                    session.close()
            except Exception:
                pass
            try:
                hud.dispose()
            except Exception:
                pass
            if isinstance(exc, LiveDiagnosticStagingError):
                raise
            raise LiveDiagnosticStagingError(f"P45 staging diagnostic install failed: {exc}") from exc

        self._hud = hud
        self._p42_session = session
        self._page_target_id = page_target_id
        self._binding = binding
        self._last_readout = None
        self._state = "OBSERVING"
        self._reason = "P39_THEN_P42_BOUND"

    @staticmethod
    def _validate_p42_status(remote: Any, binding: Mapping[str, Any]) -> dict[str, Any]:
        if not isinstance(remote, dict) or remote.get("schema") != "wof-gstyphoon-renderer-correlation-probe-v1":
            raise LiveDiagnosticStagingError("P42 diagnostic status schema invalid")
        if remote.get("authorityEligible") is not False:
            raise LiveDiagnosticStagingError("P42 authority boundary invalid")
        if remote.get("readOnly") is not True or remote.get("ramWrites") != 0 or remote.get("inputInjection") is not False:
            raise LiveDiagnosticStagingError("P42 safety boundary invalid")
        if not _same_binding(remote.get("binding"), binding):
            raise LiveDiagnosticStagingError("P42 status binding stale/mixed")
        return dict(remote)

    def _binding_fresh(self) -> bool:
        if self._p42_session is None or self._binding is None:
            return False
        try:
            remote = self._p42_eval(
                "(()=>{const b=window.__WOF_P45_LIVE_DIAGNOSTIC_BINDING_V1;return b?{runtimeEpoch:b.runtimeEpoch,rendererEpoch:b.rendererEpoch,authorityKey:b.authorityKey}:null;})()",
                timeout=4.0,
            )
        except Exception:
            return False
        return _same_binding(remote, self._binding)

    @staticmethod
    def _p39_lifecycle(status: Mapping[str, Any]) -> dict[str, Any]:
        automatic = status.get("automaticPlayers") if isinstance(status.get("automaticPlayers"), list) else ["P1", "P2", "P3"]
        visible = status.get("visiblePlayers") if isinstance(status.get("visiblePlayers"), list) else []
        controller = status.get("controller") if isinstance(status.get("controller"), dict) else {}
        tracks = controller.get("tracks") if isinstance(controller.get("tracks"), dict) else {}
        lost = [p for p in automatic if isinstance(tracks.get(p), dict) and tracks[p].get("state") == "LOST"]
        ambiguous = controller.get("envelopeState") == "AMBIGUOUS" or any(
            isinstance(tracks.get(p), dict) and tracks[p].get("state") == "AMBIGUOUS" for p in automatic
        )
        stale = controller.get("visibleFresh") is False or status.get("state") == "STALE_OR_UNAVAILABLE"
        reacquire = {
            p: int(tracks[p].get("reacquireCount") or 0)
            for p in automatic
            if isinstance(tracks.get(p), dict)
        }
        return {
            "visiblePlayers": list(visible),
            "hiddenPlayers": [p for p in automatic if p not in visible],
            "lostPlayers": lost,
            "stale": bool(stale),
            "ambiguous": bool(ambiguous),
            "reacquireCountByPlayer": reacquire,
            "controllerState": controller.get("state"),
            "envelopeState": controller.get("envelopeState"),
        }

    def _collect(self, *, seal: bool = False, seal_reason: str = "P45_BOUNDED_DIAGNOSTIC_SEAL") -> dict[str, Any]:
        if not self.enabled:
            return {"schema": SCHEMA, "enabled": False, "state": "GATE_OFF", "reason": "STAGING_GATE_CLOSED"}
        if self._hud is None or self._p42_session is None or self._binding is None:
            return {
                "schema": SCHEMA,
                "enabled": True,
                "state": self._state,
                "reason": self._reason,
                "injectionOrder": list(INJECTION_ORDER),
                "p39Classification": P39_CLASSIFICATION,
                "p42Classification": P42_CLASSIFICATION,
                "authorityEligibility": dict(AUTHORITY_ELIGIBILITY),
                "safety": dict(SAFETY),
            }
        if not self._binding_fresh():
            self._state = "REJECTED"
            self._reason = "STALE_OR_MIXED_AUTHORITY_BINDING"
            self._teardown_diagnostics(self._reason, preserve=True)
            if self._last_readout is not None:
                return copy.deepcopy(self._last_readout)
            raise LiveDiagnosticStagingError(self._reason)

        try:
            p39 = self._hud.refresh()
            if p39.get("classification") != P39_CLASSIFICATION:
                raise LiveDiagnosticStagingError("P39 classification drift")
            if seal:
                self._p42_eval(
                    f"window.__WOF_P45_P42_PROBE_V1?.stop?.({json.dumps(str(seal_reason))})||null",
                    timeout=5.0,
                )
            p42_status = self._validate_p42_status(
                self._p42_eval("window.__WOF_P45_P42_PROBE_V1?.status?.()||null", timeout=5.0),
                self._binding,
            )
            raw_bundle = self._p42_eval("window.__WOF_P45_P42_PROBE_V1?.result?.()||null", timeout=12.0)
        except Exception as exc:
            if isinstance(exc, LiveDiagnosticStagingError):
                raise
            raise LiveDiagnosticStagingError(f"P45 diagnostic readout failed: {exc}") from exc
        if not isinstance(raw_bundle, dict) or raw_bundle.get("schema") != "wof-gstyphoon-renderer-correlation-probe-v1":
            raise LiveDiagnosticStagingError("P42 raw bundle missing/invalid")
        if raw_bundle.get("authorityEligible") is not False or not _same_binding(raw_bundle.get("binding"), self._binding):
            raise LiveDiagnosticStagingError("P42 raw bundle authority/binding boundary invalid")

        self._state = str(p42_status.get("state") or "OBSERVING")
        self._reason = str(p42_status.get("reason") or self._reason)
        out = {
            "schema": SCHEMA,
            "enabled": True,
            "state": self._state,
            "reason": self._reason,
            "zeroClick": True,
            "manualSeedRequired": False,
            "manualAvatarSelectionRequired": False,
            "injectionOrder": list(INJECTION_ORDER),
            "binding": {
                **self._binding,
                "rendererEpochSource": "P45_DIAGNOSTIC_SESSION_ONLY",
                "productionRendererAuthority": False,
            },
            "p39": {
                "classification": P39_CLASSIFICATION,
                "testedCommit": P39_TESTED_COMMIT,
                "status": p39,
                "lifecycle": self._p39_lifecycle(p39),
            },
            "p42": {
                "classification": P42_CLASSIFICATION,
                "testedCommit": P42_TESTED_COMMIT,
                "state": p42_status,
                # Intentionally pass through the complete result object. No candidate
                # ranking, sorting, slicing, selection, or record deletion is done here.
                "rawBundle": raw_bundle,
                "sealReason": raw_bundle.get("reason"),
                "teardown": raw_bundle.get("teardown"),
            },
            "authorityEligibility": dict(AUTHORITY_ELIGIBILITY),
            "productAuthority": "NONE_DIAGNOSTIC_ONLY",
            "safety": dict(SAFETY),
        }
        self._last_readout = copy.deepcopy(out)
        return out

    def ensure_running(self, client: CdpClient, choice: Any, authority_key: str) -> dict[str, Any]:
        status = self.runtime.ensure_running(client, choice, authority_key)
        if not self.enabled:
            return status
        page_target_id = self._page_id(choice)
        if not page_target_id:
            raise LiveDiagnosticStagingError("P45 accepted page target missing")
        runtime_epoch, exact_authority = self._validate_runtime_status(status, authority_key)
        wanted_base = {"runtimeEpoch": runtime_epoch, "authorityKey": exact_authority}
        current_ok = (
            self._binding is not None
            and self._page_target_id == page_target_id
            and self._binding.get("runtimeEpoch") == wanted_base["runtimeEpoch"]
            and self._binding.get("authorityKey") == wanted_base["authorityKey"]
        )
        if not current_ok:
            self._install(client, page_target_id, runtime_epoch, exact_authority)
        diagnostic = self._collect()
        merged = dict(status)
        merged["liveDiagnosticStaging"] = diagnostic
        return merged

    def ingest_live_diagnostic_frame(self, frame: Mapping[str, Any], timestamp_ms: float) -> dict[str, Any]:
        if not self.enabled:
            raise LiveDiagnosticStagingError("P45 staging diagnostic gate is off")
        if self._hud is None:
            raise LiveDiagnosticStagingError("P45 staging diagnostic is not bound")
        self._hud.ingest_frame(frame, timestamp_ms)
        return self._collect()

    def live_diagnostic_readout(self, *, seal: bool = False, reason: str = "P45_BOUNDED_DIAGNOSTIC_SEAL") -> dict[str, Any]:
        if not self.enabled and self._last_readout is None:
            return {"schema": SCHEMA, "enabled": False, "state": "GATE_OFF", "reason": "STAGING_GATE_CLOSED"}
        if self._hud is None and self._last_readout is not None:
            return copy.deepcopy(self._last_readout)
        return self._collect(seal=seal, seal_reason=reason)

    def _teardown_diagnostics(self, reason: str, *, preserve: bool) -> None:
        if self._p42_session is not None and self._binding is not None:
            try:
                if self._binding_fresh():
                    self._p42_eval(
                        f"window.__WOF_P45_P42_PROBE_V1?.stop?.({json.dumps(str(reason))})||null",
                        timeout=5.0,
                    )
                    if preserve:
                        try:
                            self._collect()
                        except Exception:
                            pass
            except Exception:
                pass
            try:
                self._p42_session.evaluate(
                    "(()=>{try{delete window.__WOF_P45_P42_PROBE_V1;}catch(_){}"
                    "try{delete window.__WOF_P45_LIVE_DIAGNOSTIC_BINDING_V1;}catch(_){}return true;})()",
                    timeout=3.0,
                )
            except Exception:
                pass
            try:
                self._p42_session.close()
            except Exception:
                pass
        if self._hud is not None:
            try:
                self._hud.disable()
            except Exception:
                pass
            try:
                self._hud.dispose()
            except Exception:
                pass
        self._p42_session = None
        self._hud = None
        self._page_target_id = None
        self._binding = None
        self._state = "SEALED" if preserve else "WAITING_FOR_ALPHA_RUNTIME"
        self._reason = str(reason)

    def stop_live_diagnostic(self, reason: str = "P45_BOUNDED_DIAGNOSTIC_COMPLETE") -> dict[str, Any]:
        if not self.enabled:
            return self.live_diagnostic_readout()
        if self._hud is not None:
            try:
                self._collect(seal=True, seal_reason=reason)
            finally:
                self._teardown_diagnostics(reason, preserve=True)
        return self.live_diagnostic_readout()

    def revoke(self, client: CdpClient | None = None) -> None:
        if self.enabled:
            self._teardown_diagnostics("P45_ALPHA_RUNTIME_REVOKED", preserve=True)
        self.runtime.revoke(client)

    def poll_projection_recovery(self, *args: Any, **kwargs: Any) -> Any:
        return self.runtime.poll_projection_recovery(*args, **kwargs)

    def ingest_canonical_w3_frame(self, *args: Any, **kwargs: Any) -> Any:
        return self.runtime.ingest_canonical_w3_frame(*args, **kwargs)

    def clear_canonical_overlay(self, *args: Any, **kwargs: Any) -> Any:
        return self.runtime.clear_canonical_overlay(*args, **kwargs)

    def projection_proof_result(self) -> Any:
        return self.runtime.projection_proof_result()

    def status(self) -> dict[str, Any]:
        status = self.runtime.status()
        if not self.enabled:
            return status
        merged = dict(status)
        merged["liveDiagnosticStaging"] = self.live_diagnostic_readout()
        return merged

    def __getattr__(self, name: str) -> Any:
        return getattr(self.runtime, name)
