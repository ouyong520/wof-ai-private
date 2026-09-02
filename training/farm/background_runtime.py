"""ROM-free headless/background runtime foundation for Training Farm R0.4.5.

No Stable-Retro/RL dependency is imported here and no emulator worker is launched.
"""
from __future__ import annotations

import argparse
import ast
import ctypes
import hashlib
import json
import os
import platform
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping

POLICY_SCHEMA = "wof-training-farm-runtime-policy-v1"
DIAGNOSTIC_SCHEMA = "wof-training-farm-background-diagnostic-v1"
INPUT_AUTHORITY = "emulator-core-api-only"
PRIORITY_INTENT = "background"


class PolicyError(ValueError):
    pass


def _keys(raw: Mapping[str, Any], expected: set[str], where: str) -> None:
    if type(raw) is not dict:
        raise PolicyError(f"{where} must be an object")
    actual = set(raw)
    if actual != expected:
        raise PolicyError(
            f"{where} keys mismatch; missing={sorted(expected-actual)}; unknown={sorted(actual-expected)}"
        )


def _bool(value: Any, where: str) -> bool:
    if type(value) is not bool:
        raise PolicyError(f"{where} must be boolean")
    return value


def _int(value: Any, where: str, low: int, high: int) -> int:
    if type(value) is not int or not low <= value <= high:
        raise PolicyError(f"{where} must be strict integer in [{low}, {high}]")
    return value


def _choice(value: Any, where: str, allowed: set[str]) -> str:
    if type(value) is not str or value not in allowed:
        raise PolicyError(f"{where} must be one of {sorted(allowed)}")
    return value


@dataclass(frozen=True)
class ResourceBudget:
    configured_worker_ceiling: int
    foreground_active_worker_target: int
    idle_worker_target: int
    pressure_high_worker_target: int
    process_priority_intent: str
    cpu_budget_percent: int
    memory_budget_mib: int
    cpu_pressure_high_percent: int
    cpu_pressure_recover_percent: int
    memory_pressure_high_percent: int
    memory_pressure_recover_percent: int
    transition_cooldown_ms: int

    @classmethod
    def from_dict(cls, raw: Mapping[str, Any]) -> "ResourceBudget":
        expected = {
            "configuredWorkerCeiling", "foregroundActiveWorkerTarget", "idleWorkerTarget",
            "pressureHighWorkerTarget", "processPriorityIntent", "cpuBudgetPercent",
            "memoryBudgetMiB", "cpuPressureHighPercent", "cpuPressureRecoverPercent",
            "memoryPressureHighPercent", "memoryPressureRecoverPercent", "transitionCooldownMs",
        }
        _keys(raw, expected, "resourceBudget")
        ceiling = _int(raw["configuredWorkerCeiling"], "configuredWorkerCeiling", 1, 10)
        foreground = _int(raw["foregroundActiveWorkerTarget"], "foregroundActiveWorkerTarget", 0, ceiling)
        idle = _int(raw["idleWorkerTarget"], "idleWorkerTarget", 0, ceiling)
        pressure = _int(raw["pressureHighWorkerTarget"], "pressureHighWorkerTarget", 0, min(1, ceiling))
        priority = _choice(raw["processPriorityIntent"], "processPriorityIntent", {PRIORITY_INTENT})
        cpu_budget = _int(raw["cpuBudgetPercent"], "cpuBudgetPercent", 1, 100)
        memory_budget = _int(raw["memoryBudgetMiB"], "memoryBudgetMiB", 64, 1048576)
        cpu_high = _int(raw["cpuPressureHighPercent"], "cpuPressureHighPercent", 1, 100)
        cpu_recover = _int(raw["cpuPressureRecoverPercent"], "cpuPressureRecoverPercent", 0, 99)
        memory_high = _int(raw["memoryPressureHighPercent"], "memoryPressureHighPercent", 1, 100)
        memory_recover = _int(raw["memoryPressureRecoverPercent"], "memoryPressureRecoverPercent", 0, 99)
        cooldown = _int(raw["transitionCooldownMs"], "transitionCooldownMs", 0, 600000)
        if cpu_recover >= cpu_high or memory_recover >= memory_high:
            raise PolicyError("pressure recovery thresholds must be below high thresholds")
        return cls(ceiling, foreground, idle, pressure, priority, cpu_budget, memory_budget,
                   cpu_high, cpu_recover, memory_high, memory_recover, cooldown)

    def to_dict(self) -> dict[str, Any]:
        return {
            "configuredWorkerCeiling": self.configured_worker_ceiling,
            "foregroundActiveWorkerTarget": self.foreground_active_worker_target,
            "idleWorkerTarget": self.idle_worker_target,
            "pressureHighWorkerTarget": self.pressure_high_worker_target,
            "processPriorityIntent": self.process_priority_intent,
            "cpuBudgetPercent": self.cpu_budget_percent,
            "memoryBudgetMiB": self.memory_budget_mib,
            "cpuPressureHighPercent": self.cpu_pressure_high_percent,
            "cpuPressureRecoverPercent": self.cpu_pressure_recover_percent,
            "memoryPressureHighPercent": self.memory_pressure_high_percent,
            "memoryPressureRecoverPercent": self.memory_pressure_recover_percent,
            "transitionCooldownMs": self.transition_cooldown_ms,
        }


