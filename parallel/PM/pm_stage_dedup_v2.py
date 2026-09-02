#!/usr/bin/env python3
"""Deterministic helper for WOF PM canonical stage dedup protocol v2.

This module validates prompt metadata and derives the canonical GitHub
create-only claim path. It deliberately does NOT perform GitHub writes; the
atomic gate is the repository workflow's real GitHub create-file operation.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping


STAGE_ID_RE = re.compile(r"^[A-Z0-9][A-Z0-9_]{2,127}$")
DEDUP_KEY_RE = re.compile(r"^[a-z0-9][a-z0-9.-]{2,95}$")
VALIDATION_TOKEN_RE = re.compile(r"^[a-z0-9][a-z0-9.-]{2,47}$")
ALLOWED_MODES = {"exclusive", "independent-validation"}


class DedupProtocolError(ValueError):
    """Metadata or ownership does not satisfy fail-closed protocol v2."""


@dataclass(frozen=True)
class PromptMetadata:
    stage_id: str
    dedup_protocol: str
    dedup_key: str
    dedup_mode: str
    independent_validation_group: str | None = None
    independent_validation_key: str | None = None

    @property
    def effective_dedup_key(self) -> str:
        if self.dedup_mode == "exclusive":
            return self.dedup_key
        assert self.independent_validation_group is not None
        assert self.independent_validation_key is not None
        return (
            f"{self.dedup_key}--iv--{self.independent_validation_group}"
            f"--{self.independent_validation_key}"
        )

    @property
    def canonical_claim_path(self) -> str:
        return f"parallel/PM/DEDUP_CLAIMS/{self.effective_dedup_key}.json"


_FIELD_TEMPLATE = r"(?m)^{name}:\s*`([^`\r\n]+)`\s*$"


def _field(text: str, name: str, *, required: bool) -> str | None:
    matches = re.findall(_FIELD_TEMPLATE.format(name=re.escape(name)), text)
    if len(matches) > 1:
        raise DedupProtocolError(f"duplicate metadata field: {name}")
    if not matches:
        if required:
            raise DedupProtocolError(f"missing required metadata field: {name}")
        return None
    value = matches[0].strip()
    if not value:
        raise DedupProtocolError(f"empty metadata field: {name}")
    return value


def parse_prompt_metadata(text: str) -> PromptMetadata:
    stage_id = _field(text, "stageId", required=True)
    protocol = _field(text, "dedupProtocol", required=True)
    dedup_key = _field(text, "dedupKey", required=True)
    dedup_mode = _field(text, "dedupMode", required=True)
    group = _field(text, "independentValidationGroup", required=False)
    validation_key = _field(text, "independentValidationKey", required=False)

    assert stage_id is not None
    assert protocol is not None
    assert dedup_key is not None
    assert dedup_mode is not None

    if not STAGE_ID_RE.fullmatch(stage_id):
        raise DedupProtocolError(f"invalid stageId: {stage_id!r}")
    if protocol != "v2":
        raise DedupProtocolError(f"dedupProtocol must be 'v2', got {protocol!r}")
    if not DEDUP_KEY_RE.fullmatch(dedup_key):
        raise DedupProtocolError(f"invalid dedupKey: {dedup_key!r}")
    if dedup_mode not in ALLOWED_MODES:
        raise DedupProtocolError(f"invalid dedupMode: {dedup_mode!r}")

    if dedup_mode == "exclusive":
        if group is not None or validation_key is not None:
            raise DedupProtocolError(
                "exclusive mode must not declare independent validation fields"
            )
    else:
        if group is None or validation_key is None:
            raise DedupProtocolError(
                "independent-validation requires independentValidationGroup and "
                "independentValidationKey"
            )
        if not VALIDATION_TOKEN_RE.fullmatch(group):
            raise DedupProtocolError(
                f"invalid independentValidationGroup: {group!r}"
            )
        if not VALIDATION_TOKEN_RE.fullmatch(validation_key):
            raise DedupProtocolError(
                f"invalid independentValidationKey: {validation_key!r}"
            )

    return PromptMetadata(
        stage_id=stage_id,
        dedup_protocol=protocol,
        dedup_key=dedup_key,
        dedup_mode=dedup_mode,
        independent_validation_group=group,
        independent_validation_key=validation_key,
    )


def build_canonical_claim(
    metadata: PromptMetadata,
    *,
    prompt_path: str,
    owner: str,
    claim_token: str,
    start_commit: str,
) -> dict[str, str]:
    for field_name, value in {
        "prompt_path": prompt_path,
        "owner": owner,
        "claim_token": claim_token,
        "start_commit": start_commit,
    }.items():
        if not isinstance(value, str) or not value.strip():
            raise DedupProtocolError(f"{field_name} must be a non-empty string")

    payload = {
        "schema": "wof-pm-dedup-claim-v2",
        "dedupProtocol": "v2",
        "dedupKey": metadata.dedup_key,
        "effectiveDedupKey": metadata.effective_dedup_key,
        "dedupMode": metadata.dedup_mode,
        "stageId": metadata.stage_id,
        "promptPath": prompt_path,
        "owner": owner,
        "claimToken": claim_token,
        "state": "ACTIVE",
        "startCommit": start_commit,
    }
    if metadata.dedup_mode == "independent-validation":
        assert metadata.independent_validation_group is not None
        assert metadata.independent_validation_key is not None
        payload["independentValidationGroup"] = metadata.independent_validation_group
        payload["independentValidationKey"] = metadata.independent_validation_key
    return payload


def verify_claim_ownership(
    claim: Mapping[str, Any],
    metadata: PromptMetadata,
    *,
    prompt_path: str,
    claim_token: str,
) -> None:
    expected = {
        "schema": "wof-pm-dedup-claim-v2",
        "dedupProtocol": "v2",
        "dedupKey": metadata.dedup_key,
        "effectiveDedupKey": metadata.effective_dedup_key,
        "dedupMode": metadata.dedup_mode,
        "stageId": metadata.stage_id,
        "promptPath": prompt_path,
        "claimToken": claim_token,
        "state": "ACTIVE",
    }
    for key, value in expected.items():
        if claim.get(key) != value:
            raise DedupProtocolError(
                f"ownership verification failed for {key}: "
                f"expected {value!r}, got {claim.get(key)!r}"
            )

    if metadata.dedup_mode == "independent-validation":
        if claim.get("independentValidationGroup") != metadata.independent_validation_group:
            raise DedupProtocolError("ownership verification failed for validation group")
        if claim.get("independentValidationKey") != metadata.independent_validation_key:
            raise DedupProtocolError("ownership verification failed for validation key")


def occupied_claim_stop(existing_claim: Mapping[str, Any]) -> str:
    """Map any occupied canonical path to the only safe ordinary-worker stop."""
    if existing_claim.get("state") == "COMPLETE":
        return "ALREADY COMPLETE — SAFE TO CLOSE"
    return "ALREADY CLAIMED — SAFE TO CLOSE"


class MemoryCreateOnlyStore:
    """Test double for create-only path collision semantics, not a GitHub client."""

    def __init__(self) -> None:
        self._items: dict[str, dict[str, Any]] = {}

    def create(self, path: str, payload: Mapping[str, Any]) -> bool:
        if path in self._items:
            return False
        self._items[path] = dict(payload)
        return True

    def read(self, path: str) -> dict[str, Any]:
        return dict(self._items[path])

    def force_write_for_test(self, path: str, payload: Mapping[str, Any]) -> None:
        self._items[path] = dict(payload)


def attempt_claim_for_test(
    store: MemoryCreateOnlyStore,
    metadata: PromptMetadata,
    *,
    prompt_path: str,
    owner: str,
    claim_token: str,
    start_commit: str,
) -> str:
    """Model the protocol ordering used by deterministic repository tests."""
    payload = build_canonical_claim(
        metadata,
        prompt_path=prompt_path,
        owner=owner,
        claim_token=claim_token,
        start_commit=start_commit,
    )
    path = metadata.canonical_claim_path
    if not store.create(path, payload):
        return occupied_claim_stop(store.read(path))
    verify_claim_ownership(
        store.read(path), metadata, prompt_path=prompt_path, claim_token=claim_token
    )
    return "CLAIM ACQUIRED — WORK STARTED"


def _metadata_summary(metadata: PromptMetadata) -> dict[str, Any]:
    return {
        "stageId": metadata.stage_id,
        "dedupProtocol": metadata.dedup_protocol,
        "dedupKey": metadata.dedup_key,
        "dedupMode": metadata.dedup_mode,
        "independentValidationGroup": metadata.independent_validation_group,
        "independentValidationKey": metadata.independent_validation_key,
        "effectiveDedupKey": metadata.effective_dedup_key,
        "canonicalClaimPath": metadata.canonical_claim_path,
    }


def _cmd_validate_prompt(path: Path) -> int:
    metadata = parse_prompt_metadata(path.read_text(encoding="utf-8"))
    print(json.dumps(_metadata_summary(metadata), ensure_ascii=False, indent=2))
    return 0


def _cmd_self_test() -> int:
    exclusive = parse_prompt_metadata(
        "\n".join(
            [
                "stageId: `EXAMPLE_FIX_V1`",
                "dedupProtocol: `v2`",
                "dedupKey: `example.same-logical-fix`",
                "dedupMode: `exclusive`",
            ]
        )
    )
    same_work_other_stage = parse_prompt_metadata(
        "\n".join(
            [
                "stageId: `EXAMPLE_FIX_COPY_V99`",
                "dedupProtocol: `v2`",
                "dedupKey: `example.same-logical-fix`",
                "dedupMode: `exclusive`",
            ]
        )
    )
    assert exclusive.canonical_claim_path == same_work_other_stage.canonical_claim_path
    store = MemoryCreateOnlyStore()
    first = attempt_claim_for_test(
        store,
        exclusive,
        prompt_path="parallel/PM/A_START_PROMPT.md",
        owner="a",
        claim_token="token-a",
        start_commit="head-a",
    )
    second = attempt_claim_for_test(
        store,
        same_work_other_stage,
        prompt_path="parallel/PM/B_START_PROMPT.md",
        owner="b",
        claim_token="token-b",
        start_commit="head-b",
    )
    assert first == "CLAIM ACQUIRED — WORK STARTED"
    assert second == "ALREADY CLAIMED — SAFE TO CLOSE"
    print("PASS — pm_stage_dedup_v2 self-test")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    validate = sub.add_parser("validate-prompt", help="validate v2 prompt metadata")
    validate.add_argument("path", type=Path)
    sub.add_parser("self-test", help="run a minimal deterministic collision test")

    args = parser.parse_args(argv)
    try:
        if args.command == "validate-prompt":
            return _cmd_validate_prompt(args.path)
        if args.command == "self-test":
            return _cmd_self_test()
    except (DedupProtocolError, OSError) as exc:
        print(f"FAIL CLOSED — {exc}", file=sys.stderr)
        return 2
    raise AssertionError("unreachable")


if __name__ == "__main__":
    raise SystemExit(main())
