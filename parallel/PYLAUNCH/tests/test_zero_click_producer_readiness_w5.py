from __future__ import annotations

import argparse
import copy
import importlib.util
import json
import re
import subprocess
import sys
import unittest
from pathlib import Path
from typing import Any, Callable

FIXTURE_NAME = "alpha_v3_w5_zero_click_producer_readiness.json"
REQUIRED_BINDINGS = {"runtimeEpoch", "p1Generation", "layoutKey"}
REQUIRED_INVALIDATIONS = {"runtime", "lifecycle", "layout"}
SEMANTIC_KINDS = {
    "hud-semantic": "hud-character-id",
    "portrait-semantic": "portrait-character-id",
    "tile-semantic": "tile-character-id",
    "render-semantic": "render-character-id",
}


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
    out: Any = copy.deepcopy(value)
    for dotted, replacement in mutations.items():
        parts = dotted.split(".")
        cursor: Any = out
        for part in parts[:-1]:
            cursor = cursor[int(part)] if isinstance(cursor, list) else cursor[part]
        final = parts[-1]
        if isinstance(cursor, list):
            cursor[int(final)] = replacement
        else:
            cursor[final] = replacement
    return out


def _candidate_bindings(row: dict[str, Any], context: dict[str, Any], label: str) -> list[str]:
    errors: list[str] = []
    for key in ("worldSha256", "runtimeEpoch", "layoutKey"):
        if row.get(key) != context.get(key):
            kind = "runtime" if key == "runtimeEpoch" else ("layout" if key == "layoutKey" else "world")
            errors.append(f"{label} has stale {kind} binding: {key}")
    try:
        row_generation = int(row.get("p1Generation"))
        context_generation = int(context.get("p1Generation"))
    except (TypeError, ValueError):
        row_generation, context_generation = -1, -2
    if row_generation <= 0 or row_generation != context_generation:
        errors.append(f"{label} has stale lifecycle generation binding")
    return errors