@dataclass(frozen=True)
class StageGuard:
    max_real_emulator_workers_this_stage: int
    real_worker_launch_enabled: bool
    real_wof_proof_claimed: bool
    r0_5_authorized: bool

    @classmethod
    def from_dict(cls, raw: Mapping[str, Any]) -> "StageGuard":
        _keys(raw, {"maxRealEmulatorWorkersThisStage", "realWorkerLaunchEnabled",
                    "realWofProofClaimed", "r0_5Authorized"}, "stageGuard")
        maximum = _int(raw["maxRealEmulatorWorkersThisStage"], "maxRealEmulatorWorkersThisStage", 1, 1)
        launch = _bool(raw["realWorkerLaunchEnabled"], "realWorkerLaunchEnabled")
        proof = _bool(raw["realWofProofClaimed"], "realWofProofClaimed")
        r05 = _bool(raw["r0_5Authorized"], "r0_5Authorized")
        if launch or proof or r05:
            raise PolicyError("R0.4.5 forbids real launch/proof and R0.5 authorization")
        return cls(maximum, launch, proof, r05)

    def to_dict(self) -> dict[str, Any]:
        return {
            "maxRealEmulatorWorkersThisStage": self.max_real_emulator_workers_this_stage,
            "realWorkerLaunchEnabled": self.real_worker_launch_enabled,
            "realWofProofClaimed": self.real_wof_proof_claimed,
            "r0_5Authorized": self.r0_5_authorized,
        }


