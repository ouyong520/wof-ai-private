"""ROM-free deterministic contract/error-path smoke for Training Farm R0.1."""

from __future__ import annotations

import hashlib
import json

from .adapter import CoreAction, RuntimeCapabilityError, TrainingFarmAdapter
from .fake_backend import DeterministicFakeBackend


def run_smoke() -> dict[str, object]:
    backend = DeterministicFakeBackend()
    adapter = TrainingFarmAdapter(backend)

    initial = adapter.reset()
    assert len(initial) == 32
    assert initial == bytes(32)

    first = adapter.step(CoreAction(player=0, pressed=(1, 3)))
    assert first != initial
    state = adapter.save_state()

    second = adapter.step(CoreAction(player=0, pressed=(2,)))
    assert second != first

    adapter.load_state(state)
    restored = adapter.read_ram()
    assert restored == first

    replay = adapter.step(CoreAction(player=0, pressed=(2,)))
    assert replay == second

    invalid_state_rejected = False
    try:
        adapter.load_state(b"x")
    except RuntimeCapabilityError:
        invalid_state_rejected = True
    assert invalid_state_rejected

    adapter.close()
    closed_rejected = False
    try:
        adapter.read_ram()
    except RuntimeCapabilityError:
        closed_rejected = True
    assert closed_rejected

    return {
        "status": "PASS",
        "contract": ["reset", "step", "read_ram", "save_state", "load_state"],
        "deterministic_replay": True,
        "invalid_state_fail_closed": True,
        "closed_adapter_fail_closed": True,
        "replay_ram_sha256": hashlib.sha256(replay).hexdigest(),
    }


def main() -> int:
    print(json.dumps(run_smoke(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