def validate_evidence(evidence: dict[str, Any] | None, context: dict[str, Any], fixture: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if not isinstance(evidence, dict):
        return ["semantic p1ZeroClickEvidence producer emitted no evidence envelope"]
    if evidence.get("schema") != fixture.get("evidenceSchema"):
        errors.append("p1ZeroClickEvidence schema mismatch")
    if evidence.get("producerSchema") != fixture.get("producerSchema"):
        errors.append("p1ZeroClickEvidence producer schema mismatch")
    if evidence.get("producerVerdict") != "SAFE_UNIQUE":
        errors.append("p1ZeroClickEvidence is not a SAFE_UNIQUE producer verdict")
    for key, expected in _mapping(fixture.get("safety")).items():
        if evidence.get(key) != expected:
            errors.append(f"p1ZeroClickEvidence safety mismatch: {key}")

    for key in ("worldSha256", "runtimeEpoch", "layoutKey"):
        if evidence.get(key) != context.get(key):
            kind = "runtime" if key == "runtimeEpoch" else ("layout" if key == "layoutKey" else "world")
            errors.append(f"stale {kind} binding: {key}")
    try:
        generation = int(evidence.get("p1Generation"))
        p1_generation = int(context.get("p1Generation"))
        p1_type = int(context.get("p1Type"))
        evidence_type = int(evidence.get("p1Type"))
    except (TypeError, ValueError):
        generation, p1_generation, p1_type, evidence_type = -1, -2, -3, -4
    if generation <= 0 or generation != p1_generation:
        errors.append("stale lifecycle generation binding: p1Generation")
    if p1_type <= 0 or evidence_type != p1_type:
        errors.append("producer envelope P1 type does not match active runtime P1 type")

    hud = [row for row in _list(evidence.get("hudIdentityCandidates")) if isinstance(row, dict)]
    scene = [row for row in _list(evidence.get("sceneHeadCandidates")) if isinstance(row, dict)]
    if len(hud) != 1:
        errors.append("semantic producer must emit exactly one safe HUD identity candidate")
    if len(scene) != 1:
        errors.append("semantic producer must emit exactly one safe scene P1/head candidate")
    if not hud or not scene:
        return errors

    identity = hud[0]
    if identity.get("semanticAuthority") is not True:
        errors.append("HUD identity candidate is not semantic authority")
    kind = str(identity.get("semanticAuthorityKind") or "")
    derivation = str(identity.get("identityDerivation") or "")
    if "palette" in kind.lower() or "color" in kind.lower() or "palette" in derivation.lower():
        errors.append("generic HUD palette cannot be semantic producer authority")
    expected_derivation = SEMANTIC_KINDS.get(kind)
    if expected_derivation is None:
        errors.append("HUD identity candidate uses an unproven semantic authority kind")
    elif derivation != expected_derivation:
        if "runtime" in derivation.lower() or "p1-type" in derivation.lower() or "lifecycle-type" in derivation.lower():
            errors.append("HUD identity candidate circularly copies runtime P1 type")
        else:
            errors.append("HUD identity candidate semantic derivation mismatch")
    if identity.get("independentOfRuntimeType") is not True:
        errors.append("HUD identity candidate is not independent of runtime P1 type")
    if not str(identity.get("authorityId") or "").strip():
        errors.append("HUD identity candidate lacks semantic authority provenance")
    try:
        identity_type = int(identity.get("characterType"))
    except (TypeError, ValueError):
        identity_type = -1
    if identity_type != p1_type:
        errors.append("semantic HUD identity does not match active runtime P1 type")
    errors.extend(_candidate_bindings(identity, context, "HUD identity candidate"))

    head = scene[0]
    if head.get("actor") != "P1":
        errors.append("scene producer candidate is not actor=P1")
    if not str(head.get("authorityId") or "").strip():
        errors.append("scene P1/head candidate lacks authority provenance")
    if str(head.get("identityKey") or "") != str(identity.get("identityKey") or ""):
        errors.append("HUD and scene producer identity keys conflict")
    try:
        head_type = int(head.get("characterType"))
    except (TypeError, ValueError):
        head_type = -1
    if head_type != p1_type:
        errors.append("scene P1/head candidate does not match active runtime P1 type")
    errors.extend(_candidate_bindings(head, context, "scene P1/head candidate"))
    sources = {str(value) for value in _list(head.get("evidenceSources"))}
    if "canvas" not in sources or not ({"sprite", "tile", "render-object"} & sources):
        errors.append("scene P1/head candidate lacks canvas plus verified spatial authority")
    return errors


def _producer_selection(render: dict[str, Any], fixture: dict[str, Any]) -> tuple[str | None, dict[str, Any]]:
    for field in _list(_mapping(fixture.get("manifest")).get("producerSelectionFields")):
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
    for key, expected in expected_safety.items():
        if _mapping(manifest.get("safety")).get(key) != expected:
            errors.append(f"manifest safety mismatch: {key}")

    components = _mapping(manifest.get("components"))
    render = _mapping(components.get("renderAuthorityV3"))
    pylaunch = _mapping(components.get("pylaunch"))
    selected_paths = {str(path) for path in _list(render.get("files")) + _list(pylaunch.get("files")) if path}
    config = _mapping(fixture.get("manifest"))
    required_consumers = {str(path) for path in _list(config.get("requiredConsumerPaths"))}
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
    if render.get("semanticIdentityGate") != "W2_FAIL_CLOSED":
        errors.append("W2 fail-closed semantic consumer is not selected")
    if render.get("genericHudPaletteSemanticIdentityAllowed") is not False:
        errors.append("generic HUD palette is not explicitly forbidden for semantic identity")

    selection_field, producer = _producer_selection(render, fixture)
    if selection_field is None:
        errors.append("normal zero-click product readiness FAIL: no selected semantic p1ZeroClickEvidence producer")
        producer = {}
    else:
        if producer.get("selected") is not True:
            errors.append("p1ZeroClickEvidence producer is present but not selected")
        if producer.get("path") != config.get("producerPath"):
            errors.append("candidate selected a producer path that is not the W6 semantic producer")
        if producer.get("callable") != config.get("producerCallable"):
            errors.append("selected producer callable mismatch")
        if producer.get("outputField") != fixture.get("outputField"):
            errors.append("selected producer does not emit p1ZeroClickEvidence")
        if producer.get("outputSchema") != fixture.get("evidenceSchema"):
            errors.append("selected producer output schema mismatch")
        if producer.get("producerSchema") != fixture.get("producerSchema"):
            errors.append("selected producer schema mismatch")
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
        if producer_path and producer_path not in selected_paths:
            errors.append("selected producer path is not selected by renderAuthorityV3/pylaunch package runtime")

    source_commit = str(manifest.get("sourceCommit") or "")
    if not re.fullmatch(r"[0-9a-f]{40}", source_commit):
        errors.append("manifest sourceCommit is not a full SHA")
    blob_map = {
        str(row.get("path")): str(row.get("gitBlobSha"))
        for row in _list(manifest.get("files"))
        if isinstance(row, dict) and row.get("path") and row.get("gitBlobSha")
    }
    critical = set(required_consumers)
    producer_path = str(producer.get("path") or "")
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


def _apply_w6_mutation(base: dict[str, Any], mutation: dict[str, Any]) -> dict[str, Any]:
    out = copy.deepcopy(base)
    for key, patch in mutation.items():
        if key in {"semanticIdentity", "sceneHead"} and isinstance(out.get(key), list) and out[key]:
            out[key][0].update(_mapping(patch))
        elif isinstance(out.get(key), dict) and isinstance(patch, dict):
            out[key].update(patch)
        else:
            out[key] = copy.deepcopy(patch)
    return out


def _invoke_producer(producer_callable: Any, case: dict[str, Any]) -> Any:
    return producer_callable(
        world_sha256=str(case.get("worldSha256") or ""),
        runtime_epoch=str(case.get("runtimeEpoch") or ""),
        layout_key=str(case.get("layoutKey") or ""),
        p1_lifecycle=_mapping(case.get("p1Lifecycle")),
        canvas=_mapping(case.get("canvas")),
        semantic_identity_observations=_list(case.get("semanticIdentity")),
        scene_head_observations=_list(case.get("sceneHead")),
    )


def run_selected_producer_harness(repo_root: Path, producer: dict[str, Any], fixture: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    config = _mapping(fixture.get("manifest"))
    producer_path = repo_root / str(producer.get("path") or "")
    if not producer_path.is_file():
        return [f"selected semantic producer file does not exist: {producer_path}"]
    spec = importlib.util.spec_from_file_location("_alpha_v3_w5_selected_producer", producer_path)
    if spec is None or spec.loader is None:
        return ["selected semantic producer cannot be imported"]
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    try:
        spec.loader.exec_module(module)
    except Exception as exc:
        return [f"selected semantic producer import failed: {type(exc).__name__}: {exc}"]
    finally:
        sys.modules.pop(spec.name, None)
    callable_name = str(producer.get("callable") or config.get("producerCallable") or "")
    producer_callable = getattr(module, callable_name, None)
    if not callable(producer_callable):
        return [f"selected semantic producer callable is missing: {callable_name}"]

    w6_fixture_path = repo_root / str(config.get("producerInputFixture") or "")
    if not w6_fixture_path.is_file():
        return ["W6 deterministic producer input fixture is missing"]
    w6_fixture = json.loads(w6_fixture_path.read_text(encoding="utf-8"))
    base = _mapping(w6_fixture.get("base"))
    mutations = _mapping(w6_fixture.get("mutations"))
    for case_name, case_spec in _mapping(fixture.get("executedProducerCases")).items():
        if not isinstance(case_spec, dict):
            errors.append(f"invalid W5 executed producer case: {case_name}")
            continue
        mutation_name = case_spec.get("fixtureMutation")
        case = copy.deepcopy(base)
        if mutation_name is not None:
            mutation = mutations.get(str(mutation_name))
            if not isinstance(mutation, dict):
                errors.append(f"W6 producer fixture mutation missing: {mutation_name}")
                continue
            case = _apply_w6_mutation(case, mutation)
        try:
            result = _invoke_producer(producer_callable, case)
        except Exception as exc:
            errors.append(f"selected producer execution failed for {case_name}: {type(exc).__name__}: {exc}")
            continue
        ok = bool(getattr(result, "ok", False))
        envelope = getattr(result, "envelope", None)
        expected_ok = case_spec.get("expectedOk") is True
        if ok != expected_ok:
            reason = str(getattr(result, "reason", ""))
            errors.append(f"selected producer behavior mismatch for {case_name}: ok={ok}, expected={expected_ok}, reason={reason}")
        if expected_ok:
            context = {
                "worldSha256": base.get("worldSha256"),
                "runtimeEpoch": base.get("runtimeEpoch"),
                "layoutKey": base.get("layoutKey"),
                "p1Generation": _mapping(base.get("p1Lifecycle")).get("generation"),
                "p1Type": _mapping(base.get("p1Lifecycle")).get("type"),
            }
            evidence_errors = validate_evidence(envelope if isinstance(envelope, dict) else None, context, fixture)
            errors.extend(f"{case_name}: {error}" for error in evidence_errors)
        elif envelope is not None:
            errors.append(f"selected producer emitted stale/nonsemantic evidence instead of revoking it for {case_name}")
    return errors


def _git_blob_resolver(repo_root: Path) -> Callable[[str, str], str]:
    def resolve(commit: str, path: str) -> str:
        return subprocess.check_output(
            ["git", "-C", str(repo_root), "rev-parse", f"{commit}:{path}"],
            text=True,
            stderr=subprocess.STDOUT,
        ).strip()
    return resolve


def _working_blob(repo_root: Path, path: str) -> str:
    return subprocess.check_output(
        ["git", "-C", str(repo_root), "hash-object", path],
        text=True,
        stderr=subprocess.STDOUT,
    ).strip()


def candidate_check(repo_root: Path, manifest_path: Path) -> list[str]:
    fixture = load_fixture(repo_root)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    errors, producer = validate_manifest_selection(manifest, fixture, blob_resolver=_git_blob_resolver(repo_root))
    if producer and producer.get("selected") is True:
        blob_map = {
            str(row.get("path")): str(row.get("gitBlobSha"))
            for row in _list(manifest.get("files")) if isinstance(row, dict)
        }
        producer_path = str(producer.get("path") or "")
        pin = blob_map.get(producer_path)
        if pin:
            try:
                current_blob = _working_blob(repo_root, producer_path)
            except Exception as exc:
                errors.append(f"cannot hash selected producer working file: {exc}")
            else:
                if current_blob != pin:
                    errors.append(f"executed producer working blob is not the manifest-selected blob: {current_blob} != {pin}")
        errors.extend(run_selected_producer_harness(repo_root, producer, fixture))
    return errors


class ZeroClickProducerReadinessW5Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.fixture = load_fixture()
        cls.repo_root = Path(__file__).resolve().parents[3]

    def test_w6_shaped_semantic_evidence_fixture_is_accepted(self) -> None:
        self.assertEqual(validate_evidence(self.fixture["validEvidence"], self.fixture["baseContext"], self.fixture), [])

    def test_generic_palette_runtime_type_copy_and_stale_evidence_are_rejected(self) -> None:
        base_context = self.fixture["baseContext"]
        valid = self.fixture["validEvidence"]
        for row in self.fixture["negativeEvidenceCases"]:
            with self.subTest(row=row["name"]):
                context = _apply_dotted_mutations(base_context, row.get("contextMutations") or {})
                evidence = _apply_dotted_mutations(valid, row.get("mutations") or {})
                errors = validate_evidence(evidence, context, self.fixture)
                self.assertTrue(errors)
                self.assertTrue(any(str(row["errorContains"]).lower() in error.lower() for error in errors), errors)

    def test_actual_w6_producer_executes_safe_unique_and_revokes_nonsemantic_or_stale_inputs(self) -> None:
        config = self.fixture["manifest"]
        producer = {"path": config["producerPath"], "callable": config["producerCallable"]}
        self.assertEqual(run_selected_producer_harness(self.repo_root, producer, self.fixture), [])

    def _good_manifest(self) -> dict[str, Any]:
        commit = "a" * 40
        config = self.fixture["manifest"]
        producer_path = config["producerPath"]
        paths = list(config["requiredConsumerPaths"]) + [producer_path]
        pins = {path: (hex(index + 1)[2:] * 40)[:40] for index, path in enumerate(paths)}
        render = {
            "sourceCommit": commit,
            "ownerClickExpectedNormal": 0,
            "ownerClickFallbackMaximumPerAuthorityGeneration": 1,
            "automaticSeedRequiredBeforeFallback": True,
            "semanticIdentityGate": "W2_FAIL_CLOSED",
            "genericHudPaletteSemanticIdentityAllowed": False,
            "files": paths,
            "p1ZeroClickEvidenceProducer": {
                "selected": True,
                "path": producer_path,
                "callable": config["producerCallable"],
                "outputField": self.fixture["outputField"],
                "outputSchema": self.fixture["evidenceSchema"],
                "producerSchema": self.fixture["producerSchema"],
                "bindings": sorted(REQUIRED_BINDINGS),
                "invalidatesOn": sorted(REQUIRED_INVALIDATIONS),
                "readOnly": True,
                "ramWrites": 0,
                "inputInjection": False,
            },
        }
        return {
            "sourceCommit": commit,
            "components": {"renderAuthorityV3": render, "pylaunch": {"sourceCommit": commit, "files": paths}},
            "safety": {"readOnly": True, "ramWrites": 0, "inputInjection": False},
            "files": [{"path": path, "gitBlobSha": pins[path]} for path in paths],
        }

    def test_consumer_and_safe_one_click_fallback_alone_is_normal_zero_click_readiness_fail(self) -> None:
        manifest = self._good_manifest()
        manifest["components"]["renderAuthorityV3"].pop("p1ZeroClickEvidenceProducer")
        errors, _producer = validate_manifest_selection(manifest, self.fixture)
        self.assertTrue(any("readiness FAIL" in error and "producer" in error for error in errors), errors)

    def test_selected_producer_and_consumer_blob_pins_pass_manifest_oracle(self) -> None:
        manifest = self._good_manifest()
        pins = {row["path"]: row["gitBlobSha"] for row in manifest["files"]}
        errors, producer = validate_manifest_selection(manifest, self.fixture, blob_resolver=lambda _commit, path: pins[path])
        self.assertEqual(errors, [])
        self.assertEqual(producer["path"], self.fixture["manifest"]["producerPath"])

    def test_manifest_cannot_select_only_producer_without_w2_consumer(self) -> None:
        manifest = self._good_manifest()
        consumer = self.fixture["manifest"]["requiredConsumerPaths"][0]
        manifest["components"]["renderAuthorityV3"]["files"].remove(consumer)
        manifest["components"]["pylaunch"]["files"].remove(consumer)
        errors, _producer = validate_manifest_selection(manifest, self.fixture)
        self.assertTrue(any("consumer integration runtime" in error for error in errors), errors)


def main() -> int:
    parser = argparse.ArgumentParser(description="Alpha V3 W5 zero-click producer readiness / false-green gate")
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[3])
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--expect", choices=("ready", "not-ready"))
    args = parser.parse_args()
    if args.manifest:
        if not args.expect:
            parser.error("--expect is required with --manifest")
        errors = candidate_check(args.repo_root.resolve(), args.manifest.resolve())
        ready = not errors
        expected_ready = args.expect == "ready"
        print(json.dumps({
            "schema": "alpha-v3-w5-zero-click-producer-readiness-result-v1",
            "normalZeroClickProductReady": ready,
            "expectedReady": expected_ready,
            "errors": errors,
        }, ensure_ascii=False, indent=2))
        return 0 if ready is expected_ready else 1
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(ZeroClickProducerReadinessW5Tests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
