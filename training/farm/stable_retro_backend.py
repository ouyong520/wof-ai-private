"""Stable-Retro + FBNeo single-instance backend for WOF Training Farm."""

from __future__ import annotations

import hashlib
import importlib
import importlib.metadata
import importlib.util
import json
import os
import platform
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from .adapter import (
    ConfigurationError,
    CoreAction,
    CoreFrameInput,
    DependencyError,
    RamBlockSnapshot,
    RuntimeCapabilityError,
)

ROM_ENV = "WOF_ROM_PATH"
PINNED_STABLE_RETRO = "0.9.8"
SUPPORTED_PYTHON_MIN = (3, 10)
SUPPORTED_PYTHON_MAX = (3, 14)


@dataclass(frozen=True)
class DependencyReport:
    python: str
    platform: str
    platform_supported: bool
    stable_retro_present: bool
    stable_retro_version: str | None
    pinned_version_match: bool
    fbneo_declared: bool
    fbneo_zip_mapping: bool
    rom_env: str
    rom_configured: bool
    rom_exists: bool
    rom_is_zip: bool
    rom_is_absolute: bool
    rom_external_to_repo: bool
    runtime_ready: bool
    detail: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def configured_rom_path(explicit: str | os.PathLike[str] | None = None) -> Path | None:
    raw = os.fspath(explicit) if explicit is not None else os.environ.get(ROM_ENV)
    if not raw:
        return None
    return Path(raw).expanduser()


def _import_stable_retro():
    try:
        return importlib.import_module("stable_retro")
    except ImportError as exc:
        raise DependencyError(
            "stable-retro is not importable; install training/farm/requirements-r0.1.txt"
        ) from exc


def installed_stable_retro_version() -> str | None:
    try:
        return importlib.metadata.version("stable-retro")
    except importlib.metadata.PackageNotFoundError:
        return None


def dependency_probe(
    rom_path: str | os.PathLike[str] | None = None,
) -> DependencyReport:
    py = sys.version_info[:2]
    py_supported = SUPPORTED_PYTHON_MIN <= py <= SUPPORTED_PYTHON_MAX
    system = platform.system()
    platform_supported = system in {"Windows", "Linux"}

    spec = importlib.util.find_spec("stable_retro")
    present = spec is not None
    version: str | None = None
    pinned = False
    fbneo_declared = False
    fbneo_zip_mapping = False
    details: list[str] = []

    if not py_supported:
        details.append("Python must be 3.10..3.14 for the pinned Farm assumption")
    if not platform_supported:
        details.append("FBNeo Farm bootstrap supports Windows/Linux only")

    if present:
        version = installed_stable_retro_version()
        pinned = version == PINNED_STABLE_RETRO
        if not pinned:
            details.append(
                f"stable-retro {version or 'unknown'} is present; Farm pins {PINNED_STABLE_RETRO}"
            )
        try:
            retro = _import_stable_retro()
            info = retro.get_system_info("FBNeo")
            fbneo_declared = bool(info and info.get("buttons"))
            fbneo_zip_mapping = retro.get_romfile_system("probe.zip") == "FBNeo"
        except Exception as exc:
            details.append(f"FBNeo capability probe failed: {type(exc).__name__}: {exc}")
    else:
        details.append("stable-retro is not installed")

    rom = configured_rom_path(rom_path)
    rom_configured = rom is not None
    rom_exists = bool(rom and rom.is_file())
    rom_is_zip = bool(rom and rom.suffix.lower() == ".zip")
    rom_is_absolute = bool(rom and rom.is_absolute())
    repo_root = Path(__file__).resolve().parents[2]
    rom_external_to_repo = bool(
        rom and rom_is_absolute and not rom.resolve(strict=False).is_relative_to(repo_root)
    )
    if rom_configured and not rom_is_absolute:
        details.append(f"{ROM_ENV} must be an absolute external path")
    if rom_configured and rom_is_absolute and not rom_external_to_repo:
        details.append(f"{ROM_ENV} must stay outside the repository tree")
    if rom_configured and not rom_exists:
        details.append(f"{ROM_ENV} path does not exist or is not a file")
    if rom_configured and rom_exists and not rom_is_zip:
        details.append("FBNeo Farm expects a local .zip arcade romset")
    if not rom_configured:
        details.append(f"{ROM_ENV} is not set; ROM-free implementation checks remain available")

    runtime_ready = all(
        (
            py_supported,
            platform_supported,
            present,
            pinned,
            fbneo_declared,
            fbneo_zip_mapping,
            rom_configured,
            rom_exists,
            rom_is_zip,
            rom_is_absolute,
            rom_external_to_repo,
        )
    )

    if runtime_ready:
        details.append("environment is ready for explicit single-instance runtime execution")

    return DependencyReport(
        python=platform.python_version(),
        platform=system,
        platform_supported=platform_supported,
        stable_retro_present=present,
        stable_retro_version=version,
        pinned_version_match=pinned,
        fbneo_declared=fbneo_declared,
        fbneo_zip_mapping=fbneo_zip_mapping,
        rom_env=ROM_ENV,
        rom_configured=rom_configured,
        rom_exists=rom_exists,
        rom_is_zip=rom_is_zip,
        rom_is_absolute=rom_is_absolute,
        rom_external_to_repo=rom_external_to_repo,
        runtime_ready=runtime_ready,
        detail="; ".join(details),
    )


