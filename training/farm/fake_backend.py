"""Deterministic in-repository backend used only for R0.1 contract smoke."""

from __future__ import annotations

import struct

from .adapter import CoreAction, RuntimeCapabilityError


class DeterministicFakeBackend:
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

    def reset(self) -> None:
        self._require_open()
        self._frame = 0
        self._masks[:] = [0, 0, 0, 0]
        self._ram[:] = bytes(32)

    def step(self, action: CoreAction) -> None:
        self._require_open()
        mask = 0
        for index in action.pressed:
            if index >= 32:
                raise ValueError("fake backend supports button indices 0..31")
            mask |= 1 << index
        self._masks[action.player] = mask
        self._frame += 1
        self._ram[0:8] = self._frame.to_bytes(8, "little")
        for player, value in enumerate(self._masks):
            start = 8 + player * 4
            self._ram[start : start + 4] = value.to_bytes(4, "little")
        checksum = (sum(self._ram[:24]) + self._frame) & 0xFF
        self._ram[24] = checksum

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

    def close(self) -> None:
        self._closed = True
