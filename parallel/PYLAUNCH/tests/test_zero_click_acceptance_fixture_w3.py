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

FIXTURE_NAME = "alpha_v3_w3_zero_click_acceptance.json"
GOOD_AUTO_RESULTS = {"SAFE_UNIQUE", "RECOVERED"}
ALLOWED_BROWSER_ENTRY_MODES = {"reuse-existing", "configured-url", "restore-last-session"}


def fixture_path(repo_root: Path | None = None) -> Path:
    if repo_root is not None:
        return Path(repo_root) / "parallel/PYLAUNCH/tests/fixtures" / FIXTURE_NAME
    return Path(__file__).resolve().parent / "fixtures" / FIXTURE_NAME


def load_fixture(repo_root: Path | None = None) -> dict[str, Any]:
    return json.loads(fixture_path(repo_root).read_text(encoding="utf-8"))


def validate_trace(scenario: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    name = str(scenario.get("name") or "<unnamed>")
    kind = str(scenario.get("kind") or "")
    browser = scenario.get("browser") if isinstance(scenario.get("browser"), dict) else {}
    steps = scenario.get("steps") if isinstance(scenario.get("steps"), list) else []
    if browser.get("entryMode") not in ALLOWED_BROWSER_ENTRY_MODES:
        errors.append(f"{name}: browser entryMode is not an accepted WOF reuse/open path")
    if browser.get("wofIntent") is not True:
        errors.append(f"{name}: browser path does not explicitly target/reuse WOF")
    if browser.get("aboutBlank") is not False:
        errors.append(f"{name}: blank-browser launch is forbidden")
    if not steps:
        return errors + [f"{name}: trace has no steps"]

    counts = [int(step.get("ownerClickCount") or 0) for step in steps]
    if any(count < 0 or count > 1 for count in counts):
        errors.append(f"{name}: owner click budget exceeded")
    if counts != sorted(counts):
        errors.append(f"{name}: owner click count is not monotonic")
    if any(step.get("trayVisible") is not True for step in steps):
        errors.append(f"{name}: tray/status disappeared during the owner path")
    first_auto = next((i for i, step in enumerate(steps) if step.get("autoAttempted") is True), None)
    first_click_arm = next((i for i, step in enumerate(steps) if step.get("clickArmed") is True), None)
    if first_click_arm is not None and (first_auto is None or first_auto > first_click_arm):
        errors.append(f"{name}: click fallback was armed before automatic acquisition")

    for index, step in enumerate(steps):
        state = str(step.get("state") or "")
        if state == "HEAD_TRACKING" and int(step.get("ownerClickCount") or 0) == 0:
            if step.get("autoAttempted") is not True:
                errors.append(f"{name}: zero-click HEAD_TRACKING lacks an automatic attempt at step {index}")
            if str(step.get("autoResult") or "") not in GOOD_AUTO_RESULTS:
                errors.append(f"{name}: zero-click HEAD_TRACKING lacks safe-unique/recovered authority at step {index}")
            if step.get("boundActor") != "P1":
                errors.append(f"{name}: zero-click HEAD_TRACKING is not bound to P1 at step {index}")
        if state != "HEAD_TRACKING" and step.get("markerVisible") is True and kind in {"ambiguous", "invalidation"}:
            errors.append(f"{name}: marker visible without tracking authority at step {index}")

    if kind == "safe_unique":
        final = steps[-1]
        if final.get("state") != "HEAD_TRACKING" or int(final.get("ownerClickCount") or 0) != 0:
            errors.append(f"{name}: safe unique acquisition did not reach HEAD_TRACKING with ownerClickCount=0")
        if any(step.get("clickArmed") is True for step in steps):
            errors.append(f"{name}: safe unique acquisition exposed click fallback")
        if final.get("markerVisible") is not True:
            errors.append(f"{name}: safe unique tracking marker is not visible")
    elif kind == "ambiguous":
        if any(step.get("state") == "HEAD_TRACKING" for step in steps):
            errors.append(f"{name}: ambiguous acquisition silently entered HEAD_TRACKING")
        if any(step.get("boundActor") is not None for step in steps):
            errors.append(f"{name}: ambiguous acquisition silently bound an actor")
        if any(step.get("markerVisible") is True for step in steps):
            errors.append(f"{name}: ambiguous acquisition displayed a marker")
        if steps[-1].get("state") != "ONE_CLICK_REQUIRED" or steps[-1].get("clickArmed") is not True:
            errors.append(f"{name}: fallback click was not deferred until automatic failure")
    elif kind == "fallback_click":
        if sum(1 for step in steps if step.get("clickArmed") is True) != 1:
            errors.append(f"{name}: fallback click must be armed at most once")
        final = steps[-1]
        if final.get("state") != "HEAD_TRACKING" or int(final.get("ownerClickCount") or 0) != 1:
            errors.append(f"{name}: single fallback click did not produce the expected tracking trace")
        if first_auto is None or first_click_arm is None or first_auto >= first_click_arm:
            errors.append(f"{name}: automatic failure must precede fallback click arming")
    elif kind == "loss_recovery":
        if [bool(step.get("markerVisible")) for step in steps] != [True, False, True]:
            errors.append(f"{name}: confidence loss/recovery must show-hide-show the marker")
        if len(set(counts)) != 1:
            errors.append(f"{name}: recovery consumed another owner click")
        if steps[1].get("state") != "HEAD_ACQUIRING" or steps[-1].get("state") != "HEAD_TRACKING":
            errors.append(f"{name}: loss/recovery state sequence is invalid")
    elif kind == "invalidation":
        first, final = steps[0], steps[-1]
        if first.get("state") != "HEAD_TRACKING" or first.get("markerVisible") is not True:
            errors.append(f"{name}: invalidation fixture must start from visible tracking authority")
        if final.get("authorityRevoked") is not True or final.get("markerVisible") is not False:
            errors.append(f"{name}: stale authority was not revoked/hidden")
        invalidation = scenario.get("invalidation")
        if invalidation == "runtime" and first.get("authorityGeneration") == final.get("authorityGeneration"):
            errors.append(f"{name}: runtime generation did not change")
        if invalidation == "lifecycle" and first.get("p1Generation") == final.get("p1Generation"):
            errors.append(f"{name}: P1 lifecycle generation did not change")
        if invalidation == "layout" and first.get("layoutKey") == final.get("layoutKey"):
            errors.append(f"{name}: layout key did not change")
    else:
        errors.append(f"{name}: unknown fixture kind {kind!r}")
    return errors


def validate_fixture(fixture: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if fixture.get("schema") != "alpha-v3-w3-zero-click-acceptance-fixture-v1":
        errors.append("fixture schema mismatch")
    safety = fixture.get("safety") if isinstance(fixture.get("safety"), dict) else {}
    if safety != {"readOnly": True, "ramWrites": 0, "inputInjection": False}:
        errors.append("fixture safety contract mismatch")
    scenarios = fixture.get("scenarios") if isinstance(fixture.get("scenarios"), list) else []
    names = [str(row.get("name") or "") for row in scenarios if isinstance(row, dict)]
    if len(names) != len(set(names)):
        errors.append("fixture scenario names are not unique")
    for scenario in scenarios:
        if isinstance(scenario, dict):
            errors.extend(validate_trace(scenario))
        else:
            errors.append("fixture contains a non-object scenario")
    return errors


def _optional_zero_click_paths(paths: set[str], package_cfg: dict[str, Any]) -> list[str]:
    directory = str(package_cfg.get("optionalZeroClickModuleDirectory") or "")
    return sorted(
        path for path in paths
        if path.startswith(directory) and path.endswith(".py") and "zero" in Path(path).name.lower() and "click" in Path(path).name.lower()
    )


def _zero_click_contract(render: dict[str, Any]) -> bool:
    owner_flow = str(render.get("ownerFlow") or "").lower()
    textual = "zero" in owner_flow and "click" in owner_flow and any(word in owner_flow for word in ("auto", "automatic", "fallback"))
    mode = str(render.get("mode") or "").lower()
    try:
        expected_normal = int(render.get("ownerClickExpectedNormal"))
        fallback_max = int(render.get("ownerClickFallbackMaximumPerAuthorityGeneration"))
    except (TypeError, ValueError):
        expected_normal, fallback_max = -1, 99
    structured = (
        "zero-click-first" in mode
        and render.get("automaticSeedRequiredBeforeFallback") is True
        and expected_normal == 0
        and fallback_max <= 1
    )
    return textual or structured


def validate_package_manifest(
    manifest: dict[str, Any],
    fixture: dict[str, Any],
    *,
    blob_resolver: Callable[[str, str], str] | None = None,
    immutable: dict[str, Any] | None = None,
) -> list[str]:
    errors: list[str] = []
    package_cfg = fixture.get("package") if isinstance(fixture.get("package"), dict) else {}
    safety = manifest.get("safety") if isinstance(manifest.get("safety"), dict) else {}
    for key, expected in {"readOnly": True, "ramWrites": 0, "inputInjection": False}.items():
        if safety.get(key) != expected:
            errors.append(f"manifest safety mismatch: {key}")
    if int(safety.get("ownerClickMaximumPerAuthorityGeneration", 99)) > 1:
        errors.append("manifest owner click maximum exceeds one")

    components = manifest.get("components") if isinstance(manifest.get("components"), dict) else {}
    render = components.get("renderAuthorityV3") if isinstance(components.get("renderAuthorityV3"), dict) else {}
    pylaunch = components.get("pylaunch") if isinstance(components.get("pylaunch"), dict) else {}
    selected = set(render.get("files") or []) | set(pylaunch.get("files") or [])
    required = {str(path) for path in package_cfg.get("requiredRuntimePaths") or []}
    for path in sorted(required - selected):
        errors.append(f"package does not select required corrected runtime file: {path}")
    if not _zero_click_contract(render):
        errors.append("renderAuthorityV3 does not declare a zero-click-first automatic-before-fallback contract")

    source_commit = str(manifest.get("sourceCommit") or "")
    if not re.fullmatch(r"[0-9a-f]{40}", source_commit):
        errors.append("manifest sourceCommit is not a full SHA")
    for component_name in ("ownerOneclick", "renderAuthorityV3", "pylaunch", "operatorToolkit"):
        component = components.get(component_name)
        if isinstance(component, dict) and component.get("sourceCommit") != source_commit:
            errors.append(f"{component_name} sourceCommit is not pinned to package sourceCommit")

    file_rows = manifest.get("files") if isinstance(manifest.get("files"), list) else []
    blob_map = {
        str(row.get("path")): str(row.get("gitBlobSha"))
        for row in file_rows
        if isinstance(row, dict) and row.get("path") and row.get("gitBlobSha")
    }
    critical = required | set(_optional_zero_click_paths(selected, package_cfg))
    for path in sorted(critical):
        if path not in blob_map:
            errors.append(f"manifest has no blob pin for corrected runtime file: {path}")
        elif blob_resolver is not None and source_commit:
            try:
                actual = blob_resolver(source_commit, path)
            except Exception as exc:  # pragma: no cover - candidate CLI only
                errors.append(f"cannot resolve source blob {path}: {exc}")
            else:
                if actual != blob_map[path]:
                    errors.append(f"manifest blob pin is stale for {path}: {blob_map[path]} != {actual}")

    stale = package_cfg.get("staleBaselineBlobs") if isinstance(package_cfg.get("staleBaselineBlobs"), dict) else {}
    if package_cfg.get("requireAnyCorrectedIntegrationBlobChange") is True and stale:
        changed = any(path in blob_map and blob_map[path] != str(old_blob) for path, old_blob in stale.items())
        if not changed:
            errors.append("package still pins the pre-zero-click integration runtime blobs")

    if immutable is not None:
        immutable_safety = immutable.get("safety") if isinstance(immutable.get("safety"), dict) else {}
        for key, expected in {"readOnly": True, "ramWrites": 0, "inputInjection": False}.items():
            if immutable_safety.get(key) != expected:
                errors.append(f"immutable descriptor safety mismatch: {key}")
        if immutable.get("packageVersion") != manifest.get("packageVersion"):
            errors.append("immutable descriptor packageVersion does not match manifest")
        if immutable.get("sourceCommit") != source_commit:
            errors.append("immutable descriptor sourceCommit does not match manifest")
        if immutable.get("manifestPath") != "parallel/OWNER_ONECLICK/package_manifest.json":
            errors.append("immutable descriptor points at an unexpected manifest path")
    return errors


def _git_blob_resolver(repo_root: Path) -> Callable[[str, str], str]:
    def resolve(commit: str, path: str) -> str:
        return subprocess.check_output(
            ["git", "-C", str(repo_root), "rev-parse", f"{commit}:{path}"],
            text=True,
            stderr=subprocess.STDOUT,
        ).strip()
    return resolve


def candidate_check(repo_root: Path, manifest_path: Path, immutable_path: Path | None) -> list[str]:
    fixture = load_fixture(repo_root)
    errors = validate_fixture(fixture)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    immutable = json.loads(immutable_path.read_text(encoding="utf-8")) if immutable_path else None
    errors.extend(validate_package_manifest(manifest, fixture, blob_resolver=_git_blob_resolver(repo_root), immutable=immutable))
    return errors


class ZeroClickAcceptanceFixtureW3Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.fixture = load_fixture()

    def test_fixture_scenarios_are_self_consistent(self) -> None:
        self.assertEqual(validate_fixture(self.fixture), [])

    def test_oracle_rejects_click_before_automatic_attempt(self) -> None:
        scenario = copy.deepcopy(next(row for row in self.fixture["scenarios"] if row["kind"] == "fallback_click"))
        scenario["steps"][0]["clickArmed"] = True
        self.assertTrue(any("before automatic" in error or "at most once" in error for error in validate_trace(scenario)))

    def test_oracle_rejects_ambiguous_wrong_bind(self) -> None:
        scenario = copy.deepcopy(next(row for row in self.fixture["scenarios"] if row["kind"] == "ambiguous"))
        scenario["steps"][0].update({"state": "HEAD_TRACKING", "boundActor": "P2", "markerVisible": True})
        errors = validate_trace(scenario)
        self.assertTrue(any("silently" in error or "marker" in error for error in errors))

    def test_oracle_rejects_visible_marker_during_confidence_loss(self) -> None:
        scenario = copy.deepcopy(next(row for row in self.fixture["scenarios"] if row["kind"] == "loss_recovery"))
        scenario["steps"][1]["markerVisible"] = True
        self.assertTrue(any("show-hide-show" in error for error in validate_trace(scenario)))

    def test_package_gate_accepts_structured_zero_click_candidate(self) -> None:
        required = list(self.fixture["package"]["requiredRuntimePaths"])
        commit = "a" * 40
        blob_by_path = {path: f"corrected-{index}" for index, path in enumerate(required)}
        manifest = {
            "schema": "wof-owner-oneclick-package-v1",
            "packageVersion": "synthetic.w3.ready",
            "sourceCommit": commit,
            "components": {
                "ownerOneclick": {"sourceCommit": commit, "files": []},
                "renderAuthorityV3": {
                    "sourceCommit": commit,
                    "mode": "owner-visible-exact-world-zero-click-first-p1-multisample-head-visual",
                    "ownerFlow": "menu6 -> normal game -> auto P1 identity/HUD -> bounded live-scene P1 head auto seed -> normal play -> auto complete",
                    "ownerClickExpectedNormal": 0,
                    "ownerClickFallbackMaximumPerAuthorityGeneration": 1,
                    "automaticSeedRequiredBeforeFallback": True,
                    "files": required,
                },
                "pylaunch": {"sourceCommit": commit, "files": required},
                "operatorToolkit": {"sourceCommit": commit, "files": []},
            },
            "safety": {"readOnly": True, "ramWrites": 0, "inputInjection": False, "ownerClickMaximumPerAuthorityGeneration": 1},
            "files": [{"path": path, "gitBlobSha": blob_by_path[path]} for path in required],
        }
        immutable = {
            "packageVersion": manifest["packageVersion"],
            "sourceCommit": commit,
            "manifestPath": "parallel/OWNER_ONECLICK/package_manifest.json",
            "safety": {"readOnly": True, "ramWrites": 0, "inputInjection": False},
        }
        errors = validate_package_manifest(manifest, self.fixture, blob_resolver=lambda _commit, path: blob_by_path[path], immutable=immutable)
        self.assertEqual(errors, [])

    def test_package_gate_rejects_preintegration_one_click_manifest(self) -> None:
        required = list(self.fixture["package"]["requiredRuntimePaths"])
        stale = self.fixture["package"]["staleBaselineBlobs"]
        commit = "b" * 40
        blob_by_path = {path: stale.get(path, "blob") for path in required}
        manifest = {
            "sourceCommit": commit,
            "components": {
                "renderAuthorityV3": {"sourceCommit": commit, "ownerFlow": "camera prepare -> one P1 head click maximum -> normal play", "files": required},
                "pylaunch": {"sourceCommit": commit, "files": required},
            },
            "safety": {"readOnly": True, "ramWrites": 0, "inputInjection": False, "ownerClickMaximumPerAuthorityGeneration": 1},
            "files": [{"path": path, "gitBlobSha": blob_by_path[path]} for path in required],
        }
        errors = validate_package_manifest(manifest, self.fixture)
        self.assertTrue(any("zero-click-first" in error for error in errors))
        self.assertTrue(any("pre-zero-click" in error for error in errors))


def _parse_candidate_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Alpha V3 W3 zero-click acceptance/package-readiness gate")
    parser.add_argument("--candidate-root", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, default=Path("parallel/OWNER_ONECLICK/package_manifest.json"))
    parser.add_argument("--immutable", type=Path)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if "--candidate-root" not in argv:
        suite = unittest.defaultTestLoader.loadTestsFromTestCase(ZeroClickAcceptanceFixtureW3Tests)
        return 0 if unittest.TextTestRunner(verbosity=2).run(suite).wasSuccessful() else 1
    args = _parse_candidate_args(argv)
    root = args.candidate_root.resolve()
    manifest = args.manifest if args.manifest.is_absolute() else root / args.manifest
    immutable = None if args.immutable is None else (args.immutable if args.immutable.is_absolute() else root / args.immutable)
    errors = candidate_check(root, manifest, immutable)
    if errors:
        print("W3 CANDIDATE NOT READY")
        for error in errors:
            print("-", error)
        return 2
    print("W3 CANDIDATE READY")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
