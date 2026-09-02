"""Stable-Retro + FBNeo single-instance backend for WOF Training Farm R0.1."""

from __future__ import annotations

import importlib
import importlib.metadata
import importlib.util
import os
import platform
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from .adapter import (
    ConfigurationError,
    CoreAction,
    DependencyError,
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
        # 0.9.7+ uses stable_retro. Do not silently substitute an unrelated package.
        raise DependencyError(
            "stable-retro is not importable; install training/farm/requirements-r0.1.txt"
        ) from exc


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
        details.append("Python must be 3.10..3.14 for the pinned R0.1 assumption")
    if not platform_supported:
        details.append("R0.1 FBNeo bootstrap supports Windows/Linux only")

    if present:
        try:
            version = importlib.metadata.version("stable-retro")
        except importlib.metadata.PackageNotFoundError:
            version = None
        pinned = version == PINNED_STABLE_RETRO
        if not pinned:
            details.append(
                f"stable-retro {version or 'unknown'} is present; R0.1 pins {PINNED_STABLE_RETRO}"
            )
        try:
            retro = _import_stable_retro()
            info = retro.get_system_info("FBNeo")
            fbneo_declared = bool(info and info.get("buttons"))
            fbneo_zip_mapping = retro.get_romfile_system("probe.zip") == "FBNeo"
        except Exception as exc:  # dependency probe must report, not crash
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
        details.append("FBNeo R0.1 expects a local .zip arcade romset")
    if not rom_configured:
        details.append(f"{ROM_ENV} is not set; repository smoke remains available")

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
        details.append("environment is ready for an explicit one-instance runtime probe")

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
    """Direct Stable-Retro RetroEmulator host for an external FBNeo ROM zip.

    Using RetroEmulator directly is intentional: it accepts a filesystem ROM
    path and selects FBNeo from the .zip mapping, so the repository does not
    import/copy/package the ROM into Stable-Retro integration data.
    """

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
            self._num_buttons = len(core["buttons"])
        except Exception as exc:
            self.close()
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
        self._em.set_button_mask(self._mask_for(action), action.player)
        self._em.step()

    def read_ram(self) -> bytes:
        blocks = self._data.memory.blocks
        if not blocks:
            raise RuntimeCapabilityError("FBNeo exposed no writable RAM blocks")
        try:
            return b"".join(bytes(blocks[offset]) for offset in sorted(blocks))
        except Exception as exc:
            raise RuntimeCapabilityError(
                f"failed to snapshot FBNeo RAM blocks: {type(exc).__name__}: {exc}"
            ) from exc

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

    def close(self) -> None:
        # RetroEmulator owns the single-process core. Releasing the reference is
        # the upstream-supported lifecycle used by RetroEnv.close().
        if hasattr(self, "_em"):
            del self._em
