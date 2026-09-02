from __future__ import annotations

import os
import tempfile
import unittest
from unittest import mock

from training.farm.adapter import (
    CoreAction,
    CoreFrameInput,
    RuntimeCapabilityError,
    TrainingFarmAdapter,
)
from training.farm.fake_backend import DeterministicFakeBackend
from training.farm.stable_retro_backend import configured_rom_path, dependency_probe


class ContractTests(unittest.TestCase):
    def test_reset_step_save_load_deterministic(self):
        with TrainingFarmAdapter(DeterministicFakeBackend()) as adapter:
            initial = adapter.reset()
            first = adapter.step(CoreAction(player=0, pressed=(0, 4)))
            saved = adapter.save_state()
            second = adapter.step(CoreAction(player=0, pressed=(1,)))
            self.assertNotEqual(initial, first)
            self.assertNotEqual(first, second)
            adapter.load_state(saved)
            self.assertEqual(adapter.read_ram(), first)
            self.assertEqual(adapter.step(CoreAction(player=0, pressed=(1,))), second)

    def test_full_frame_neutral_is_explicit(self):
        with TrainingFarmAdapter(DeterministicFakeBackend()) as adapter:
            adapter.reset()
            active = CoreFrameInput(
                (
                    CoreAction(0, (3,)),
                    CoreAction(1, ()),
                    CoreAction(2, ()),
                    CoreAction(3, ()),
                )
            )
            neutral = CoreFrameInput.neutral()
            first = adapter.step_frame(active)
            second = adapter.step_frame(neutral)
            self.assertNotEqual(first, second)
            self.assertEqual(int.from_bytes(second[8:12], "little"), 0)

    def test_invalid_state_fails_closed(self):
        with TrainingFarmAdapter(DeterministicFakeBackend()) as adapter:
            with self.assertRaises(RuntimeCapabilityError):
                adapter.load_state(b"bad")

    def test_action_rejects_coercible_types(self):
        with self.assertRaises(TypeError):
            CoreAction(player=True)
        with self.assertRaises(TypeError):
            CoreAction(pressed=[1])  # type: ignore[arg-type]
        with self.assertRaises(TypeError):
            CoreAction(pressed=(False,))
        with self.assertRaises(ValueError):
            CoreAction(pressed=(-1,))
        with self.assertRaises(ValueError):
            CoreAction(pressed=(1, 1))

    def test_rom_path_is_external_env_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "wof.zip")
            with open(path, "wb") as fh:
                fh.write(b"fixture-not-a-rom")
            with mock.patch.dict(os.environ, {"WOF_ROM_PATH": path}, clear=False):
                self.assertEqual(configured_rom_path(), configured_rom_path(path))
                report = dependency_probe()
                self.assertTrue(report.rom_configured)
                self.assertTrue(report.rom_exists)
                self.assertTrue(report.rom_is_zip)
                self.assertTrue(report.rom_is_absolute)
                self.assertTrue(report.rom_external_to_repo)


if __name__ == "__main__":
    unittest.main()
