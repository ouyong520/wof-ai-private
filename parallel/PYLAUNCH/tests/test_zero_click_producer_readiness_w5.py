from __future__ import annotations

import argparse
import copy
import json
import re
import subprocess
import sys
import unittest
from pathlib import Path
from typing import Any, Callable

FIXTURE_NAME = "alpha_v3_w5_zero_click_producer_readiness.json"
PROOF_SCHEMA = "alpha-v3-w5-producer-behavior-proof-v1"
REQUIRED_BINDINGS = {"authorityKey", "runtimeEpoch", "p1Generation", "layoutKey"}
REQUIRED_INVALIDATIONS = {"runtime", "lifecycle", "layout"}
SEMANTIC_SOURCE_WORDS = ("hud", "portrait", "tile", "render", "sprite", "object")
FORBIDDEN_IDENTITY_SOURCE_WORDS = ("generic-hud-palette", "runtime-type-copy", "p1-lifecycle-type")


def fixture_path(repo_root: Path | None = None) -> Path:
    if repo_root is not None:
        return Path(repo_root) / "parallel/PYLAUNCH/tests/fixtures" / FIXTURE_NAME
    return Path(__file__).resolve().parent / "fixtures" / FIXTURE_NAME


def load_fixture(repo_root: Path | None = None) -> dict[str, Any]:
    return json.loads(fixture_path(repo_root).read_text(encoding="utf-8"))


