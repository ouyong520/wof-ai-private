#!/usr/bin/env python3
"""Synthetic regression tests for SEQMINER v3. Standard library only."""
import unittest

import seqminer


def make_state(**overrides):
    state = {name: 0 for name in seqminer.FIELDS}
    state.update(
        {
            "logical_cursor": 0x02000000,
            "cursor_flags": 0,
            "split_ref": 0,
            "x": 0,
            "y": 0,
            "type": 1,
            "timer34": 8,
            "timer42": 8,
            "profile_b4": 0,
            "profile_b6": 1,
            "mode35": 0,
            "fine6c": 0,
            "fine70": 0,
            "phase72": 0,
            "coarse73": 0,
            "coarse77": 0,
            "target": 0xBE1C,
        }
    )
    state.update(overrides)
    return state


def make_branch_state(mode35=0):
    state = make_state(mode35=mode35)
    state.update(
        {
            "timerStart": 8,
            "timerEnd": 1,
            "timerMin": 1,
            "timerMax": 8,
            "timer42Start": 8,
            "timer42End": 1,
            "timer42Min": 1,
            "timer42Max": 8,
            "timerStartBucket": "0",
            "timerEndBucket": "6-10",
            "timerMinBucket": "6-10",
            "timerMaxBucket": "0",
            "terminalTimer1Frames": 1,
            "terminalTimer1Bucket": "1",
            "positiveTimer34Reloads": [],
        }
    )
    return state


class SeqminerV3Tests(unittest.TestCase):
    def test_cross_core_timer_reload_is_not_lost(self):
        before = make_state(timer34=8, timer42=20, mode35=0)
        after = make_state(timer34=12, timer42=19, mode35=0xFF)
        cycle = seqminer.new_cycle(
            "capture.jsonl.gz", "capture.jsonl.gz", "capture-fallback", 0, 100, before
        )

        seqminer.track_zero_prefix_timer(cycle, 101, after)

        self.assertEqual(len(cycle["timer34_reload_events"]), 1)
        event = cycle["timer34_reload_events"][0]
        self.assertEqual((event["from"], event["to"]), (8, 12))
        self.assertFalse(event["sameCore"])
        self.assertTrue(event["mode35Changed"])
        self.assertTrue(event["timer42Changed"])

    def test_same_core_reload_is_also_retained(self):
        before = make_state(timer34=8, timer42=20, mode35=0)
        after = make_state(timer34=10, timer42=19, mode35=0)
        cycle = seqminer.new_cycle(
            "capture.jsonl.gz", "capture.jsonl.gz", "capture-fallback", 0, 100, before
        )

        seqminer.track_zero_prefix_timer(cycle, 101, after)

        event = cycle["timer34_reload_events"][0]
        self.assertTrue(event["sameCore"])
        self.assertFalse(event["mode35Changed"])

    def test_branchpoint_confidence_is_cycle_based(self):
        anchor = make_branch_state(0)
        branch_a = make_branch_state(1)
        branch_b = make_branch_state(2)

        cycles = [
            {"eventual_attack": 10, "states": [anchor, branch_a, anchor]},
            {"eventual_attack": 20, "states": [anchor, branch_b]},
        ]
        branchpoints = seqminer.branchpoints(cycles)
        anchor_signature = seqminer.sgn(seqminer.core(anchor))
        result = next(x for x in branchpoints if x["anchor"] == anchor_signature)

        self.assertEqual(result["attack_distribution"], {"10": 1, "20": 1})
        self.assertEqual(result["raw_occurrence_distribution"], {"10": 2, "20": 1})
        self.assertEqual(result["cycles_with_anchor"], 2)
        self.assertEqual(result["raw_occurrences"], 3)

    def test_scene_metadata_preserves_all_explicit_dimensions(self):
        label, quality = seqminer.scene_meta(
            {"stage": 2, "room": "R3", "wave": 4}, "capture.jsonl.gz"
        )
        self.assertEqual(quality, "explicit")
        self.assertEqual(label, "stage=2|room=R3|wave=4")

    def test_capture_filename_is_only_fallback_provenance(self):
        label, quality = seqminer.scene_meta({}, "capture.jsonl.gz")
        self.assertEqual(quality, "capture-fallback")
        self.assertEqual(label, "capture.jsonl.gz")


if __name__ == "__main__":
    unittest.main()
