"""Deterministic in-repository backend used only for Farm implementation checks."""

from __future__ import annotations

import struct

from .adapter import CoreAction, CoreFrameInput, RuntimeCapabilityError


class DeterministicFakeBackend:
    """Small deterministic backend; never real-WOF proof authority."""

    _STATE = struct.Struct("<Q4I32s")

    def __init__(self):
        self._closed = False
        self._frame = 0
        self._masks = [0, 0, 0, 0]
        self._ram = bytearray(32)
        self.reset()

    def _require_open(self) -> None:
        if self._closed:
            raise RuntimeCapabilityError("fake backend is closed")

    @staticmethod
    def _mask(action: CoreAction) -> int:
        mask = 0
        for index in action.pressed:
            if index >= 32:
                raise ValueError("fake backend supports button indices 0..31")
            mask |= 1 << index
        return mask

    def _advance(self) -> None:
        self._frame += 1
        self._ram[0:8] = self._frame.to_bytes(8, "little")
        for player, value in enumerate(self._masks):
            start = 8 + player * 4
            self._ram[start : start + 4] = value.to_bytes(4, "little")
        checksum = (sum(self._ram[:24]) + self._frame) & 0xFF
        self._ram[24] = checksum

    def reset(self) -> None:
        self._require_open()
        self._frame = 0
        self._masks[:] = [0, 0, 0, 0]
        self._ram[:] = bytes(32)

    def step(self, action: CoreAction) -> None:
        """R0.1 compatibility: change one player's persistent mask and advance."""
        self._require_open()
        self._masks[action.player] = self._mask(action)
        self._advance()

    def step_frame(self, frame_input: CoreFrameInput) -> None:
        """Set all four masks explicitly, then advance one frame."""
        self._require_open()
        for action in frame_input.inputs:
            self._masks[action.player] = self._mask(action)
        self._advance()

    def read_ram(self) -> bytes:
        self._require_open()
        return bytes(self._ram)

    def save_state(self) -> bytes:
        self._require_open()
        return self._STATE.pack(self._frame, *self._masks, bytes(self._ram))

    def load_state(self, state: bytes) -> None:
        self._require_open()
        if not isinstance(state, bytes) or len(state) != self._STATE.size:
            raise RuntimeCapabilityError("invalid deterministic fake savestate")
        unpacked = self._STATE.unpack(state)
        self._frame = unpacked[0]
        self._masks[:] = unpacked[1:5]
        self._ram[:] = unpacked[5]

    def runtime_identity_components(self) -> dict[str, object]:
        self._require_open()
        return {
            "backendName": "DeterministicFakeBackend",
            "coreName": "fixture",
            "buttonCount": 32,
        }

    def close(self) -> None:
        self._closed = True
