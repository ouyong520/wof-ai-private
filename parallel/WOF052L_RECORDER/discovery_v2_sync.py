from __future__ import annotations

from typing import Any

import discovery_v2_sync_base as _base


# Keep the previous Discovery V2 implementation intact as the compatibility
# base, then narrow identity authority to the currently attached runtime.
for _name in dir(_base):
    if not _name.startswith("__"):
        globals()[_name] = getattr(_base, _name)

_BASE_PROBE_SESSION = _base._probe_session


def _runtime_identity_token(session: Any) -> tuple[Any, ...]:
    """Return a token scoped to the current CDP runtime/session lifecycle."""
    session_id = str(getattr(session, "session_id", "") or "")
    client = getattr(session, "client", None)
    if session_id:
        return ("cdp-session", client, session_id)
    # Test doubles and unusual adapters may not expose a CDP session id. In
    # that case only the exact same live session object may reuse authority.
    return ("session-object", session)


def _probe_session(manager: Any, session: Any, target: dict[str, Any]):
    """Never let targetId alone carry exact-World authority across runtimes."""
    target_id = str(target.get("targetId") or "")
    cache = getattr(manager, "_wof052l_identity_cache", None)
    if not isinstance(cache, dict):
        cache = {}
        manager._wof052l_identity_cache = cache

    lifecycle = getattr(manager, "_wof052l_identity_lifecycle", None)
    if not isinstance(lifecycle, dict):
        lifecycle = {}
        manager._wof052l_identity_lifecycle = lifecycle

    runtime_token = _runtime_identity_token(session)
    if lifecycle.get(target_id) != runtime_token:
        # A new/recreated/re-attached runtime must prove World 921031 again.
        cache.pop(target_id, None)
        lifecycle.pop(target_id, None)

    light, identity, status = _BASE_PROBE_SESSION(manager, session, target)

    # The compatibility base only caches structurally valid SHA payloads.
    # Bind any such cache entry to this exact runtime token; wrong identity is
    # still fail-closed and can only be reused by this same session lifecycle.
    if isinstance(cache.get(target_id), dict):
        lifecycle[target_id] = runtime_token
    else:
        lifecycle.pop(target_id, None)

    return light, identity, status


def _sync_base_overrides() -> None:
    """Mirror hardening monkey-patches into the compatibility module globals."""
    for name in ("_worker_compatible", "_page_for_direct"):
        if name in globals():
            setattr(_base, name, globals()[name])


# Legacy scan functions resolve _probe_session in their defining module.
_base._probe_session = _probe_session
