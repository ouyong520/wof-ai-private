from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from wof_launcher.proof import compact_proof_snapshot, write_proof_json


class WindowsProofTests(unittest.TestCase):
    @staticmethod
    def _passing_snapshot() -> dict:
        return {
            "browser_connected": True,
            "wof_page_found": True,
            "worker_found": True,
            "wasm_module_found": True,
            "heap_found": True,
            "world_921031": True,
            "read_only": True,
            "ram_writes": 0,
            "input_injection": False,
            "state": "CONNECTED",
            "identity_sha256": "5c369ce2de4f53d8cef87eca5623a1f0d39a779e885532d6f185b81357878f62",
        }

    def test_pass_requires_all_six_checks(self) -> None:
        result = compact_proof_snapshot(self._passing_snapshot())
        self.assertEqual("PASS", result["automatedResult"])
        self.assertEqual("REQUIRED", result["ownerPlayabilityConfirmation"])
        self.assertTrue(all(value == "OK" for value in result["checks"].values()))

    def test_nonzero_ram_writes_fails_closed(self) -> None:
        snapshot = self._passing_snapshot()
        snapshot["ram_writes"] = 1
        result = compact_proof_snapshot(snapshot)
        self.assertEqual("WAITING", result["automatedResult"])
        self.assertEqual("--", result["checks"]["READ ONLY / RAM writes: 0"])

    def test_missing_identity_fails_closed(self) -> None:
        snapshot = self._passing_snapshot()
        snapshot["world_921031"] = False
        result = compact_proof_snapshot(snapshot)
        self.assertEqual("WAITING", result["automatedResult"])
        self.assertEqual("--", result["checks"]["World 921031"])

    def test_writer_emits_single_compact_json(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "WINDOWS_PROOF_STATUS.json"
            write_proof_json(path, self._passing_snapshot())
            payload = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual("wof-python-launcher-windows-proof-v1", payload["schema"])
            self.assertEqual("PASS", payload["automatedResult"])
            self.assertFalse((Path(td) / "WINDOWS_PROOF_STATUS.json.tmp").exists())


if __name__ == "__main__":
    unittest.main()
