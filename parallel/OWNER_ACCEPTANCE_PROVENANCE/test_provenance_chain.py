from __future__ import annotations

import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import provenance_chain as pc


class ProvenanceChainTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp_ctx = tempfile.TemporaryDirectory(prefix="p28 provenance test ")
        self.root = Path(self.tmp_ctx.name)
        self.world = "a" * 64
        self.source = "b" * 40
        self.runtime = "runtime-epoch-00000001"
        self.renderer = "renderer-epoch-00001"
        self.identity = {
            "worldSha256": self.world,
            "pageTargetId": "page-target-1",
            "authorityKey": "authority-key-1",
            "runtimeEpoch": self.runtime,
            "rendererEpoch": self.renderer,
        }
        self.session_id = "session-0001"
        self.run_token = "p21-run-token-0001"
        self.artifacts = {}
        self._write_artifacts()
        self.manifest = self._manifest()

    def tearDown(self) -> None:
        self.tmp_ctx.cleanup()

    def _write(self, name: str, value: dict) -> Path:
        path = self.root / name
        path.write_text(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
        return path

    def _base_safety(self) -> dict:
        return {"readOnly": True, "ramWrites": 0, "inputInjection": False, "screenshotProductionCoordinates": False, "worldProjectionProductionCoordinates": False}

    def _write_artifacts(self) -> None:
        candidate = {
            "schema": "wof-owner-oneclick-package-v1", "version": 1, "sourceCommit": self.source,
            "packageVersion": "2026.09.05.test", "safety": self._base_safety(),
        }
        p19 = self._write("p19.json", candidate)
        candidate_sha = pc.sha256_file(p19)
        self.candidate_sha = candidate_sha
        self.attestation_sha = "c" * 64
        p21 = {
            "schema": "wof-alpha-p21-prepromotion-staging-receipt-v1", "version": 1,
            "candidate": {"sourceCommit": self.source, "packageVersion": "2026.09.05.test", "candidateSha256": candidate_sha},
            "alphaLiveMoved": False, "ownerVisualAcceptance": "NOT_RUN", "realWofAcceptance": "NOT_RUN", "safety": self._base_safety(),
        }
        w3 = {"schema": "wof-render-source-qualification-v1", "version": 1, "status": "PASS", "captureIdentity": {k: self.identity[k] for k in ("worldSha256", "authorityKey", "runtimeEpoch", "rendererEpoch")}}
        p16 = {
            "schema": "wof-alpha-canonical-owner-acceptance-evidence-v1", "version": 1, "packageVersion": "2026.09.05.test",
            "world": {"accepted": True, "sha256": self.world, "pageTargetId": "page-target-1", "workerTargetId": "worker-1"},
            "runtime": {"epoch": self.runtime, "authorityKey": "authority-key-1", "rendererEpoch": self.renderer},
            "canonical": {"state": "HUD_INGEST_ACCEPTED"}, "visibleProof": "NOT_PROVEN", "safety": self._base_safety(),
        }
        ack = {"sequence": 1, "evidenceGeneration": 7, "completed": True, "visibleProof": "NOT_PROVEN"}
        p18 = {
            "schema": "wof-alpha-canonical-draw-evidence-v1", "version": 1, "evidenceState": "CANONICAL_DRAW_ACKNOWLEDGED",
            "identity": dict(self.identity), "evidenceGeneration": 7, "acknowledgements": [ack], "visibleProof": "NOT_PROVEN", "safety": self._base_safety(),
        }
        p22 = {"schema": "wof-alpha-dynamic-actor-state-coverage-v1", "version": 1, "state": "OBSERVED_PARTIAL"}
        p24 = {"schema": "wof-alpha-canonical-temporal-stability-evidence-v1", "version": 1, "classification": "OBSERVED_WITH_CHURN"}
        p17 = {"schema": "wof-alpha-final-acceptance-bundle-v1", "version": 1, "automaticDecision": "READY_FOR_OWNER_VISUAL_CONFIRMATION", "visibleProof": "NOT_PROVEN"}
        p20r = {"schema": "wof-alpha-owner-visual-confirmation-receipt-v1", "version": 1, "fixture": True}
        p20p = {"schema": "wof-alpha-live-promotion-plan-v1", "version": 1, "fixture": True}
        p20x = {"schema": "wof-alpha-live-promotion-result-v1", "version": 1, "fixture": True}
        p23 = {"schema": "wof-alpha-post-promotion-verification-v1", "version": 1, "fixture": True}
        values = {"P19": candidate, "P21": p21, "W3": w3, "P16": p16, "P18": p18, "P22": p22, "P24": p24, "P17": p17, "P20_RECEIPT": p20r, "P20_PLAN": p20p, "P20_RESULT": p20x, "P23": p23}
        for stage, value in values.items():
            if stage == "P19":
                self.artifacts[stage] = p19
            else:
                self.artifacts[stage] = self._write(stage.lower() + ".json", value)

    def _bindings(self, stage: str) -> dict:
        core = {
            "sessionId": self.session_id, "p21SessionId": "p21-session-0001", "p21RunToken": self.run_token,
            "sourceCommit": self.source, "packageVersion": "2026.09.05.test", "candidateSha256": self.candidate_sha,
            **self.identity, "ackGeneration": 7,
        }
        if stage == "P19": return {k: core[k] for k in ("sourceCommit", "packageVersion", "candidateSha256")}
        if stage == "P21": return {k: core[k] for k in ("sessionId", "p21SessionId", "p21RunToken", "sourceCommit", "packageVersion", "candidateSha256", *pc.IDENTITY_FIELDS)}
        if stage in {"W3", "P16"}: return {k: core[k] for k in ("sessionId", "sourceCommit", "packageVersion", *pc.IDENTITY_FIELDS)}
        if stage == "P18": return {k: core[k] for k in ("sessionId", "sourceCommit", "packageVersion", *pc.IDENTITY_FIELDS, "ackGeneration")}
        if stage == "P22": return {"sessionId": self.session_id, "p22RunId": self.session_id, **self.identity}
        if stage == "P24": return {"sessionId": self.session_id, "p24RunId": self.session_id, **self.identity, "ackGeneration": 7}
        if stage == "P17": return {k: core[k] for k in ("sessionId", "sourceCommit", "packageVersion", "candidateSha256", *pc.IDENTITY_FIELDS, "ackGeneration")}
        return {k: core[k] for k in ("sessionId", "sourceCommit", "packageVersion", "candidateSha256")}

    def _manifest(self) -> dict:
        schemas = {stage: json.loads(path.read_text(encoding="utf-8"))["schema"] for stage, path in self.artifacts.items()}
        artifacts = [{"stage": stage, "sourceClass": "fixture", "path": path.name, "schema": schemas[stage], "semanticId": f"{self.session_id}:{stage}", "bindings": self._bindings(stage)} for stage, path in self.artifacts.items()]
        hashes = {stage: pc.sha256_file(path) for stage, path in self.artifacts.items()}
        return {
            "schema": pc.MANIFEST_SCHEMA, "version": 1,
            "sessionRoot": {
                "sessionId": self.session_id, "p21SessionId": "p21-session-0001", "p21RunToken": self.run_token,
                "candidate": {"sourceCommit": self.source, "packageVersion": "2026.09.05.test", "candidateSha256": self.candidate_sha, "attestationSha256": self.attestation_sha},
                "identity": dict(self.identity), "ackGeneration": 7, "p22RunId": self.session_id, "p24RunId": self.session_id,
            },
            "artifacts": artifacts,
            "dependencies": {
                "p17": {"artifactHashes": {stage: hashes[stage] for stage in ("P19", "P21", "W3", "P16", "P18", "P22", "P24")}},
                "p20Receipt": {"p17Sha256": hashes["P17"], "sessionId": self.session_id},
                "p20Plan": {"receiptSha256": hashes["P20_RECEIPT"], "p17Sha256": hashes["P17"], "sessionId": self.session_id},
                "p20Result": {"planSha256": hashes["P20_PLAN"], "receiptSha256": hashes["P20_RECEIPT"], "sessionId": self.session_id},
                "p23": {"promotionResultSha256": hashes["P20_RESULT"], "promotedSessionId": self.session_id},
            },
            "safety": dict(pc.SAFETY),
        }

    def _build(self, manifest: dict | None = None) -> dict:
        return pc.build_session(manifest or self.manifest, manifest_dir=self.root)

    def test_01_normal_full_chain_fixture(self):
        session = self._build()
        self.assertEqual(session["state"], "CLOSED")
        self.assertEqual(len(session["artifactLedger"]), 12)

    def test_02_p19_candidate_hash_mismatch_fails(self):
        bad = copy.deepcopy(self.manifest); bad["sessionRoot"]["candidate"]["candidateSha256"] = "d" * 64
        with self.assertRaisesRegex(pc.ProvenanceError, "P19 candidate byte hash mismatch|binding mismatch"):
            self._build(bad)

    def test_03_p21_token_mismatch_fails(self):
        bad = copy.deepcopy(self.manifest); next(x for x in bad["artifacts"] if x["stage"] == "P21")["bindings"]["p21RunToken"] = "wrong-token"
        with self.assertRaisesRegex(pc.ProvenanceError, "p21RunToken"):
            self._build(bad)

    def test_04_p21_world_page_authority_mismatch_fails(self):
        for field, value in (("worldSha256", "d" * 64), ("pageTargetId", "other-page"), ("authorityKey", "other-authority")):
            bad = copy.deepcopy(self.manifest); next(x for x in bad["artifacts"] if x["stage"] == "P21")["bindings"][field] = value
            with self.assertRaises(pc.ProvenanceError): self._build(bad)

    def test_05_runtime_epoch_mismatch_fails(self):
        bad = copy.deepcopy(self.manifest); next(x for x in bad["artifacts"] if x["stage"] == "P16")["bindings"]["runtimeEpoch"] = "runtime-epoch-99999999"
        with self.assertRaisesRegex(pc.ProvenanceError, "runtimeEpoch"): self._build(bad)

    def test_06_renderer_epoch_mismatch_fails(self):
        raw = json.loads(self.artifacts["P18"].read_text()); raw["identity"]["rendererEpoch"] = "renderer-epoch-99999"; self._write("p18.json", raw)
        with self.assertRaisesRegex(pc.ProvenanceError, "P18 exact identity mismatch|dependency hash mismatch"): self._build()

    def test_07_generation_ack_mismatch_fails(self):
        raw = json.loads(self.artifacts["P18"].read_text()); raw["acknowledgements"][0]["evidenceGeneration"] = 8; self._write("p18.json", raw)
        with self.assertRaisesRegex(pc.ProvenanceError, "generation mismatch|dependency hash mismatch"): self._build()

    def test_08_p22_cross_run_fails(self):
        bad = copy.deepcopy(self.manifest); bad["sessionRoot"]["p22RunId"] = "session-other"
        with self.assertRaisesRegex(pc.ProvenanceError, "P22 cross-run"): self._build(bad)

    def test_09_p24_cross_run_fails(self):
        bad = copy.deepcopy(self.manifest); bad["sessionRoot"]["p24RunId"] = "session-other"
        with self.assertRaisesRegex(pc.ProvenanceError, "P24 cross-run"): self._build(bad)

    def test_10_p17_dependency_hash_mismatch_fails(self):
        bad = copy.deepcopy(self.manifest); bad["dependencies"]["p17"]["artifactHashes"]["P18"] = "0" * 64
        with self.assertRaisesRegex(pc.ProvenanceError, "P17 dependency hash mismatch"): self._build(bad)

    def test_11_p20_receipt_plan_result_mismatch_fails(self):
        for branch, key in (("p20Receipt", "p17Sha256"), ("p20Plan", "receiptSha256"), ("p20Result", "planSha256")):
            bad = copy.deepcopy(self.manifest); bad["dependencies"][branch][key] = "0" * 64
            with self.assertRaisesRegex(pc.ProvenanceError, "P20"):
                self._build(bad)

    def test_12_p23_promoted_session_binding_fails(self):
        bad = copy.deepcopy(self.manifest); bad["dependencies"]["p23"]["promotedSessionId"] = "session-other"
        with self.assertRaisesRegex(pc.ProvenanceError, "P23 promoted-session"):
            self._build(bad)

    def test_13_digest_is_deterministic(self):
        one, two = self._build(), self._build()
        self.assertEqual(pc.canonical_bytes(one), pc.canonical_bytes(two))
        self.assertEqual(one["chainDigest"], two["chainDigest"])

    def test_14_persisted_artifact_tamper_is_detected(self):
        session = self._build(); output = self.root / "session.json"; pc.atomic_persist(output, session)
        self.artifacts["P22"].write_text('{"schema":"wof-alpha-dynamic-actor-state-coverage-v1","version":1,"tampered":true}\n', encoding="utf-8")
        with self.assertRaisesRegex(pc.ProvenanceError, "byte hash mismatch"):
            pc.verify_session(output)

    def test_15_terminal_immutability(self):
        output = self.root / "session.json"; pc.atomic_persist(output, self._build())
        with self.assertRaisesRegex(pc.ProvenanceError, "terminal session is immutable"):
            pc.atomic_persist(output, self._build())

    def test_16_verify_only_exact_pass_and_does_not_mutate(self):
        output = self.root / "session.json"; pc.atomic_persist(output, self._build())
        before = output.read_bytes(); result = pc.verify_session(output); after = output.read_bytes()
        self.assertEqual(result["state"], "VERIFIED"); self.assertEqual(before, after)

    def test_17_verify_session_byte_tamper_fails(self):
        output = self.root / "session.json"; pc.atomic_persist(output, self._build())
        raw = json.loads(output.read_text()); raw["sessionRoot"]["identity"]["authorityKey"] = "tampered"; output.write_text(json.dumps(raw), encoding="utf-8")
        with self.assertRaises(pc.ProvenanceError): pc.verify_session(output)

    def test_18_windows_friendly_python_cli_with_spaces(self):
        manifest_path = self.root / "manifest with spaces.json"; output = self.root / "session with spaces.json"
        manifest_path.write_text(json.dumps(self.manifest, indent=2), encoding="utf-8")
        script = Path(pc.__file__).resolve()
        build = subprocess.run([sys.executable, str(script), "build", "--manifest", str(manifest_path), "--output", str(output)], text=True, capture_output=True)
        self.assertEqual(build.returncode, 0, build.stderr)
        verify = subprocess.run([sys.executable, str(script), "verify", "--session", str(output)], text=True, capture_output=True)
        self.assertEqual(verify.returncode, 0, verify.stderr)
        self.assertIn('"state": "VERIFIED"', verify.stdout)

    def test_19_duplicate_stage_conflict_fails(self):
        bad = copy.deepcopy(self.manifest); duplicate = copy.deepcopy(next(x for x in bad["artifacts"] if x["stage"] == "P22")); duplicate["semanticId"] = "other-semantic"; bad["artifacts"].append(duplicate)
        with self.assertRaisesRegex(pc.ProvenanceError, "duplicate stage"):
            self._build(bad)

    def test_20_safety_boundary_fails_closed(self):
        bad = copy.deepcopy(self.manifest); bad["safety"]["ramWrites"] = 1
        with self.assertRaisesRegex(pc.ProvenanceError, "safety mismatch"):
            self._build(bad)


if __name__ == "__main__":
    unittest.main()
