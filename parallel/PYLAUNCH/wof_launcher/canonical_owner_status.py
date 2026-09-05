from __future__ import annotations

from collections.abc import Mapping
from typing import Any

SCHEMA = "wof-alpha-owner-canonical-status-v1"

OWNER_STATES = (
    "WAITING_WOF",
    "VERIFYING_WORLD",
    "CANONICAL_STACK_READY",
    "WAITING_RENDERER_SOURCE",
    "IDENTITY_SUPPRESSED",
    "ANCHORS_SUPPRESSED",
    "ANCHORS_READY",
    "HUD_INGEST_ACCEPTED",
    "CANONICAL_RUNTIME_ERROR",
)

STATE_LABEL_ZH = {
    "WAITING_WOF": "等待 WOF",
    "VERIFYING_WORLD": "正在确认 World",
    "CANONICAL_STACK_READY": "Alpha 运行时就绪",
    "WAITING_RENDERER_SOURCE": "等待渲染坐标来源",
    "IDENTITY_SUPPRESSED": "身份已安全隐藏",
    "ANCHORS_SUPPRESSED": "坐标已安全隐藏",
    "ANCHORS_READY": "canonical anchor READY",
    "HUD_INGEST_ACCEPTED": "HUD 已接收",
    "CANONICAL_RUNTIME_ERROR": "运行时异常",
}

_ERROR_TOKENS = ("ERROR", "FATAL", "EXCEPTION", "FAILED")
_IDENTITY_TOKENS = ("IDENTITY", "ACTOR", "GENERATION", "ASSOCIATION", "CONFLICT")
_RENDERER_WAIT_TOKENS = (
    "WAITING_RENDERER_SOURCE",
    "RENDERER_SOURCE_UNPROVEN",
    "RENDERER_UNPROVEN",
    "SOURCE_UNPROVEN",
    "SOURCE_NOT_PROVEN",
    "W3_SOURCE_UNPROVEN",
    "W3_FRAME_MISSING",
    "NO_W3_FRAME",
    "WAITING_W3_FRAME",
    "WAITING_FOR_W3_FRAME",
    "FRAME_UNAVAILABLE",
    "FRAME_SOURCE_QUALIFICATION",
    "W3_SOURCE_UNAVAILABLE",
    "CANONICAL_W3_SOURCE_UNAVAILABLE",
)
_REVOKE_TOKENS = (
    "REVOK",
    "STALE",
    "EPOCH",
    "AUTHORITY_MISMATCH",
    "AUTHORITY_REPLACED",
    "NOT_BOUND",
    "UNBOUND",
)
_HUD_ACCEPTED_TOKENS = ("HUD_INGEST_ACCEPTED", "INGEST_ACCEPTED", "ACCEPTED")
_READY_TOKENS = ("READY", "ANCHORS_READY", "RESOLVED_READY")
_SUPPRESSED_TOKENS = ("SUPPRESSED", "HIDDEN", "REJECTED")


def _mapping(value: Any) -> Mapping[str, Any] | None:
    return value if isinstance(value, Mapping) else None


def _path(root: Mapping[str, Any] | None, *keys: str) -> Any:
    cur: Any = root
    for key in keys:
        if not isinstance(cur, Mapping):
            return None
        cur = cur.get(key)
    return cur


def _first_mapping(root: Mapping[str, Any] | None, paths: tuple[tuple[str, ...], ...]) -> Mapping[str, Any] | None:
    for path in paths:
        value = _path(root, *path)
        if isinstance(value, Mapping):
            return value
    return None


def _first_value(root: Mapping[str, Any] | None, paths: tuple[tuple[str, ...], ...]) -> Any:
    for path in paths:
        value = _path(root, *path)
        if value is not None:
            return value
    return None


