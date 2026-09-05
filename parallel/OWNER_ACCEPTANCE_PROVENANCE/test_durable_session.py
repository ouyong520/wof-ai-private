from __future__ import annotations

import copy
import json
from pathlib import Path
import py_compile
import tempfile
import unittest

import durable_session as ds


class DurableSessionTests(unittest.TestCase):
    """P28-only synthetic fixtures; no real WOF, Owner action, or promotion occurs."""

    def setUp(self) -> None:
        self.tmp_ctx = tempfile.TemporaryDirectory(prefix="p28 durable session test ")
        self.root_dir = Path(self.tmp_ctx.name)
        self.source_commit = "b" * 40
        self.package_version = "2026.09.05.p28-test"
        self.world = "a" * 64
        self.identity = {
            "worldSha256": self.world,
            "pageTargetId": "page-target-p28",
            "authorityKey": "authority-p28",
            "runtimeEpoch": "runtime-epoch-00000001",
            "rendererEpoch": "renderer-epoch-00001",
        }
        self.session_id = "p28-session-0001"
        self.run_nonce = "p28-run-nonce-00000001"
        self.attestation_sha = "c" * 64
        self.p19 = self._write(
            "p19.json",
            {
                "schema": "wof-owner-oneclick-package-v1",
                "version": 1,
                "sourceCommit": self.source_commit,
                "packageVersion": self.package_version,
                "safety": self._safety(),
            },
        )
        self.candidate_sha = ds.sha256_file(self.p19)
        self.root = {
            "schema": ds.ROOT_SCHEMA,
            "version": 1,
            "sessionId": self.session_id,
            "runNonce": self.run_nonce,
            "candidate": {
                "sourceCommit": self.source_commit,
                "packageVersion": self.package_version,
                "candidateSha256": self.candidate_sha,
                "attestationSha256": self.attestation_sha,
            },
            "initialIdentity": dict(self.identity),
            "createdAtUtc": "2026-09-05T12:00:00Z",
            "safety": self._safety(),
        }

    def tearDown(self) -> None:
        self.tmp_ctx.cleanup()

    @staticmethod
    def _safety() -> dict:
        return {
            "readOnly": True,
            "ramWrites": 0,
            "inputInjection": False,
            "screenshotProductionCoordinates": False,
            "worldProjectionProductionCoordinates": False,
            "guessedCoordinates": False,
        }

    def _write(self, name: str, value: dict) -> Path:
        path = self.root_dir / name
        path.write_text(
            json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n",
            encoding="utf-8",
        )
        return path

    def _candidate_bindings(self, *, identity: dict | None = None, **extra) -> dict:
        out = {
            "sourceCommit": self.source_commit,
            "packageVersion": self.package_version,
            "candidateSha256": self.candidate_sha,
        }
        if identity is not None:
            out.update(identity)
        out.update(extra)
        return out

    def _artifact(self, stage: str, session: dict, *, override: dict | None = None) -> tuple[Path, dict]:
        identity = dict(session["currentIdentity"])
        stages = ds.stage_map(session)
        if stage == "P19":
            path = self.p19
            bindings = self._candidate_bindings()
        elif stage == "P21":
            path = self._write(
                "p21.json",
                {
                    "schema": "wof-alpha-p21-prepromotion-staging-receipt-v1",
                    "version": 1,
                    "candidate": {
                        "sourceCommit": self.source_commit,
                        "packageVersion": self.package_version,
                        "candidateSha256": self.candidate_sha,
                    },
                    "alphaLiveMoved": False,
                    "ownerVisualAcceptance": "NOT_RUN",
                    "realWofAcceptance": "NOT_RUN",
                    "safety": self._safety(),
                },
            )
            bindings = self._candidate_bindings(identity=identity)
        elif stage == "W3":
            path = self._write(
                "w3.json",
                {"schema": "wof-render-source-qualification-v1", "version": 1, "captureIdentity": dict(identity)},
            )
            bindings = self._candidate_bindings(identity=identity)
        elif stage == "P16":
            path = self._write(
                "p16.json",
                {
                    "schema": "wof-alpha-canonical-owner-acceptance-evidence-v1",
                    "version": 1,
                    "world": {"accepted": True, "sha256": identity["worldSha256"], "pageTargetId": identity["pageTargetId"]},
                    "runtime": {
                        "authorityKey": identity["authorityKey"],
                        "epoch": identity["runtimeEpoch"],
                        "rendererEpoch": identity["rendererEpoch"],
                    },
                    "visibleProof": "NOT_PROVEN",
                    "safety": self._safety(),
                },
            )
            bindings = self._candidate_bindings(identity=identity)
        elif stage == "P18":
            path = self._write(
                "p18.json",
                {
                    "schema": "wof-alpha-canonical-draw-evidence-v1",
                    "version": 1,
                    "identity": dict(identity),
                    "evidenceGeneration": 7,
                    "acknowledgements": [{"sequence": 1, "evidenceGeneration": 7}],
                    "visibleProof": "NOT_PROVEN",
                    "safety": self._safety(),
                },
            )
            bindings = self._candidate_bindings(identity=identity, ackGeneration=7)
        elif stage == "P22":
            path = self._write("p22.json", {"schema": "wof-alpha-dynamic-actor-state-coverage-v1", "version": 1, "identity": dict(identity)})
            bindings = self._candidate_bindings(identity=identity, runNonce=self.run_nonce)
        elif stage == "P24":
            path = self._write("p24.json", {"schema": "wof-alpha-canonical-temporal-stability-evidence-v1", "version": 1, "identity": dict(identity)})
            bindings = self._candidate_bindings(identity=identity, runNonce=self.run_nonce, ackGeneration=7)
        elif stage == "P17":
            dependencies = {name: stages[name]["byteSha256"] for name in ("P19", "P21", "W3", "P16", "P18", "P22", "P24")}
            path = self._write(
                "p17.json",
                {
                    "schema": "wof-alpha-final-acceptance-bundle-v1",
                    "version": 1,
                    "visibleProof": "NOT_PROVEN",
                    "identity": dict(identity),
                    "candidate": {
                        "sourceCommit": self.source_commit,
                        "packageVersion": self.package_version,
                        "contentSha256": self.candidate_sha,
                    },
                },
            )
            bindings = self._candidate_bindings(identity=identity, dependencyHashes=dependencies)
        elif stage == "P20_RECEIPT":
            p17_sha = stages["P17"]["byteSha256"]
            path = self._write(
                "p20_receipt.json",
                {
                    "schema": "wof-alpha-owner-visual-confirmation-receipt-v1",
                    "version": 1,
                    "fixtureMode": False,
                    "promotionEligible": True,
                    "ownerVisualVerdict": "PASS",
                    "ownerAnswer": "YES",
                    "visualProof": "OWNER_VISUAL_PASS",
                    "acceptanceBundleSha256": p17_sha,
                    "candidateSourceCommit": self.source_commit,
                    "candidateSha256": self.candidate_sha,
                    "candidateAttestationSha256": self.attestation_sha,
                    "identity": dict(identity),
                    "safety": self._safety(),
                },
            )
            bindings = self._candidate_bindings(identity=identity)
        elif stage == "P20_PLAN":
            core = {
                "fromAlphaLiveCommit": "d" * 40,
                "compareAndSwapExpectedOld": "d" * 40,
                "toCandidateCommit": self.source_commit,
                "packageVersion": self.package_version,
                "candidateSha256": self.candidate_sha,
                "candidateAttestationSha256": self.attestation_sha,
                "acceptanceBundleSha256": stages["P17"]["byteSha256"],
                "visualReceiptSha256": stages["P20_RECEIPT"]["byteSha256"],
                "fastForwardRequired": True,
                "safety": {**self._safety(), "forcePushAllowed": False, "alphaLiveMovedAtPlan": False},
            }
            path = self._write(
                "p20_plan.json",
                {"schema": "wof-alpha-live-promotion-plan-v1", "version": 1, "state": "READY", "planCore": core, "planHash": ds.sha256_bytes(ds.canonical_bytes(core))},
            )
            bindings = self._candidate_bindings()
        elif stage == "P20_RESULT":
            plan = ds.load_json(Path(stages["P20_PLAN"]["path"]))
            core = plan["planCore"]
            path = self._write(
                "p20_result.json",
                {
                    "schema": "wof-alpha-live-promotion-result-v1",
                    "version": 1,
                    "state": "PROMOTED",
                    "planHash": plan["planHash"],
                    "fromAlphaLiveCommit": core["fromAlphaLiveCommit"],
                    "toCandidateCommit": core["toCandidateCommit"],
                    "forcePushUsed": False,
                    "fastForwardOnly": True,
                },
            )
            bindings = self._candidate_bindings()
        elif stage == "P23":
            path = self._write(
                "p23.json",
                {"schema": "wof-alpha-post-promotion-verification-v1", "version": 1, "candidateSourceCommit": self.source_commit},
            )
            bindings = self._candidate_bindings(
                identity=identity,
                promotedSessionId=self.session_id,
                promotionResultSha256=stages["P20_RESULT"]["byteSha256"],
            )
        else:
            raise AssertionError(stage)
        if override:
            if "raw" in override:
                raw = ds.load_json(path)
                raw.update(override["raw"])
                path = self._write(path.name, raw)
            if "bindings" in override:
                bindings.update(override["bindings"])
        return path, bindings

    def _bind(self, session: dict, stage: str, *, override: dict | None = None) -> None:
        path, bindings = self._artifact(stage, session, override=override)
        ds.bind_artifact(session, stage=stage, path=path, bindings=bindings)

    def _through(self, last_stage: str, *, session: dict | None = None) -> dict:
        session = session or ds.new_session(self.root)
        for stage in ds.REQUIRED_STAGES:
            self._bind(session, stage)
            if stage == last_stage:
                break
        return session

    def test_01_same_session_valid_chain_fixture_reaches_chain_complete(self):
        session = self._through("P23")
        self.assertEqual(session["state"], ds.CHAIN_COMPLETE)
        self.assertTrue(session["terminal"])
        self.assertEqual(len(session["artifactLedger"]), len(ds.REQUIRED_STAGES))
        self.assertEqual(ds.verify_session(session)["state"], "VERIFIED")

    def test_02_monotonic_states_are_exposed(self):
        session = ds.new_session(self.root)
        expected = {
            "P19": ds.OPEN,
            "P21": ds.WAITING_FOR_LIVE_W3,
            "W3": ds.WAITING_FOR_CANONICAL_EVIDENCE,
            "P18": ds.WAITING_FOR_DYNAMIC_TEMPORAL_EVIDENCE,
            "P17": ds.READY_FOR_OWNER_VISUAL_CONFIRMATION,
            "P20_RECEIPT": ds.WAITING_FOR_PROMOTION,
            "P20_RESULT": ds.WAITING_FOR_POST_PROMOTION_VERIFY,
            "P23": ds.CHAIN_COMPLETE,
        }
        for stage in ds.REQUIRED_STAGES:
            self._bind(session, stage)
            if stage in expected:
                self.assertEqual(session["state"], expected[stage])

    def test_03_cross_candidate_rejected(self):
        session = ds.new_session(self.root)
        path, bindings = self._artifact("P19", session)
        bindings["sourceCommit"] = "e" * 40
        with self.assertRaisesRegex(ds.ProvenanceError, "candidate binding mismatch"):
            ds.bind_artifact(session, stage="P19", path=path, bindings=bindings)
        self.assertEqual(session["state"], ds.REJECTED)

    def test_04_world_page_authority_runtime_renderer_mismatch_rejected(self):
        for field, bad_value in (
            ("worldSha256", "f" * 64),
            ("pageTargetId", "other-page"),
            ("authorityKey", "other-authority"),
            ("runtimeEpoch", "runtime-epoch-99999999"),
            ("rendererEpoch", "renderer-epoch-99999"),
        ):
            session = self._through("P21")
            path, bindings = self._artifact("W3", session)
            bindings[field] = bad_value
            with self.assertRaises(ds.ProvenanceError, msg=field):
                ds.bind_artifact(session, stage="W3", path=path, bindings=bindings)
            self.assertEqual(session["state"], ds.REJECTED)

    def test_05_explicit_epoch_transition_is_allowed_before_p17(self):
        session = self._through("P18")
        before = dict(session["currentIdentity"])
        after = {**before, "runtimeEpoch": "runtime-epoch-00000002", "rendererEpoch": "renderer-epoch-00002"}
        transition = self._write(
            "epoch.json",
            {
                "schema": ds.EPOCH_SCHEMA,
                "version": 1,
                "sequence": 1,
                "before": before,
                "after": after,
                "authorityEvidenceSha256": ["1" * 64],
            },
        )
        ds.bind_epoch_transition(session, path=transition)
        self.assertEqual(session["currentIdentity"], after)
        for stage in ("P22", "P24", "P17"):
            self._bind(session, stage)
        self.assertEqual(session["state"], ds.READY_FOR_OWNER_VISUAL_CONFIRMATION)

    def test_06_unrelated_epoch_transition_is_rejected(self):
        session = self._through("P18")
        before = dict(session["currentIdentity"])
        after = {**before, "worldSha256": "f" * 64, "runtimeEpoch": "runtime-epoch-00000002"}
        transition = self._write(
            "unrelated_epoch.json",
            {
                "schema": ds.EPOCH_SCHEMA,
                "version": 1,
                "sequence": 1,
                "before": before,
                "after": after,
                "authorityEvidenceSha256": ["2" * 64],
            },
        )
        with self.assertRaisesRegex(ds.ProvenanceError, "unrelated World/page"):
            ds.bind_epoch_transition(session, path=transition)
        self.assertEqual(session["state"], ds.REJECTED)

    def test_07_stale_p18_generation_ack_is_rejected(self):
        session = self._through("P16")
        path, bindings = self._artifact("P18", session)
        bindings["ackGeneration"] = 8
        with self.assertRaisesRegex(ds.ProvenanceError, "stale generation"):
            ds.bind_artifact(session, stage="P18", path=path, bindings=bindings)
        self.assertEqual(session["state"], ds.REJECTED)

    def test_08_p17_dependency_hash_mismatch_is_rejected(self):
        session = self._through("P24")
        path, bindings = self._artifact("P17", session)
        bindings["dependencyHashes"]["P18"] = "0" * 64
        with self.assertRaisesRegex(ds.ProvenanceError, "dependency hash mismatch"):
            ds.bind_artifact(session, stage="P17", path=path, bindings=bindings)

    def test_09_fixture_owner_receipt_cannot_fill_real_slot(self):
        session = self._through("P17")
        path, bindings = self._artifact("P20_RECEIPT", session, override={"raw": {"fixtureMode": True}})
        with self.assertRaisesRegex(ds.ProvenanceError, "fixture/non-eligible"):
            ds.bind_artifact(session, stage="P20_RECEIPT", path=path, bindings=bindings)

    def test_10_promotion_plan_cas_mismatch_is_rejected(self):
        session = self._through("P20_RECEIPT")
        path, bindings = self._artifact("P20_PLAN", session)
        raw = ds.load_json(path)
        raw["planCore"]["compareAndSwapExpectedOld"] = "e" * 40
        raw["planHash"] = ds.sha256_bytes(ds.canonical_bytes(raw["planCore"]))
        path = self._write("bad_plan.json", raw)
        with self.assertRaisesRegex(ds.ProvenanceError, "CAS/fast-forward"):
            ds.bind_artifact(session, stage="P20_PLAN", path=path, bindings=bindings)

    def test_11_promotion_result_plan_hash_mismatch_is_rejected(self):
        session = self._through("P20_PLAN")
        path, bindings = self._artifact("P20_RESULT", session, override={"raw": {"planHash": "0" * 64}})
        with self.assertRaisesRegex(ds.ProvenanceError, "plan/CAS binding mismatch"):
            ds.bind_artifact(session, stage="P20_RESULT", path=path, bindings=bindings)

    def test_12_p23_cross_session_close_is_rejected(self):
        session = self._through("P20_RESULT")
        path, bindings = self._artifact("P23", session)
        bindings["promotedSessionId"] = "other-session"
        with self.assertRaisesRegex(ds.ProvenanceError, "cross-session"):
            ds.bind_artifact(session, stage="P23", path=path, bindings=bindings)

    def test_13_digest_stable_for_fixed_normalized_inputs(self):
        one = ds.new_session(self.root)
        root_two = copy.deepcopy(self.root)
        root_two["createdAtUtc"] = "2026-09-05T12:01:00Z"
        two = ds.new_session(root_two)
        self.assertEqual(one["chainDigest"], two["chainDigest"])

    def test_14_atomic_persist_verify_only_and_terminal_immutability(self):
        session = self._through("P23")
        output = self.root_dir / "durable session.json"
        ds.atomic_write(output, session, create_only=True)
        before = output.read_bytes()
        verified = ds.verify_file(output)
        self.assertEqual(verified["sessionState"], ds.CHAIN_COMPLETE)
        self.assertEqual(before, output.read_bytes())
        with self.assertRaisesRegex(ds.ProvenanceError, "immutable"):
            ds.atomic_write(output, session)

    def test_15_python_and_windows_entrypoint_syntax_contract(self):
        here = Path(ds.__file__).resolve().parent
        py_compile.compile(str(here / "durable_session.py"), doraise=True)
        py_compile.compile(str(here / "provenance_chain.py"), doraise=True)
        cmd = (here / "WOF_ALPHA_VERIFY_ACCEPTANCE_PROVENANCE.cmd").read_text(encoding="utf-8")
        self.assertTrue(cmd.lower().startswith("@echo off"))
        self.assertIn("durable_session.py", cmd)
        self.assertNotIn("git push", cmd.lower())

    def test_16_static_safety_scan_has_no_dangerous_runtime_primitives(self):
        here = Path(ds.__file__).resolve().parent
        combined = "\n".join(
            (here / name).read_text(encoding="utf-8")
            for name in ("durable_session.py", "provenance_chain.py", "WOF_ALPHA_VERIFY_ACCEPTANCE_PROVENANCE.cmd")
        ).lower()
        for forbidden in (
            "writeprocessmemory",
            "virtualallocex",
            "sendinput(",
            "setcursorpos(",
            "pyautogui.click",
            "git push --force",
            "alpha-live:refs/heads/alpha-live",
        ):
            self.assertNotIn(forbidden, combined)
        self.assertTrue(ds.SAFETY["readOnly"])
        self.assertEqual(ds.SAFETY["ramWrites"], 0)
        self.assertFalse(ds.SAFETY["inputInjection"])
        self.assertFalse(ds.SAFETY["alphaLiveMoved"])
        self.assertEqual(ds.SAFETY["visibleProof"], "NOT_PROVEN")
        self.assertEqual(ds.SAFETY["realWofAcceptance"], "NOT_RUN")
        self.assertEqual(ds.SAFETY["ownerVisualAcceptance"], "NOT_RUN")


if __name__ == "__main__":
    unittest.main()