class StableRetroFbneoBackend:
    """Direct Stable-Retro RetroEmulator host for one external FBNeo ROM zip."""

    def __init__(self, rom_path: str | os.PathLike[str] | None = None):
        report = dependency_probe(rom_path)
        if not report.runtime_ready:
            raise ConfigurationError(report.detail)

        self._retro = _import_stable_retro()
        self._np = importlib.import_module("numpy")
        self._rom_path = configured_rom_path(rom_path)
        assert self._rom_path is not None

        try:
            self._data = self._retro.data.GameData()
            self._em = self._retro.RetroEmulator(str(self._rom_path))
            self._em.configure_data(self._data)
            self._em.step()
            core = self._retro.get_system_info("FBNeo")
            buttons = core.get("buttons") if isinstance(core, dict) else None
            if not isinstance(buttons, (list, tuple)) or not buttons:
                raise RuntimeCapabilityError("FBNeo did not expose a reliable button declaration")
            if not all(type(button) is str for button in buttons):
                raise RuntimeCapabilityError("FBNeo button declaration contains non-string values")
            self._button_names = tuple(buttons)
            self._num_buttons = len(self._button_names)
        except Exception as exc:
            self.close()
            if isinstance(exc, RuntimeCapabilityError):
                raise
            raise RuntimeCapabilityError(
                f"Stable-Retro/FBNeo failed to load local ROM: {type(exc).__name__}: {exc}"
            ) from exc

    def _zero_mask(self):
        return self._np.zeros(self._num_buttons, dtype=self._np.uint8)

    def _mask_for(self, action: CoreAction):
        mask = self._zero_mask()
        for index in action.pressed:
            if index >= self._num_buttons:
                raise ValueError(
                    f"button index {index} outside FBNeo mask size {self._num_buttons}"
                )
            mask[index] = 1
        return mask

    def reset(self) -> None:
        self._em.reset()
        zero = self._zero_mask()
        for player in range(4):
            self._em.set_button_mask(zero, player)
        self._em.step()

    def step(self, action: CoreAction) -> None:
        """R0.1 compatibility path; R0.2/R0.3 deterministic code uses step_frame."""
        self._em.set_button_mask(self._mask_for(action), action.player)
        self._em.step()

    def step_frame(self, frame_input: CoreFrameInput) -> None:
        try:
            for action in frame_input.inputs:
                self._em.set_button_mask(self._mask_for(action), action.player)
            self._em.step()
        except (TypeError, ValueError):
            raise
        except Exception as exc:
            raise RuntimeCapabilityError(
                f"FBNeo frame action failed: {type(exc).__name__}: {exc}"
            ) from exc

    def read_ram_blocks(self) -> tuple[RamBlockSnapshot, ...]:
        """Expose exact Stable-Retro GameData memory-block keys and bytes.

        Stable-Retro's ``GameData.memory.blocks`` keys are the strongest
        source-native address facts exposed by this backend. R0.3 preserves those
        integer keys without reinterpreting them as host/Browser/WinKawaks
        addresses.
        """
        blocks = self._data.memory.blocks
        if not blocks:
            raise RuntimeCapabilityError("FBNeo exposed no writable RAM blocks")
        try:
            keys = list(blocks)
            if any(type(key) is not int or key < 0 for key in keys):
                raise RuntimeCapabilityError(
                    "FBNeo memory block keys must be non-negative strict integers"
                )
            ordered = sorted(keys)
            snapshots = tuple(
                RamBlockSnapshot(base_address=base, data=bytes(blocks[base]))
                for base in ordered
            )
        except RuntimeCapabilityError:
            raise
        except Exception as exc:
            raise RuntimeCapabilityError(
                f"failed to snapshot address-aware FBNeo RAM blocks: {type(exc).__name__}: {exc}"
            ) from exc
        previous_end: int | None = None
        for snapshot in snapshots:
            if previous_end is not None and snapshot.base_address < previous_end:
                raise RuntimeCapabilityError("FBNeo memory blocks overlap")
            previous_end = snapshot.base_address + snapshot.length
        return snapshots

    def read_ram(self) -> bytes:
        """R0.1/R0.2-compatible flat fingerprint ordering."""
        return b"".join(block.data for block in self.read_ram_blocks())

    def save_state(self) -> bytes:
        try:
            state = bytes(self._em.get_state())
        except Exception as exc:
            raise RuntimeCapabilityError(
                f"FBNeo save_state failed: {type(exc).__name__}: {exc}"
            ) from exc
        if not state:
            raise RuntimeCapabilityError("FBNeo returned an empty savestate")
        return state

    def load_state(self, state: bytes) -> None:
        try:
            ok = bool(self._em.set_state(state))
        except Exception as exc:
            raise RuntimeCapabilityError(
                f"FBNeo load_state failed: {type(exc).__name__}: {exc}"
            ) from exc
        if not ok:
            raise RuntimeCapabilityError("FBNeo rejected savestate")

    def runtime_identity_components(self) -> dict[str, object]:
        encoded = json.dumps(
            list(self._button_names), separators=(",", ":"), ensure_ascii=True
        ).encode("ascii")
        return {
            "backendName": "StableRetroFbneoBackend",
            "coreName": "FBNeo",
            "buttonCount": self._num_buttons,
            "buttonNamesSha256": hashlib.sha256(encoded).hexdigest(),
        }

    def close(self) -> None:
        if hasattr(self, "_em"):
            del self._em
