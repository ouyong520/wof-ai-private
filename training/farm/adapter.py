"""Backend-neutral WOF Training Farm adapter contract.

R0.1 intentionally stops at lifecycle, one-frame input, RAM observation, and
savestate boundaries.  It contains no policy/training/search logic.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, runtime_checkable


class TrainingFarmError(RuntimeError):
    """Base error for the isolated Training Farm bootstrap."""


class ConfigurationError(TrainingFarmError):
    """Raised when local runtime configuration is missing or invalid."""


class DependencyError(TrainingFarmError):
    """Raised when Stable-Retro/FBNeo runtime support is unavailable."""


class RuntimeCapabilityError(TrainingFarmError):
    """Raised when a required emulator/core operation fails closed."""


@dataclass(frozen=True)
class CoreAction:
    """One frame of input for one emulator player.

    ``pressed`` contains zero-based Stable-Retro/FBNeo button indices.
    Input is applied through RetroEmulator.set_button_mask; no OS/global
    keyboard injection exists in this adapter.
    """

    player: int = 0
    pressed: tuple[int, ...] = ()

    def __post_init__(self) -> None:
        if isinstance(self.player, bool) or not isinstance(self.player, int):
            raise TypeError("player must be an integer")
        if not 0 <= self.player < 4:
            raise ValueError("player must be in range 0..3")
        normalized: list[int] = []
        for index in self.pressed:
            if isinstance(index, bool) or not isinstance(index, int):
                raise TypeError("pressed button indices must be integers")
            if index < 0:
                raise ValueError("pressed button indices must be non-negative")
            normalized.append(index)
        if len(set(normalized)) != len(normalized):
            raise ValueError("pressed button indices must be unique")


@runtime_checkable
class FarmBackend(Protocol):
    """Minimal backend surface required by R0.1."""

    def reset(self) -> None: ...

    def step(self, action: CoreAction) -> None: ...

    def read_ram(self) -> bytes: ...

    def save_state(self) -> bytes: ...

    def load_state(self, state: bytes) -> None: ...

    def close(self) -> None: ...


class TrainingFarmAdapter:
    """Thin fail-closed wrapper around a single emulator backend instance."""

    def __init__(self, backend: FarmBackend):
        if not isinstance(backend, FarmBackend):
            raise TypeError("backend does not satisfy FarmBackend")
        self._backend = backend
        self._closed = False

    def _require_open(self) -> None:
        if self._closed:
            raise RuntimeCapabilityError("adapter is closed")

    def reset(self) -> bytes:
        self._require_open()
        self._backend.reset()
        return self.read_ram()

    def step(self, action: CoreAction) -> bytes:
        self._require_open()
        if not isinstance(action, CoreAction):
            raise TypeError("action must be CoreAction")
        self._backend.step(action)
        return self.read_ram()

    def read_ram(self) -> bytes:
        self._require_open()
        ram = self._backend.read_ram()
        if not isinstance(ram, bytes):
            raise RuntimeCapabilityError("backend read_ram() must return bytes")
        return ram

    def save_state(self) -> bytes:
        self._require_open()
        state = self._backend.save_state()
        if not isinstance(state, bytes) or not state:
            raise RuntimeCapabilityError("backend save_state() must return non-empty bytes")
        return state

    def load_state(self, state: bytes) -> None:
        self._require_open()
        if not isinstance(state, bytes) or not state:
            raise TypeError("state must be non-empty bytes")
        self._backend.load_state(state)

    def close(self) -> None:
        if not self._closed:
            self._backend.close()
            self._closed = True

    def __enter__(self) -> "TrainingFarmAdapter":
        self._require_open()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()