def _token(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip().upper().replace("-", "_").replace(" ", "_")


def _contains(value: Any, needles: tuple[str, ...]) -> bool:
    text = _token(value)
    return any(item in text for item in needles)


def _bool_value(root: Mapping[str, Any] | None, paths: tuple[tuple[str, ...], ...]) -> bool | None:
    value = _first_value(root, paths)
    return value if isinstance(value, bool) else None


def _status_state(block: Mapping[str, Any] | None) -> str:
    if not block:
        return ""
    return _token(
        block.get("state")
        or block.get("currentState")
        or block.get("ingestState")
        or block.get("latestIngestState")
        or block.get("anchorState")
        or block.get("frameState")
        or block.get("status")
    )


def _status_reason(block: Mapping[str, Any] | None) -> str | None:
    if not block:
        return None
    raw = (
        block.get("reason")
        or block.get("currentReason")
        or block.get("ingestReason")
        or block.get("latestIngestReason")
        or block.get("anchorReason")
        or block.get("frameReason")
        or block.get("error")
    )
    if raw is None:
        return None
    text = str(raw).strip()
    return text or None


def _canonical_blocks(alpha: Mapping[str, Any] | None) -> dict[str, Mapping[str, Any] | None]:
    canonical = _first_mapping(alpha, (
        ("canonical",),
        ("canonicalRuntime",),
        ("canonicalLifecycle",),
        ("canonicalStatus",),
        ("canonicalOverlayRuntime",),
        ("canonicalOverlay",),
    ))
    renderer = _first_mapping(canonical, (
        ("rendererSource",),
        ("renderer",),
        ("source",),
    )) or _first_mapping(alpha, (
        ("rendererSource",),
        ("canonicalRendererSource",),
    ))
    identity = _first_mapping(canonical, (
        ("identity",),
        ("registry",),
        ("actorRegistry",),
        ("actorGenerationRegistry",),
    )) or _first_mapping(alpha, (
        ("canonicalIdentity",),
        ("actorRegistry",),
        ("actorGenerationRegistry",),
    ))
    anchors = _first_mapping(canonical, (
        ("anchors",),
        ("anchor",),
        ("resolution",),
        ("currentFrame",),
        ("frame",),
        ("frameResolution",),
    )) or _first_mapping(alpha, (
        ("canonicalAnchors",),
        ("anchorResolution",),
        ("canonicalFrame",),
    ))
    ingest = _first_mapping(canonical, (("latestIngest",), ("ingest",)))
    hud = _first_mapping(canonical, (
        ("bridge", "hud"),
        ("hud",),
        ("hudStatus",),
    )) or _first_mapping(alpha, (
        ("hudCanonicalStatus",),
        ("canonicalHudStatus",),
        ("page", "hudStatus", "canonicalOverlay"),
        ("page", "canonicalOverlayStatus"),
    ))
    return {
        "canonical": canonical,
        "renderer": renderer,
        "identity": identity,
        "anchors": anchors,
        "ingest": ingest,
        "hud": hud,
    }


def _metadata(
    snapshot: Mapping[str, Any],
    alpha: Mapping[str, Any] | None,
    blocks: Mapping[str, Mapping[str, Any] | None],
) -> dict[str, Any]:
    canonical = blocks.get("canonical")
    renderer = blocks.get("renderer")
    hud = blocks.get("hud")
    package_version = snapshot.get("alpha_package_version") or _first_value(alpha, (("packageVersion",),))
    runtime_epoch = snapshot.get("alpha_runtime_epoch") or _first_value(alpha, (("runtimeEpoch",),))
    authority_key = _first_value(canonical, (
        ("authorityKey",),
        ("authority", "key"),
    )) or _first_value(alpha, (("authorityKey",),))
    renderer_epoch = _first_value(renderer, (
        ("rendererEpoch",),
        ("epoch",),
    )) or _first_value(canonical, (("rendererEpoch",),))
    renderer_authority = _first_value(renderer, (
        ("authorityKey",),
        ("authority",),
        ("identity",),
        ("sourceId",),
    )) or _first_value(canonical, (
        ("rendererAuthority",),
        ("rendererAuthorityKey",),
        ("bridge", "authorityBinding"),
        ("positionAuthority",),
    ))
    return {
        "packageVersion": package_version,
        "runtimeEpoch": runtime_epoch,
        "authorityKey": authority_key,
        "rendererEpoch": renderer_epoch,
        "rendererAuthority": renderer_authority,
        "hudCanonicalStatus": dict(hud) if isinstance(hud, Mapping) else None,
    }


def _human(state: str, reason: str | None, snapshot: Mapping[str, Any]) -> str:
    if state == "WAITING_WOF":
        return "等待 WOF"
    if state == "VERIFYING_WORLD":
        return "已找到 WOF，正在确认 World 921031"
    if state == "CANONICAL_STACK_READY":
        if snapshot.get("alpha_running") is True:
            return "Alpha canonical 运行时已就绪，等待当前坐标权威"
        return "已确认 World 921031，正在建立 Alpha 运行时"
    if state == "WAITING_RENDERER_SOURCE":
        return "Alpha 已就绪，等待游戏渲染坐标来源确认"
    if state == "IDENTITY_SUPPRESSED":
        return "角色身份暂时无法唯一确认，提示已安全隐藏"
    if state == "ANCHORS_SUPPRESSED":
        if _contains(reason, _REVOKE_TOKENS):
            return "运行时已撤销旧坐标，正在重新绑定"
        return "当前 canonical 坐标不可安全使用，提示已安全隐藏"
    if state == "ANCHORS_READY":
        return "已取得当前角色 canonical 坐标，正在送入 HUD"
    if state == "HUD_INGEST_ACCEPTED":
        return "HUD 已接收当前提示数据；等待最终实机可见性确认"
    error = snapshot.get("alpha_error") or reason or snapshot.get("last_error")
    return "Alpha 运行时异常" + (f"：{error}" if error else "")


def normalize_owner_status(status: Mapping[str, Any] | Any) -> dict[str, Any]:
    if hasattr(status, "snapshot") and callable(status.snapshot):
        status = status.snapshot()
    if not isinstance(status, Mapping):
        raise TypeError("status must be a mapping or expose snapshot()")

    alpha = _mapping(status.get("alpha_status"))
    blocks = _canonical_blocks(alpha)
    canonical = blocks["canonical"]
    renderer = blocks["renderer"]
    identity = blocks["identity"]
    ingest = blocks["ingest"]
    hud = blocks["hud"]
    metadata = _metadata(status, alpha, blocks)

    browser_ready = status.get("browser_connected") is True
    runtime_authority_ready = all(
        status.get(key) is True
        for key in ("wof_page_found", "worker_found", "wasm_module_found", "heap_found")
    )

    if not browser_ready or not runtime_authority_ready:
        state, reason = "WAITING_WOF", "WOF_RUNTIME_AUTHORITY_NOT_READY"
    elif status.get("world_921031") is not True:
        state, reason = "VERIFYING_WORLD", str(status.get("identity_reason") or "WORLD_921031_NOT_ACCEPTED")
    else:
        canonical_state = _status_state(canonical)
        canonical_reason = _status_reason(canonical)
        renderer_state = _status_state(renderer)
        renderer_reason = _status_reason(renderer)
        identity_state = _status_state(identity)
        identity_reason = _status_reason(identity)
        ingest_state = _status_state(ingest)
        ingest_reason = _status_reason(ingest)
        hud_state = _status_state(hud)
        hud_reason = _status_reason(hud)

        explicit_error = status.get("alpha_error")
        if explicit_error or _contains(canonical_state, _ERROR_TOKENS) or _contains(canonical_reason, _ERROR_TOKENS):
            state, reason = (
                "CANONICAL_RUNTIME_ERROR",
                str(explicit_error or canonical_reason or canonical_state or "CANONICAL_RUNTIME_ERROR"),
            )
        elif (
            _contains(identity_state, _SUPPRESSED_TOKENS)
            or (
                _contains(identity_reason, _IDENTITY_TOKENS)
                and _contains(
                    identity_reason,
                    _SUPPRESSED_TOKENS + _ERROR_TOKENS + ("UNPROVEN", "AMBIGUOUS"),
                )
            )
            or (
                _contains(canonical_state, _SUPPRESSED_TOKENS)
                and _contains(canonical_reason, _IDENTITY_TOKENS)
            )
        ):
            state, reason = (
                "IDENTITY_SUPPRESSED",
                identity_reason or canonical_reason or identity_state or canonical_state or "IDENTITY_SUPPRESSED",
            )
        else:
            renderer_proven = _bool_value(renderer, (
                ("proven",),
                ("qualified",),
                ("sourceQualified",),
            ))
            top_renderer_proven = _bool_value(canonical, (
                ("rendererSourceProven",),
                ("rendererSourceProvenInLatestFrame",),
                ("rendererQualified",),
            ))
            explicit_wait = (
                _contains(renderer_state, _RENDERER_WAIT_TOKENS)
                or _contains(renderer_reason, _RENDERER_WAIT_TOKENS)
                or _contains(canonical_state, _RENDERER_WAIT_TOKENS)
                or _contains(canonical_reason, _RENDERER_WAIT_TOKENS)
                or canonical_state == "WAITING"
                or (
                    renderer_proven is False
                    and _contains(renderer_reason or canonical_reason, ("SOURCE", "W3", "FRAME"))
                )
                or (
                    top_renderer_proven is False
                    and _contains(canonical_reason, ("SOURCE", "W3", "FRAME"))
                )
            )

            ingest_hud_state = _token(ingest.get("hudState")) if isinstance(ingest, Mapping) else ""
            ingest_ready_count = ingest.get("readyRecordCount") if isinstance(ingest, Mapping) else None
            hud_accepted = (
                _contains(hud_state, _HUD_ACCEPTED_TOKENS)
                or _bool_value(hud, (
                    ("accepted",),
                    ("ingestAccepted",),
                    ("lastIngestAccepted",),
                )) is True
                or (
                    hud_state == "READY"
                    and (
                        ingest_hud_state == "READY"
                        or (isinstance(ingest_ready_count, int) and ingest_ready_count > 0)
                    )
                )
            )

            explicit_anchors = _first_mapping(canonical, (
                ("anchors",),
                ("anchor",),
                ("resolution",),
                ("currentFrame",),
                ("frame",),
            ))
            explicit_anchor_state = _status_state(explicit_anchors)
            explicit_anchor_reason = _status_reason(explicit_anchors)
            anchors_ready = (
                _contains(explicit_anchor_state, _READY_TOKENS)
                or (
                    canonical_state == "READY"
                    and _contains(canonical_reason, ("ANCHOR", "CANONICAL_ANCHORS_READY"))
                )
            )
            anchors_suppressed = (
                _contains(explicit_anchor_state, _SUPPRESSED_TOKENS)
                or _contains(canonical_state, ("ANCHORS_SUPPRESSED", "REVOKED"))
                or _contains(explicit_anchor_reason or canonical_reason, _REVOKE_TOKENS)
                or canonical_state == "SUPPRESSED"
            )

            if explicit_wait:
                state, reason = (
                    "WAITING_RENDERER_SOURCE",
                    renderer_reason or canonical_reason or renderer_state or canonical_state or "RENDERER_SOURCE_UNPROVEN",
                )
            elif hud_accepted:
                state, reason = (
                    "HUD_INGEST_ACCEPTED",
                    hud_reason or ingest_reason or hud_state or ingest_state or "HUD_INGEST_ACCEPTED",
                )
            elif anchors_ready:
                state, reason = (
                    "ANCHORS_READY",
                    explicit_anchor_reason or canonical_reason or explicit_anchor_state or canonical_state or "ANCHORS_READY",
                )
            elif anchors_suppressed:
                state, reason = (
                    "ANCHORS_SUPPRESSED",
                    explicit_anchor_reason or canonical_reason or explicit_anchor_state or canonical_state or "ANCHORS_SUPPRESSED",
                )
            else:
                capable = _bool_value(alpha, (
                    ("canonicalOverlayCapable",),
                    ("canonicalCapable",),
                    ("page", "canonicalOverlayCapable"),
                ))
                if capable is None:
                    capable = _bool_value(canonical, (
                        ("capable",),
                        ("installed",),
                        ("stackReady",),
                        ("capabilityPresent",),
                        ("stackInstalled",),
                    ))
                if capable is True or status.get("alpha_running") is True:
                    state, reason = (
                        "CANONICAL_STACK_READY",
                        canonical_reason or canonical_state or "CANONICAL_STACK_READY",
                    )
                else:
                    state, reason = "CANONICAL_STACK_READY", "CANONICAL_RUNTIME_STARTING"

    active = bool(
        status.get("alpha_requested") is True
        or status.get("alpha_running") is True
        or alpha
    )
    return {
        "schema": SCHEMA,
        "state": state,
        "reason": reason,
        "labelZh": STATE_LABEL_ZH[state],
        "humanZh": _human(state, reason, status),
        "active": active,
        **metadata,
    }