@dataclass(frozen=True)
class RuntimePolicy:
    headless: bool
    audio_output: str
    host_keyboard_injection: bool
    host_mouse_injection: bool
    focus_stealing: bool
    gameplay_input_authority: str
    foreground_friendly: bool
    internal_framebuffer_allowed: bool
    window_presentation_required: bool
    resource_budget: ResourceBudget
    stage_guard: StageGuard

    @classmethod
    def from_dict(cls, raw: Mapping[str, Any]) -> "RuntimePolicy":
        expected = {
            "schema", "headless", "audioOutput", "hostKeyboardInjection", "hostMouseInjection",
            "focusStealing", "gameplayInputAuthority", "foregroundFriendly",
            "internalFramebufferAllowed", "windowPresentationRequired", "resourceBudget", "stageGuard",
        }
        _keys(raw, expected, "policy")
        _choice(raw["schema"], "schema", {POLICY_SCHEMA})
        headless = _bool(raw["headless"], "headless")
        audio = _choice(raw["audioOutput"], "audioOutput", {"discard"})
        keyboard = _bool(raw["hostKeyboardInjection"], "hostKeyboardInjection")
        mouse = _bool(raw["hostMouseInjection"], "hostMouseInjection")
        focus = _bool(raw["focusStealing"], "focusStealing")
        authority = _choice(raw["gameplayInputAuthority"], "gameplayInputAuthority", {INPUT_AUTHORITY})
        foreground = _bool(raw["foregroundFriendly"], "foregroundFriendly")
        framebuffer = _bool(raw["internalFramebufferAllowed"], "internalFramebufferAllowed")
        window = _bool(raw["windowPresentationRequired"], "windowPresentationRequired")
        if not headless or keyboard or mouse or focus or not foreground or not framebuffer or window:
            raise PolicyError("mandatory headless/no-host-input/background invariants violated")
        return cls(headless, audio, keyboard, mouse, focus, authority, foreground, framebuffer, window,
                   ResourceBudget.from_dict(raw["resourceBudget"]), StageGuard.from_dict(raw["stageGuard"]))

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": POLICY_SCHEMA, "headless": self.headless, "audioOutput": self.audio_output,
            "hostKeyboardInjection": self.host_keyboard_injection,
            "hostMouseInjection": self.host_mouse_injection, "focusStealing": self.focus_stealing,
            "gameplayInputAuthority": self.gameplay_input_authority,
            "foregroundFriendly": self.foreground_friendly,
            "internalFramebufferAllowed": self.internal_framebuffer_allowed,
            "windowPresentationRequired": self.window_presentation_required,
            "resourceBudget": self.resource_budget.to_dict(), "stageGuard": self.stage_guard.to_dict(),
        }

    def canonical_json(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False)

    def sha256(self) -> str:
        return hashlib.sha256(self.canonical_json().encode("ascii")).hexdigest()


def default_policy() -> RuntimePolicy:
    return RuntimePolicy.from_dict({
        "schema": POLICY_SCHEMA, "headless": True, "audioOutput": "discard",
        "hostKeyboardInjection": False, "hostMouseInjection": False, "focusStealing": False,
        "gameplayInputAuthority": INPUT_AUTHORITY, "foregroundFriendly": True,
        "internalFramebufferAllowed": True, "windowPresentationRequired": False,
        "resourceBudget": {
            "configuredWorkerCeiling": 10, "foregroundActiveWorkerTarget": 2, "idleWorkerTarget": 8,
            "pressureHighWorkerTarget": 1, "processPriorityIntent": PRIORITY_INTENT,
            "cpuBudgetPercent": 65, "memoryBudgetMiB": 8192,
            "cpuPressureHighPercent": 85, "cpuPressureRecoverPercent": 70,
            "memoryPressureHighPercent": 88, "memoryPressureRecoverPercent": 75,
            "transitionCooldownMs": 5000,
        },
        "stageGuard": {"maxRealEmulatorWorkersThisStage": 1, "realWorkerLaunchEnabled": False,
                       "realWofProofClaimed": False, "r0_5Authorized": False},
    })


def load_policy(path: str | os.PathLike[str]) -> RuntimePolicy:
    return RuntimePolicy.from_dict(json.loads(Path(path).read_text(encoding="utf-8")))


class RuntimeState(str, Enum):
    IDLE = "IDLE"
    FOREGROUND_ACTIVE = "FOREGROUND_ACTIVE"
    PRESSURE_HIGH = "PRESSURE_HIGH"
    MANUAL_PAUSE = "MANUAL_PAUSE"


@dataclass(frozen=True)
class LoadSample:
    at_ms: int
    foreground_active: bool
    cpu_percent: int
    memory_percent: int
    manual_pause: bool = False

    @classmethod
    def from_dict(cls, raw: Mapping[str, Any]) -> "LoadSample":
        _keys(raw, {"atMs", "foregroundActive", "cpuPercent", "memoryPercent", "manualPause"}, "loadSample")
        return cls(_int(raw["atMs"], "atMs", 0, 2**63-1), _bool(raw["foregroundActive"], "foregroundActive"),
                   _int(raw["cpuPercent"], "cpuPercent", 0, 100),
                   _int(raw["memoryPercent"], "memoryPercent", 0, 100), _bool(raw["manualPause"], "manualPause"))

    def to_dict(self) -> dict[str, Any]:
        return {"atMs": self.at_ms, "foregroundActive": self.foreground_active,
                "cpuPercent": self.cpu_percent, "memoryPercent": self.memory_percent,
                "manualPause": self.manual_pause}


