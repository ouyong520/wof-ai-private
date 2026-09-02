"""Backend-neutral WOF Training Farm adapter contract.

R0.2 keeps the R0.1 single-instance boundary and adds an explicit full-frame
input primitive so deterministic replay never depends on host input persistence.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, runtime_checkable


class TrainingFarmError(RuntimeError):
    """Base error for the isolated Training Farm."""


class ConfigurationError(TrainingFarmError):
    """Raised when local runtime configuration is missing or invalid."""


class DependencyError(TrainingFarmError):
    """Raised when Stable-Retro/FBNeo runtime support is unavailable."""


class RuntimeCapabilityError(TrainingFarmError):
    """Raised when a required emulator/core operation fails closed."""


@dataclass(frozen=True)
class CoreAction:
    """Input for one emulator player.

    ``pressed`` contains zero-based Stable-Retro/FBNeo button indices. Input is
    applied only through emulator/core APIs.
    """

    player: int = 0
    pressed: tuple[int, ...] = ()

    def __post_init__(self) -> None:
        if isinstance(self.player, bool) or not isinstance(self.player, int):
            raise TypeError("player must be an integer")
        if not 0 <= self.player < 4:
            raise ValueError("player must be in range 0..3")
        if not isinstance(self.pressed, tuple):
            raise TypeError("pressed must be a tuple of integer button indices")
        normalized: list[int] = []
        for index in self.pressed:
            if isinstance(index, bool) or not isinstance(index, int):
                raise TypeError("pressed button indices must be integers")
            if index < 0:
                raise ValueError("pressed button indices must be non-negative")
            normalized.append(index)
        if len(set(normalized)) != len(normalized):
            raise ValueError("pressed button indices must be unique")


@dataclass(frozen=True)
class CoreFrameInput:
    """Explicit input state for every player for exactly one emulated frame."""

    inputs: tuple[CoreAction, CoreAction, CoreAction, CoreAction]

    def __post_init__(self) -> None:
        if not isinstance(self.inputs, tuple) or len(self.inputs) != 4:
            raise TypeError("inputs must be a tuple containing exactly four CoreAction values")
        for action in self.inputs:
            if not isinstance(action, CoreAction):
                raise TypeError("inputs must contain only CoreAction values")
        players = tuple(action.player for action in self.inputs)
        if players != (0, 1, 2, 3):
            raise ValueError("full-frame inputs must list players exactly in order 0,1,2,3")

    @classmethod
    def neutral(cls) -> "CoreFrameInput":
        return cls(tuple(CoreAction(player=p, pressed=()) for p in range(4)))  # type: ignore[arg-type]


@runtime_checkable
class FarmBackend(Protocol):
    """Single-instance backend surface required by R0.2."""

    def reset(self) -> None: ...

    def step(self, action: CoreAction) -> None: ...

    def step_frame(self, frame_input: CoreFrameInput) -> None: ...

    def read_ram(self) -> bytes: ...

    def save_state(self) -> bytes: ...

    def load_state(self, state: bytes) -> None: ...

    def runtime_identity_components(self) -> dict[str, object]: ...

    def close(self) -> None: ...


class TrainingFarmAdapter:
    """Thin fail-closed wrapper around one emulator backend instance."""

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
        """R0.1-compatible one-player step.

        R0.2 determinism code uses ``step_frame`` instead so all player masks are
        explicit before the frame advances.
        """
        self._require_open()
        if not isinstance(action, CoreAction):
            raise TypeError("action must be CoreAction")
        self._backend.step(action)
        return self.read_ram()

    def step_frame(self, frame_input: CoreFrameInput) -> bytes:
        self._require_open()
        if not isinstance(frame_input, CoreFrameInput):
            raise TypeError("frame_input must be CoreFrameInput")
        self._backend.step_frame(frame_input)
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

    def runtime_identity_components(self) -> dict[str, object]:
        self._require_open()
        value = self._backend.runtime_identity_components()
        if not isinstance(value, dict):
            raise RuntimeCapabilityError(
                "backend runtime_identity_components() must return a dict"
            )
        return dict(value)

    def close(self) -> None:
        if not self._closed:
            self._backend.close()
            self._closed = True

    def __enter__(self) -> "TrainingFarmAdapter":
        self._require_open()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()