def _mapping(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _apply_dotted_mutations(value: dict[str, Any], mutations: dict[str, Any]) -> dict[str, Any]:
    out = copy.deepcopy(value)
    for dotted, replacement in mutations.items():
        cursor: dict[str, Any] = out
        parts = dotted.split(".")
        for part in parts[:-1]:
            child = cursor.get(part)
            if not isinstance(child, dict):
                child = {}
                cursor[part] = child
            cursor = child
        cursor[parts[-1]] = replacement
    return out


def validate_evidence(evidence: dict[str, Any] | None, context: dict[str, Any], fixture: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if not isinstance(evidence, dict):
        return ["semantic p1ZeroClickEvidence producer emitted no evidence envelope"]
    if evidence.get("schema") != fixture.get("evidenceSchema"):
        errors.append("p1ZeroClickEvidence schema mismatch")
    expected_safety = _mapping(fixture.get("safety"))
    for key, expected in expected_safety.items():
        if evidence.get(key) != expected:
            errors.append(f"p1ZeroClickEvidence safety mismatch: {key}")

    for key in ("worldSha256", "authorityKey", "runtimeEpoch", "layoutKey"):
        if evidence.get(key) != context.get(key):
            label = "runtime" if key in {"authorityKey", "runtimeEpoch"} else ("layout" if key == "layoutKey" else "world")
            errors.append(f"stale {label} binding: {key}")
    try:
        evidence_generation = int(evidence.get("p1Generation"))
        context_generation = int(context.get("p1Generation"))
    except (TypeError, ValueError):
        evidence_generation, context_generation = -1, -2
    if evidence_generation <= 0 or evidence_generation != context_generation:
        errors.append("stale lifecycle generation binding: p1Generation")

    authority = _mapping(evidence.get("identityAuthority"))
    source = str(authority.get("source") or "").strip().lower()
    if authority.get("kind") != "semantic":
        errors.append("identity authority is not semantic")
    if authority.get("genericHudPalette") is True or "palette" in source:
        errors.append("generic HUD palette cannot be semantic identity authority")
    if authority.get("independentOfRuntimeP1Type") is not True or authority.get("derivedFromRuntimeP1Type") is True:
        errors.append("identity authority is circularly copied from runtime P1 type")
    if any(token in source for token in FORBIDDEN_IDENTITY_SOURCE_WORDS):
        errors.append("identity authority source is forbidden/circular")
    if not any(token in source for token in SEMANTIC_SOURCE_WORDS):
        errors.append("identity authority lacks an independently semantic HUD/portrait/tile/render source")
    try:
        identity_type = int(authority.get("characterType"))
        p1_type = int(context.get("p1Type"))
    except (TypeError, ValueError):
        identity_type, p1_type = -1, -2
    if identity_type <= 0 or identity_type != p1_type:
        errors.append("semantic identity does not match active runtime P1 type")

    hud = [row for row in _list(evidence.get("hudIdentityCandidates")) if isinstance(row, dict)]
    scene = [row for row in _list(evidence.get("sceneHeadCandidates")) if isinstance(row, dict)]
    if not hud:
        errors.append("semantic producer emitted no HUD identity candidate")
    if not scene:
        errors.append("semantic producer emitted no scene P1/head candidate")
    for row in scene:
        if row.get("actor") != "P1":
            errors.append("scene producer candidate is not actor=P1")
        try:
            row_generation = int(row.get("p1Generation"))
        except (TypeError, ValueError):
            row_generation = -1
        if row_generation != context_generation:
            errors.append("scene producer candidate has stale P1 generation")
    return errors


def _producer_selection(render: dict[str, Any], fixture: dict[str, Any]) -> tuple[str | None, dict[str, Any]]:
    config = _mapping(fixture.get("manifest"))
    for field in _list(config.get("producerSelectionFields")):
        if isinstance(field, str) and isinstance(render.get(field), dict):
            return field, render[field]
    return None, {}


def validate_manifest_selection(
    manifest: dict[str, Any],
    fixture: dict[str, Any],
    *,
    blob_resolver: Callable[[str, str], str] | None = None,
) -> tuple[list[str], dict[str, Any]]:
    errors: list[str] = []
    expected_safety = _mapping(fixture.get("safety"))
    safety = _mapping(manifest.get("safety"))
    for key, expected in expected_safety.items():
        if safety.get(key) != expected:
            errors.append(f"manifest safety mismatch: {key}")

    components = _mapping(manifest.get("components"))
    render = _mapping(components.get("renderAuthorityV3"))
    pylaunch = _mapping(components.get("pylaunch"))
    selected_paths = {str(path) for path in _list(render.get("files")) + _list(pylaunch.get("files")) if path}
    required_consumers = {str(path) for path in _list(_mapping(fixture.get("manifest")).get("requiredConsumerPaths"))}
    for path in sorted(required_consumers - selected_paths):
        errors.append(f"candidate does not select required W2 consumer integration runtime: {path}")

    try:
        expected_normal = int(render.get("ownerClickExpectedNormal"))
        fallback_max = int(render.get("ownerClickFallbackMaximumPerAuthorityGeneration"))
    except (TypeError, ValueError):
        expected_normal, fallback_max = -1, 99
    if expected_normal != 0:
        errors.append("normal product path is not declared ownerClickExpectedNormal=0")
    if fallback_max > 1:
        errors.append("one-click safety fallback budget exceeds one")
    if render.get("automaticSeedRequiredBeforeFallback") is not True:
        errors.append("automatic semantic acquisition is not required before fallback")

    selection_field, producer = _producer_selection(render, fixture)
    if selection_field is None:
        errors.append("normal zero-click product readiness FAIL: no selected semantic p1ZeroClickEvidence producer")
        producer = {}
    else:
        if producer.get("selected") is not True:
            errors.append("p1ZeroClickEvidence producer is present but not selected")
        if producer.get("outputField") != fixture.get("outputField"):
            errors.append("selected producer does not emit p1ZeroClickEvidence")
        if producer.get("outputSchema") != fixture.get("evidenceSchema"):
            errors.append("selected producer output schema mismatch")
        if producer.get("semanticAuthority") is not True:
            errors.append("selected producer is not semantic authority")
        if producer.get("independentSemanticIdentity") is not True:
            errors.append("selected producer does not promise independent semantic identity")
        source_kind = str(producer.get("identitySourceKind") or "").lower()
        if any(token in source_kind for token in ("palette", "runtime-type", "p1-lifecycle-type")):
            errors.append("selected producer identity source is generic/circular")
        if not any(token in source_kind for token in SEMANTIC_SOURCE_WORDS):
            errors.append("selected producer identity source is not semantic HUD/portrait/tile/render authority")
        for key, expected in expected_safety.items():
            if producer.get(key) != expected:
                errors.append(f"selected producer safety mismatch: {key}")
        bindings = {str(value) for value in _list(producer.get("bindings"))}
        invalidations = {str(value) for value in _list(producer.get("invalidatesOn"))}
        if not REQUIRED_BINDINGS.issubset(bindings):
            errors.append("selected producer is not bound to runtime/lifecycle/layout generations")
        if not REQUIRED_INVALIDATIONS.issubset(invalidations):
            errors.append("selected producer does not revoke on runtime/lifecycle/layout change")
        producer_path = str(producer.get("path") or "")
        if not producer_path:
            errors.append("selected producer path is missing")
        elif producer_path not in selected_paths:
            errors.append("selected producer path is not selected by renderAuthorityV3/pylaunch package runtime")

    source_commit = str(manifest.get("sourceCommit") or "")
    if not re.fullmatch(r"[0-9a-f]{40}", source_commit):
        errors.append("manifest sourceCommit is not a full SHA")
    rows = _list(manifest.get("files"))
    blob_map = {
        str(row.get("path")): str(row.get("gitBlobSha"))
        for row in rows if isinstance(row, dict) and row.get("path") and row.get("gitBlobSha")
    }
    producer_path = str(producer.get("path") or "")
    critical = set(required_consumers)
    if producer_path:
        critical.add(producer_path)
    for path in sorted(critical):
        pin = blob_map.get(path)
        if not pin:
            errors.append(f"candidate manifest has no blob pin for producer/consumer runtime: {path}")
        elif not re.fullmatch(r"[0-9a-f]{40}", pin):
            errors.append(f"candidate manifest blob pin is malformed: {path}")
        elif blob_resolver is not None and source_commit:
            try:
                actual = blob_resolver(source_commit, path)
            except Exception as exc:  # pragma: no cover - candidate mode
                errors.append(f"cannot resolve candidate blob {path}: {exc}")
            else:
                if actual != pin:
                    errors.append(f"candidate manifest blob pin is stale for {path}: {pin} != {actual}")
    return errors, producer


def validate_producer_proof(proof: dict[str, Any] | None, producer: dict[str, Any], fixture: dict[str, Any], producer_blob_sha: str | None) -> list[str]:
    if not isinstance(proof, dict):
        return ["normal zero-click product readiness FAIL: deterministic executed-producer proof is missing"]
    errors: list[str] = []
    if proof.get("schema") != PROOF_SCHEMA:
        errors.append("producer proof schema mismatch")
    if proof.get("producerExecuted") is not True:
        errors.append("producer proof does not record an executed producer harness")
    if proof.get("producerPath") != producer.get("path"):
        errors.append("producer proof path does not match selected producer")
    if producer_blob_sha and proof.get("producerBlobSha") != producer_blob_sha:
        errors.append("producer proof blob does not match selected producer blob pin")

    required_cases = {
        "safe_unique": True,
        "generic_hud_palette": False,
        "runtime_type_copy": False,
        "runtime_changed": False,
        "lifecycle_changed": False,
        "layout_changed": False,
    }
    cases = {str(row.get("name")): row for row in _list(proof.get("cases")) if isinstance(row, dict)}
    for name, expected in required_cases.items():
        case = cases.get(name)
        if case is None:
            errors.append(f"producer proof missing behavior case: {name}")
            continue
        context = _mapping(case.get("context"))
        evidence = case.get("evidence") if isinstance(case.get("evidence"), dict) else None
        accepted = not validate_evidence(evidence, context, fixture)
        if accepted is not expected:
            errors.append(f"producer proof behavior mismatch for {name}: accepted={accepted}, expected={expected}")
        if case.get("accepted") is not expected:
            errors.append(f"producer proof recorded verdict mismatch for {name}")
    return errors


def _git_blob_resolver(repo_root: Path) -> Callable[[str, str], str]:
    def resolve(commit: str, path: str) -> str:
        return subprocess.check_output(
            ["git", "-C", str(repo_root), "rev-parse", f"{commit}:{path}"],
            text=True,
            stderr=subprocess.STDOUT,
        ).strip()
    return resolve


def candidate_check(repo_root: Path, manifest_path: Path, proof_path: Path | None) -> list[str]:
    fixture = load_fixture(repo_root)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    errors, producer = validate_manifest_selection(manifest, fixture, blob_resolver=_git_blob_resolver(repo_root))
    if producer:
        blob_map = {
            str(row.get("path")): str(row.get("gitBlobSha"))
            for row in _list(manifest.get("files")) if isinstance(row, dict)
        }
        proof = json.loads(proof_path.read_text(encoding="utf-8")) if proof_path else None
        errors.extend(validate_producer_proof(proof, producer, fixture, blob_map.get(str(producer.get("path") or ""))))
    return errors


def make_valid_proof(fixture: dict[str, Any], producer_path: str, producer_blob_sha: str) -> dict[str, Any]:
    base_context = copy.deepcopy(_mapping(fixture.get("baseContext")))
    valid = copy.deepcopy(_mapping(fixture.get("validEvidence")))
    cases: list[dict[str, Any]] = [
        {"name": "safe_unique", "context": base_context, "evidence": valid, "accepted": True}
    ]
    aliases = {
        "generic_hud_palette_is_not_identity_authority": "generic_hud_palette",
        "runtime_p1_type_copy_is_circular": "runtime_type_copy",
        "runtime_change_revokes_old_evidence": "runtime_changed",
        "lifecycle_change_revokes_old_evidence": "lifecycle_changed",
        "layout_change_revokes_old_evidence": "layout_changed",
    }
    for row in _list(fixture.get("negativeCases")):
        if not isinstance(row, dict):
            continue
        context = _apply_dotted_mutations(base_context, _mapping(row.get("contextMutations")))
        evidence = _apply_dotted_mutations(valid, _mapping(row.get("mutations")))
        cases.append({"name": aliases[str(row.get("name"))], "context": context, "evidence": evidence, "accepted": False})
    return {
        "schema": PROOF_SCHEMA,
        "producerExecuted": True,
        "producerPath": producer_path,
        "producerBlobSha": producer_blob_sha,
        "cases": cases,
    }


class ZeroClickProducerReadinessW5Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.fixture = load_fixture()

    def test_semantic_evidence_fixture_is_accepted(self) -> None:
        self.assertEqual(validate_evidence(self.fixture["validEvidence"], self.fixture["baseContext"], self.fixture), [])

    def test_generic_palette_runtime_type_copy_and_stale_evidence_are_rejected(self) -> None:
        base_context = self.fixture["baseContext"]
        valid = self.fixture["validEvidence"]
        for row in self.fixture["negativeCases"]:
            with self.subTest(row=row["name"]):
                context = _apply_dotted_mutations(base_context, row.get("contextMutations") or {})
                evidence = _apply_dotted_mutations(valid, row.get("mutations") or {})
                errors = validate_evidence(evidence, context, self.fixture)
                self.assertTrue(errors)
                self.assertTrue(any(str(row["errorContains"]).lower() in error.lower() for error in errors), errors)

    def _good_manifest(self) -> tuple[dict[str, Any], str, str]:
        commit = "a" * 40
        producer_path = self.fixture["manifest"]["producerPathExample"]
        producer_blob = "b" * 40
        consumers = list(self.fixture["manifest"]["requiredConsumerPaths"])
        all_paths = consumers + [producer_path]
        render = {
            "sourceCommit": commit,
            "ownerClickExpectedNormal": 0,
            "ownerClickFallbackMaximumPerAuthorityGeneration": 1,
            "automaticSeedRequiredBeforeFallback": True,
            "files": all_paths,
            "p1ZeroClickEvidenceProducer": {
                "selected": True,
                "path": producer_path,
                "outputField": self.fixture["outputField"],
                "outputSchema": self.fixture["evidenceSchema"],
                "semanticAuthority": True,
                "identitySourceKind": "hud-portrait-tile-render",
                "independentSemanticIdentity": True,
                "bindings": sorted(REQUIRED_BINDINGS),
                "invalidatesOn": sorted(REQUIRED_INVALIDATIONS),
                "readOnly": True,
                "ramWrites": 0,
                "inputInjection": False,
            },
        }
        pins = {path: (producer_blob if path == producer_path else (hex(index + 1)[2:] * 40)[:40]) for index, path in enumerate(all_paths)}
        manifest = {
            "sourceCommit": commit,
            "components": {"renderAuthorityV3": render, "pylaunch": {"sourceCommit": commit, "files": all_paths}},
            "safety": {"readOnly": True, "ramWrites": 0, "inputInjection": False},
            "files": [{"path": path, "gitBlobSha": pins[path]} for path in all_paths],
        }
        return manifest, producer_path, producer_blob

    def test_consumer_and_safe_fallback_alone_cannot_claim_normal_zero_click_ready(self) -> None:
        manifest, _producer_path, _producer_blob = self._good_manifest()
        render = manifest["components"]["renderAuthorityV3"]
        render.pop("p1ZeroClickEvidenceProducer")
        render["ownerClickExpectedNormal"] = 0
        render["ownerClickFallbackMaximumPerAuthorityGeneration"] = 1
        errors, _producer = validate_manifest_selection(manifest, self.fixture)
        self.assertTrue(any("readiness FAIL" in error and "producer" in error for error in errors), errors)

    def test_selected_semantic_producer_and_consumer_blob_pins_pass_manifest_gate(self) -> None:
        manifest, producer_path, producer_blob = self._good_manifest()
        pins = {row["path"]: row["gitBlobSha"] for row in manifest["files"]}
        errors, producer = validate_manifest_selection(manifest, self.fixture, blob_resolver=lambda _commit, path: pins[path])
        self.assertEqual(errors, [])
        proof = make_valid_proof(self.fixture, producer_path, producer_blob)
        self.assertEqual(validate_producer_proof(proof, producer, self.fixture, producer_blob), [])

    def test_manifest_rejects_generic_palette_or_runtime_type_copy_as_selected_producer(self) -> None:
        for source in ("generic-hud-palette", "runtime-type-copy"):
            manifest, _producer_path, _producer_blob = self._good_manifest()
            manifest["components"]["renderAuthorityV3"]["p1ZeroClickEvidenceProducer"]["identitySourceKind"] = source
            errors, _producer = validate_manifest_selection(manifest, self.fixture)
            self.assertTrue(any("generic/circular" in error for error in errors), errors)

    def test_producer_proof_requires_runtime_lifecycle_and_layout_revocation_cases(self) -> None:
        manifest, producer_path, producer_blob = self._good_manifest()
        _errors, producer = validate_manifest_selection(manifest, self.fixture)
        proof = make_valid_proof(self.fixture, producer_path, producer_blob)
        proof["cases"] = [row for row in proof["cases"] if row["name"] != "layout_changed"]
        errors = validate_producer_proof(proof, producer, self.fixture, producer_blob)
        self.assertTrue(any("layout_changed" in error for error in errors), errors)


def main() -> int:
    parser = argparse.ArgumentParser(description="Alpha V3 W5 zero-click producer readiness / false-green gate")
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[3])
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--producer-proof", type=Path)
    parser.add_argument("--expect", choices=("ready", "not-ready"))
    args = parser.parse_args()
    if args.manifest:
        if not args.expect:
            parser.error("--expect is required with --manifest")
        errors = candidate_check(args.repo_root.resolve(), args.manifest.resolve(), args.producer_proof.resolve() if args.producer_proof else None)
        ready = not errors
        expected_ready = args.expect == "ready"
        payload = {
            "schema": "alpha-v3-w5-zero-click-producer-readiness-result-v1",
            "normalZeroClickProductReady": ready,
            "expectedReady": expected_ready,
            "errors": errors,
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0 if ready is expected_ready else 1
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(ZeroClickProducerReadinessW5Tests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