@dataclass(frozen=True)
class ControllerDecision:
    state: RuntimeState
    desired_state: RuntimeState
    allowed_worker_target: int
    transitioned: bool
    reason: str
    next_scale_up_eligible_at_ms: int

    def to_dict(self) -> dict[str, Any]:
        return {"state": self.state.value, "desiredState": self.desired_state.value,
                "allowedWorkerTarget": self.allowed_worker_target, "transitioned": self.transitioned,
                "reason": self.reason, "nextScaleUpEligibleAtMs": self.next_scale_up_eligible_at_ms,
                "decisionOnly": True, "realWorkersStarted": 0}


class ForegroundFriendlyController:
    """Deterministic decision-only load controller; it never launches processes."""
    def __init__(self, budget: ResourceBudget):
        self.budget = budget
        self.state = RuntimeState.FOREGROUND_ACTIVE
        self.last_transition: int | None = None
        self.last_sample: int | None = None

    def _target(self, state: RuntimeState) -> int:
        return {RuntimeState.MANUAL_PAUSE: 0, RuntimeState.PRESSURE_HIGH: self.budget.pressure_high_worker_target,
                RuntimeState.FOREGROUND_ACTIVE: self.budget.foreground_active_worker_target,
                RuntimeState.IDLE: self.budget.idle_worker_target}[state]

    def _desired(self, s: LoadSample) -> tuple[RuntimeState, str]:
        if s.manual_pause:
            return RuntimeState.MANUAL_PAUSE, "MANUAL_PAUSE"
        if self.state is RuntimeState.PRESSURE_HIGH and not (
            s.cpu_percent <= self.budget.cpu_pressure_recover_percent and
            s.memory_percent <= self.budget.memory_pressure_recover_percent
        ):
            return RuntimeState.PRESSURE_HIGH, "PRESSURE_HYSTERESIS"
        if s.cpu_percent >= self.budget.cpu_pressure_high_percent or s.memory_percent >= self.budget.memory_pressure_high_percent:
            return RuntimeState.PRESSURE_HIGH, "PRESSURE_HIGH"
        return ((RuntimeState.FOREGROUND_ACTIVE, "FOREGROUND_ACTIVE") if s.foreground_active
                else (RuntimeState.IDLE, "IDLE"))

    def evaluate(self, sample: LoadSample) -> ControllerDecision:
        if type(sample) is not LoadSample:
            raise PolicyError("sample must be LoadSample")
        if self.last_sample is not None and sample.at_ms < self.last_sample:
            raise PolicyError("load sample time must be monotonic")
        desired, reason = self._desired(sample)
        transitioned = False
        if desired is not self.state:
            scale_down = self._target(desired) < self._target(self.state)
            cooldown = self.last_transition is None or sample.at_ms - self.last_transition >= self.budget.transition_cooldown_ms
            if scale_down or cooldown:
                self.state, self.last_transition, transitioned = desired, sample.at_ms, True
            else:
                reason = f"SCALE_UP_COOLDOWN:{reason}"
        self.last_sample = sample.at_ms
        next_up = sample.at_ms if self.last_transition is None else self.last_transition + self.budget.transition_cooldown_ms
        return ControllerDecision(self.state, desired, min(self._target(self.state), self.budget.configured_worker_ceiling),
                                  transitioned, reason, next_up)


@dataclass(frozen=True)
class PriorityStatus:
    platform: str
    intent: str
    attempted: bool
    applied: bool
    method: str
    detail: str

    def to_dict(self) -> dict[str, Any]:
        return {"platform": self.platform, "intent": self.intent, "attempted": self.attempted,
                "applied": self.applied, "method": self.method, "detail": self.detail,
                "proofAuthorityMutated": False}


def _windows_below_normal() -> None:
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel32.GetCurrentProcess.restype = ctypes.c_void_p
    kernel32.SetPriorityClass.argtypes = [ctypes.c_void_p, ctypes.c_uint32]
    kernel32.SetPriorityClass.restype = ctypes.c_int
    handle = kernel32.GetCurrentProcess()
    if not handle or not kernel32.SetPriorityClass(handle, 0x00004000):
        raise OSError(ctypes.get_last_error(), "SetPriorityClass(BELOW_NORMAL) failed")


def apply_background_priority(*, platform_name: str | None = None, windows_setter: Callable[[], None] | None = None,
                              posix_getter: Callable[[], int] | None = None,
                              posix_setter: Callable[[int], None] | None = None) -> PriorityStatus:
    system = platform_name or platform.system()
    if system == "Windows":
        try:
            (windows_setter or _windows_below_normal)()
            return PriorityStatus(system, PRIORITY_INTENT, True, True, "SetPriorityClass(BELOW_NORMAL)", "below-normal priority applied")
        except Exception as exc:
            return PriorityStatus(system, PRIORITY_INTENT, True, False, "SetPriorityClass(BELOW_NORMAL)", f"{type(exc).__name__}: {exc}")
    if system == "Linux":
        if posix_getter is None and not hasattr(os, "getpriority"):
            return PriorityStatus(system, PRIORITY_INTENT, False, False, "os.setpriority", "os.getpriority unavailable")
        if posix_setter is None and not hasattr(os, "setpriority"):
            return PriorityStatus(system, PRIORITY_INTENT, False, False, "os.setpriority", "os.setpriority unavailable")
        getter = posix_getter or (lambda: os.getpriority(os.PRIO_PROCESS, 0))
        setter = posix_setter or (lambda value: os.setpriority(os.PRIO_PROCESS, 0, value))
        try:
            current = getter()
            if type(current) is not int:
                raise TypeError("niceness getter returned non-integer")
            desired = min(19, max(current, 10))
            if desired != current:
                setter(desired)
            return PriorityStatus(system, PRIORITY_INTENT, True, True, "os.setpriority(PRIO_PROCESS)", f"niceness {current}->{desired}")
        except Exception as exc:
            return PriorityStatus(system, PRIORITY_INTENT, True, False, "os.setpriority(PRIO_PROCESS)", f"{type(exc).__name__}: {exc}")
    return PriorityStatus(system, PRIORITY_INTENT, False, False, "unsupported-platform", "no priority primitive for this platform")


FORBIDDEN_IMPORTS = frozenset({"pyautogui", "keyboard", "mouse", "pynput", "ahk", "autohotkey"})
FORBIDDEN_SYMBOLS = frozenset({"SendInput", "keybd_event", "mouse_event", "SetForegroundWindow", "SetFocus", "SwitchToThisWindow"})


@dataclass(frozen=True)
class SafetyViolation:
    path: str
    line: int
    kind: str
    symbol: str

    def to_dict(self) -> dict[str, Any]:
        return {"path": self.path, "line": self.line, "kind": self.kind, "symbol": self.symbol}


class _Visitor(ast.NodeVisitor):
    def __init__(self, path: Path):
        self.path, self.violations = path, []

    def add(self, node: ast.AST, kind: str, symbol: str) -> None:
        self.violations.append(SafetyViolation(str(self.path), int(getattr(node, "lineno", 0)), kind, symbol))

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            if alias.name.split(".", 1)[0] in FORBIDDEN_IMPORTS:
                self.add(node, "forbidden-import", alias.name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        if node.module and node.module.split(".", 1)[0] in FORBIDDEN_IMPORTS:
            self.add(node, "forbidden-import", node.module)
        self.generic_visit(node)

    def visit_Name(self, node: ast.Name) -> None:
        if node.id in FORBIDDEN_SYMBOLS:
            self.add(node, "forbidden-authority-symbol", node.id)
        self.generic_visit(node)

    def visit_Attribute(self, node: ast.Attribute) -> None:
        if node.attr in FORBIDDEN_SYMBOLS:
            self.add(node, "forbidden-authority-symbol", node.attr)
        self.generic_visit(node)


@dataclass(frozen=True)
class SafetyGuardStatus:
    scanned_files: tuple[str, ...]
    violations: tuple[SafetyViolation, ...]

    @property
    def passed(self) -> bool:
        return not self.violations

    def to_dict(self) -> dict[str, Any]:
        return {"passed": self.passed, "scannedFiles": list(self.scanned_files),
                "violations": [v.to_dict() for v in self.violations],
                "repositoryGuarantee": "no known host-input/focus gameplay authority in scanned Training Farm Python paths",
                "externalLibraryGuarantee": False}


def scan_no_host_input_authority(paths: Iterable[Path]) -> SafetyGuardStatus:
    scanned, violations = [], []
    for path in sorted(map(Path, paths), key=str):
        if path.suffix != ".py" or not path.is_file():
            continue
        scanned.append(str(path))
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        except Exception as exc:
            violations.append(SafetyViolation(str(path), 0, "parse-error", f"{type(exc).__name__}:{exc}"))
            continue
        visitor = _Visitor(path)
        visitor.visit(tree)
        violations.extend(visitor.violations)
    return SafetyGuardStatus(tuple(scanned), tuple(violations))


def _default_scan_paths() -> list[Path]:
    root = Path(__file__).resolve().parent
    return [p for p in root.glob("*.py") if p.name != "__init__.py"]


def build_diagnostic(policy: RuntimePolicy, sample: LoadSample, *, priority_status: PriorityStatus,
                     safety_status: SafetyGuardStatus) -> dict[str, Any]:
    decision = ForegroundFriendlyController(policy.resource_budget).evaluate(sample)
    return {
        "schema": DIAGNOSTIC_SCHEMA, "status": "PASS" if safety_status.passed else "FAIL",
        "proofScope": "ROM_FREE_RUNTIME_FOUNDATION_DIAGNOSTIC", "realWofProof": False,
        "r0_5Authorized": False, "realWorkerExecutionStarted": False,
        "stableRetroRequiredForThisDiagnostic": False, "policy": policy.to_dict(),
        "policySha256": policy.sha256(), "priority": priority_status.to_dict(),
        "loadSample": sample.to_dict(), "controllerDecision": decision.to_dict(),
        "safetyGuard": safety_status.to_dict(),
        "boundary": {"maxRealEmulatorWorkersThisStage": policy.stage_guard.max_real_emulator_workers_this_stage,
                     "fixtureEvidenceUnlocksR0_5": False, "realR0_2ProofStillOwnerGated": True,
                     "realR0_4ProofStillOwnerGated": True},
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="ROM-free Training Farm R0.4.5 background runtime diagnostic")
    parser.add_argument("--policy")
    parser.add_argument("--at-ms", type=int, default=0)
    parser.add_argument("--cpu-percent", type=int, default=20)
    parser.add_argument("--memory-percent", type=int, default=20)
    parser.add_argument("--foreground-active", action="store_true")
    parser.add_argument("--manual-pause", action="store_true")
    parser.add_argument("--skip-priority-apply", action="store_true")
    args = parser.parse_args(argv)
    try:
        policy = load_policy(args.policy) if args.policy else default_policy()
        sample = LoadSample.from_dict({"atMs": args.at_ms, "foregroundActive": args.foreground_active,
                                       "cpuPercent": args.cpu_percent, "memoryPercent": args.memory_percent,
                                       "manualPause": args.manual_pause})
        priority = (PriorityStatus(platform.system(), PRIORITY_INTENT, False, False, "skipped-by-operator",
                                   "priority application explicitly skipped") if args.skip_priority_apply
                    else apply_background_priority())
        result = build_diagnostic(policy, sample, priority_status=priority,
                                  safety_status=scan_no_host_input_authority(_default_scan_paths()))
        print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2))
        return 0 if result["status"] == "PASS" else 1
    except Exception as exc:
        print(json.dumps({"schema": DIAGNOSTIC_SCHEMA, "status": "ERROR",
                          "reasonCode": "INVALID_DIAGNOSTIC_INPUT", "detail": f"{type(exc).__name__}: {exc}",
                          "realWofProof": False, "r0_5Authorized": False,
                          "realWorkerExecutionStarted": False}, ensure_ascii=False, sort_keys=True, indent=2))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
