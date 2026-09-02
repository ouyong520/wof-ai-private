"""Windows one-click environment bootstrap for strict Training Farm real-WOF proof.

This module is bootstrap/UX only. It never reads ROM bytes in diagnostics mode,
never changes R0.2/R0.4 proof authority, and never authorizes R0.5.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Callable, Mapping, Sequence

from .stable_retro_backend import (
    PINNED_STABLE_RETRO,
    SUPPORTED_PYTHON_MAX,
    SUPPORTED_PYTHON_MIN,
)

REQUIREMENTS_RELATIVE = Path("training/farm/requirements-r0.1.txt")
BEGINNER_LAUNCHER_MODULE = "training.farm.beginner_real_wof_launcher"
VENV_DIRNAME = ".venv"
WORKSPACE_DIRS = ("ROM", "evidence", "logs", "runtime", "training-data", "checkpoints")
ROM_ENV = "WOF_ROM_PATH"
_DIAGNOSTIC_SCHEMA = "wof-training-farm-windows-bootstrap-diagnostic-v1"
_VERSION_RE = re.compile(r"^\d+\.\d+\.\d+(?:[A-Za-z0-9.+-]*)?$")
_PIN_RE = re.compile(r"^\s*stable-retro==([A-Za-z0-9_.+-]+)\s*$", re.MULTILINE)


class BootstrapError(RuntimeError):
    """Precise bootstrap-only failure; never a proof verdict."""


@dataclass(frozen=True)
class PythonProbe:
    source: str
    command: tuple[str, ...]
    executable: str | None
    version: tuple[int, int, int] | None
    accepted: bool
    detail: str

    def to_dict(self) -> dict[str, object]:
        data = asdict(self)
        data["command"] = list(self.command)
        data["version"] = list(self.version) if self.version is not None else None
        return data


@dataclass(frozen=True)
class VenvReport:
    state: str
    root: str
    python: str
    version: tuple[int, int, int] | None
    detail: str

    def to_dict(self) -> dict[str, object]:
        data = asdict(self)
        data["version"] = list(self.version) if self.version is not None else None
        return data


@dataclass(frozen=True)
class RequirementAuthority:
    path: str
    sha256: str
    stable_retro_expected: str
    requirements_pin: str
    consistent: bool

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


RunCommand = Callable[
    [Sequence[str], Path, Mapping[str, str] | None],
    subprocess.CompletedProcess[str],
]


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _is_within(child: Path, parent: Path) -> bool:
    try:
        child.resolve(strict=False).relative_to(parent.resolve(strict=False))
        return True
    except ValueError:
        return False


def _default_run(
    command: Sequence[str],
    cwd: Path,
    env: Mapping[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        list(command),
        cwd=str(cwd),
        env=None if env is None else dict(env),
        text=True,
        capture_output=True,
        check=False,
    )


def _strict_version(value: object) -> tuple[int, int, int]:
    if (
        type(value) is not list
        or len(value) != 3
        or any(type(part) is not int or part < 0 for part in value)
    ):
        raise BootstrapError("Python probe returned malformed strict version")
    return value[0], value[1], value[2]


def _supported(version: tuple[int, int, int]) -> bool:
    pair = version[:2]
    return SUPPORTED_PYTHON_MIN <= pair <= SUPPORTED_PYTHON_MAX


def probe_python(
    command: Sequence[str],
    *,
    source: str,
    cwd: Path,
    run: RunCommand = _default_run,
) -> PythonProbe:
    prefix = tuple(os.fspath(part) for part in command)
    snippet = (
        "import json,sys;"
        "print(json.dumps({'version':list(sys.version_info[:3]),"
        "'executable':sys.executable},separators=(',',':')))"
    )
    try:
        cp = run((*prefix, "-c", snippet), cwd, None)
    except OSError as exc:
        return PythonProbe(source, prefix, None, None, False, f"not runnable: {type(exc).__name__}: {exc}")
    if cp.returncode != 0:
        detail = (cp.stderr or cp.stdout or "candidate failed").strip().replace("\n", " ")[:500]
        return PythonProbe(source, prefix, None, None, False, f"exit={cp.returncode}: {detail}")
    try:
        payload = json.loads((cp.stdout or "").strip())
        if type(payload) is not dict or set(payload) != {"version", "executable"}:
            raise BootstrapError("unexpected Python probe object")
        version = _strict_version(payload["version"])
        executable = payload["executable"]
        if type(executable) is not str or not executable:
            raise BootstrapError("Python probe executable is malformed")
    except (json.JSONDecodeError, BootstrapError) as exc:
        return PythonProbe(source, prefix, None, None, False, f"malformed probe: {exc}")
    if not _supported(version):
        return PythonProbe(
            source,
            prefix,
            executable,
            version,
            False,
            f"unsupported {version[0]}.{version[1]}; required "
            f"{SUPPORTED_PYTHON_MIN[0]}.{SUPPORTED_PYTHON_MIN[1]}.."
            f"{SUPPORTED_PYTHON_MAX[0]}.{SUPPORTED_PYTHON_MAX[1]}",
        )
    return PythonProbe(source, prefix, executable, version, True, "supported")


def venv_python_path(local_root: Path, *, windows: bool | None = None) -> Path:
    use_windows = os.name == "nt" if windows is None else windows
    return local_root / VENV_DIRNAME / ("Scripts/python.exe" if use_windows else "bin/python")


def python_candidate_commands(
    *,
    local_root: Path,
    explicit_python: str | None = None,
    windows: bool | None = None,
) -> list[tuple[str, tuple[str, ...]]]:
    result: list[tuple[str, tuple[str, ...]]] = []
    if explicit_python:
        result.append(("explicit", (explicit_python,)))
    vpy = venv_python_path(local_root, windows=windows)
    if vpy.is_file():
        result.append(("existing-venv", (str(vpy),)))
    for minor in range(SUPPORTED_PYTHON_MAX[1], SUPPORTED_PYTHON_MIN[1] - 1, -1):
        result.append((f"py-{SUPPORTED_PYTHON_MIN[0]}.{minor}", ("py", f"-{SUPPORTED_PYTHON_MIN[0]}.{minor}")))
    result.append(("PATH-python", ("python",)))
    result.append(("PATH-python3", ("python3",)))
    deduped: list[tuple[str, tuple[str, ...]]] = []
    seen: set[tuple[str, ...]] = set()
    for item in result:
        if item[1] not in seen:
            seen.add(item[1])
            deduped.append(item)
    return deduped


def discover_python(
    *,
    local_root: Path,
    repo: Path,
    explicit_python: str | None = None,
    windows: bool | None = None,
    run: RunCommand = _default_run,
) -> tuple[PythonProbe | None, list[PythonProbe]]:
    probes: list[PythonProbe] = []
    selected: PythonProbe | None = None
    for source, command in python_candidate_commands(
        local_root=local_root,
        explicit_python=explicit_python,
        windows=windows,
    ):
        probe = probe_python(command, source=source, cwd=repo, run=run)
        probes.append(probe)
        if selected is None and probe.accepted:
            selected = probe
    return selected, probes


def requirement_authority(repo: Path) -> RequirementAuthority:
    path = repo / REQUIREMENTS_RELATIVE
    try:
        raw = path.read_bytes()
        text = raw.decode("utf-8")
    except (OSError, UnicodeError) as exc:
        raise BootstrapError(f"cannot read requirement authority: {type(exc).__name__}: {exc}") from exc
    pins = _PIN_RE.findall(text)
    if len(pins) != 1:
        raise BootstrapError("requirements-r0.1.txt must contain exactly one stable-retro== pin")
    req_pin = pins[0]
    expected = PINNED_STABLE_RETRO
    return RequirementAuthority(
        path=str(path),
        sha256=hashlib.sha256(raw).hexdigest(),
        stable_retro_expected=expected,
        requirements_pin=req_pin,
        consistent=req_pin == expected,
    )


def inspect_venv(
    *,
    local_root: Path,
    repo: Path,
    windows: bool | None = None,
    run: RunCommand = _default_run,
) -> VenvReport:
    vroot = local_root / VENV_DIRNAME
    vpy = venv_python_path(local_root, windows=windows)
    if not vroot.exists():
        return VenvReport("ABSENT", str(vroot), str(vpy), None, "dedicated venv does not exist")
    if not vroot.is_dir() or not vpy.is_file():
        return VenvReport("BROKEN", str(vroot), str(vpy), None, "venv exists but its Python executable is missing")
    probe = probe_python((str(vpy),), source="venv-state", cwd=repo, run=run)
    if probe.version is None:
        return VenvReport("BROKEN", str(vroot), str(vpy), None, probe.detail)
    if not probe.accepted:
        return VenvReport("STALE_UNSUPPORTED", str(vroot), str(vpy), probe.version, probe.detail)
    return VenvReport("VALID", str(vroot), str(vpy), probe.version, "supported reusable dedicated venv")


def create_workspace(local_root: Path) -> dict[str, str]:
    local_root.mkdir(parents=True, exist_ok=True)
    created: dict[str, str] = {}
    for name in WORKSPACE_DIRS:
        path = local_root / name
        path.mkdir(parents=True, exist_ok=True)
        created[name] = str(path)
    return created


def create_venv(
    selected: PythonProbe,
    *,
    local_root: Path,
    repo: Path,
    windows: bool | None = None,
    run: RunCommand = _default_run,
) -> VenvReport:
    command = (*selected.command, "-m", "venv", str(local_root / VENV_DIRNAME))
    cp = run(command, repo, None)
    if cp.returncode != 0:
        detail = (cp.stderr or cp.stdout or "venv creation failed").strip().replace("\n", " ")[:800]
        raise BootstrapError(f"VENV_CREATE_FAILED exit={cp.returncode}: {detail}")
    report = inspect_venv(local_root=local_root, repo=repo, windows=windows, run=run)
    if report.state != "VALID":
        raise BootstrapError(f"VENV_CREATE_FAILED post-check={report.state}: {report.detail}")
    return report


def classify_pip_failure(cp: subprocess.CompletedProcess[str]) -> tuple[str, str]:
    text = (cp.stderr or cp.stdout or "pip failed").strip().replace("\n", " ")[:1200]
    low = text.lower()
    network_tokens = (
        "connection",
        "timed out",
        "temporary failure",
        "name or service not known",
        "proxy",
        "ssl",
        "certificate verify",
        "resolve",
        "network is unreachable",
    )
    build_tokens = (
        "failed building wheel",
        "could not build wheels",
        "error: command",
        "microsoft visual c++",
        "subprocess-exited-with-error",
        "build dependencies",
    )
    if any(token in low for token in network_tokens):
        return "NETWORK_OR_INDEX_UNAVAILABLE", text
    if any(token in low for token in build_tokens):
        return "WHEEL_OR_BUILD_FAILURE", text
    return "PACKAGE_INSTALL_FAILURE", text


def sync_dependencies(
    *,
    venv_python: Path,
    authority: RequirementAuthority,
    repo: Path,
    run: RunCommand = _default_run,
) -> dict[str, object]:
    if not authority.consistent:
        raise BootstrapError(
            "DEPENDENCY_AUTHORITY_MISMATCH: requirements pin "
            f"{authority.requirements_pin!r} != stable_retro_backend pin "
            f"{authority.stable_retro_expected!r}"
        )
    command = (
        str(venv_python),
        "-m",
        "pip",
        "install",
        "--disable-pip-version-check",
        "--requirement",
        authority.path,
    )
    cp = run(command, repo, None)
    if cp.returncode != 0:
        reason, detail = classify_pip_failure(cp)
        raise BootstrapError(f"{reason}: {detail}")
    return {"state": "SYNCED", "command": list(command), "exitCode": cp.returncode}


def probe_dependencies(
    *,
    venv_python: Path,
    repo: Path,
    run: RunCommand = _default_run,
    base_environment: Mapping[str, str] | None = None,
) -> dict[str, object]:
    snippet = (
        "import json;"
        "from training.farm.stable_retro_backend import dependency_probe;"
        "print(json.dumps(dependency_probe(None).to_dict(),sort_keys=True,separators=(',',':')))"
    )
    env = dict(os.environ if base_environment is None else base_environment)
    env.pop(ROM_ENV, None)
    cp = run((str(venv_python), "-c", snippet), repo, env)
    if cp.returncode != 0:
        detail = (cp.stderr or cp.stdout or "dependency probe failed").strip().replace("\n", " ")[:1000]
        raise BootstrapError(f"FBNEO_PROBE_EXECUTION_FAILED exit={cp.returncode}: {detail}")
    try:
        report = json.loads((cp.stdout or "").strip())
    except json.JSONDecodeError as exc:
        raise BootstrapError(f"FBNEO_PROBE_MALFORMED: {exc}") from exc
    if type(report) is not dict:
        raise BootstrapError("FBNEO_PROBE_MALFORMED: expected JSON object")
    return report


def dependency_readiness(report: Mapping[str, object], authority: RequirementAuthority) -> tuple[bool, str]:
    if report.get("stable_retro_present") is not True:
        return False, f"stable-retro=={authority.stable_retro_expected} is not importable in dedicated venv"
    if report.get("stable_retro_version") != authority.stable_retro_expected:
        return False, (
            f"wrong stable-retro version {report.get('stable_retro_version')!r}; "
            f"expected {authority.stable_retro_expected}"
        )
    if report.get("pinned_version_match") is not True:
        return False, "Stable-Retro backend reports pinned-version mismatch"
    if report.get("fbneo_declared") is not True:
        return False, "FBNeo button declaration probe failed"
    if report.get("fbneo_zip_mapping") is not True:
        return False, "FBNeo ZIP mapping probe failed"
    if report.get("platform_supported") is not True:
        return False, "current platform is not supported by Training Farm FBNeo backend"
    return True, "pinned Stable-Retro + FBNeo capability ready"


def ensure_evidence_root(evidence_root: Path, repo: Path) -> Path:
    path = evidence_root.expanduser().resolve(strict=False)
    if _is_within(path, repo):
        raise BootstrapError("EVIDENCE_ROOT_UNSAFE: evidence root must stay outside repository tree")
    try:
        path.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        raise BootstrapError(f"EVIDENCE_ROOT_UNAVAILABLE: {type(exc).__name__}: {exc}") from exc
    if not path.is_dir():
        raise BootstrapError("EVIDENCE_ROOT_UNAVAILABLE: path is not a directory")
    return path


def launch_beginner_proof(
    *,
    venv_python: Path,
    repo: Path,
    evidence_root: Path,
    rom_argument: str | None,
    allow_unrecorded_rom: bool,
    run: RunCommand = _default_run,
    base_environment: Mapping[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    command: list[str] = [
        str(venv_python),
        "-m",
        BEGINNER_LAUNCHER_MODULE,
        "--evidence-root",
        str(evidence_root),
    ]
    if allow_unrecorded_rom:
        command.append("--allow-unrecorded-rom")
    if rom_argument:
        command.append(rom_argument)
    env = dict(os.environ if base_environment is None else base_environment)
    return run(command, repo, env)


def _default_local_root(repo: Path) -> Path:
    return repo.parent


def _diagnostic(
    *,
    repo: Path,
    local_root: Path,
    evidence_root: Path,
    explicit_python: str | None,
    windows: bool | None,
    run: RunCommand,
    environment: Mapping[str, str] | None,
) -> dict[str, object]:
    selected, probes = discover_python(
        local_root=local_root,
        repo=repo,
        explicit_python=explicit_python,
        windows=windows,
        run=run,
    )
    authority: RequirementAuthority | None
    authority_error: str | None = None
    try:
        authority = requirement_authority(repo)
    except BootstrapError as exc:
        authority = None
        authority_error = str(exc)
    venv = inspect_venv(local_root=local_root, repo=repo, windows=windows, run=run)
    dep_probe: dict[str, object] | None = None
    dep_state = "NOT_PROBED"
    if venv.state == "VALID" and authority is not None:
        try:
            dep_probe = probe_dependencies(
                venv_python=Path(venv.python),
                repo=repo,
                run=run,
                base_environment=environment,
            )
            ready, detail = dependency_readiness(dep_probe, authority)
            dep_state = "READY" if ready else f"NOT_READY: {detail}"
        except BootstrapError as exc:
            dep_state = f"PROBE_FAILED: {exc}"
    launcher_path = repo / "training/farm/beginner_real_wof_launcher.py"
    evidence_safe = not _is_within(evidence_root, repo)
    proof_ready = bool(
        venv.state == "VALID"
        and authority is not None
        and authority.consistent
        and dep_state == "READY"
        and launcher_path.is_file()
        and evidence_safe
    )
    return {
        "schema": _DIAGNOSTIC_SCHEMA,
        "status": "PASS",
        "repositoryRoot": str(repo),
        "localRoot": str(local_root),
        "pythonSupportedRange": {
            "min": list(SUPPORTED_PYTHON_MIN),
            "max": list(SUPPORTED_PYTHON_MAX),
        },
        "pythonCandidates": [probe.to_dict() for probe in probes],
        "selectedPython": selected.to_dict() if selected else None,
        "venv": venv.to_dict(),
        "requirementAuthority": authority.to_dict() if authority else None,
        "requirementAuthorityError": authority_error,
        "dependencySyncState": "NOT_RUN_DIAGNOSTICS",
        "dependencyProbeState": dep_state,
        "dependencyProbe": dep_probe,
        "evidenceRoot": str(evidence_root),
        "evidenceRootSafe": evidence_safe,
        "proofLauncherPath": str(launcher_path),
        "proofLauncherReady": proof_ready,
        "romAccessed": False,
        "realWofProof": False,
        "r0_5Authorized": False,
        "realWorkerExecutionStarted": False,
    }


def run_bootstrap(
    *,
    repo: Path,
    local_root: Path,
    evidence_root: Path,
    explicit_python: str | None = None,
    windows: bool | None = None,
    prepare_only: bool = False,
    rom_argument: str | None = None,
    allow_unrecorded_rom: bool = False,
    run: RunCommand = _default_run,
    environment: Mapping[str, str] | None = None,
) -> int:
    if _is_within(local_root, repo):
        print("BLOCKED — LOCAL_ROOT_UNSAFE — local root must not be inside repository tree")
        return 5
    try:
        authority = requirement_authority(repo)
    except BootstrapError as exc:
        print(f"BLOCKED — {exc}")
        return 5
    if not authority.consistent:
        print(
            "BLOCKED — DEPENDENCY_AUTHORITY_MISMATCH — "
            f"requirements={authority.requirements_pin}, backend={authority.stable_retro_expected}"
        )
        return 5

    selected, probes = discover_python(
        local_root=local_root,
        repo=repo,
        explicit_python=explicit_python,
        windows=windows,
        run=run,
    )
    if selected is None:
        examined = "; ".join(f"{p.source}: {p.detail}" for p in probes)
        print(
            "WAITING_PREREQUISITE — 未找到受支持 Python。"
            f"需要 {SUPPORTED_PYTHON_MIN[0]}.{SUPPORTED_PYTHON_MIN[1]}.."
            f"{SUPPORTED_PYTHON_MAX[0]}.{SUPPORTED_PYTHON_MAX[1]}；"
            "安装一个受支持版本后重新双击，无需卸载现有 Python。 "
            f"examined=[{examined}]"
        )
        return 2

    try:
        create_workspace(local_root)
        before = inspect_venv(local_root=local_root, repo=repo, windows=windows, run=run)
        if before.state in {"BROKEN", "STALE_UNSUPPORTED"}:
            raise BootstrapError(
                f"VENV_{before.state}: {before.python}; {before.detail}. "
                "请手动重命名/删除该专用 .venv 后重试；bootstrap 不会静默覆盖未知环境。"
            )
        current = before
        if before.state == "ABSENT":
            current = create_venv(
                selected,
                local_root=local_root,
                repo=repo,
                windows=windows,
                run=run,
            )
        venv_python = Path(current.python)
        sync_dependencies(
            venv_python=venv_python,
            authority=authority,
            repo=repo,
            run=run,
        )
        dep = probe_dependencies(
            venv_python=venv_python,
            repo=repo,
            run=run,
            base_environment=environment,
        )
        ready, detail = dependency_readiness(dep, authority)
        if not ready:
            raise BootstrapError(f"FBNEO_CAPABILITY_NOT_READY: {detail}")
        evidence = ensure_evidence_root(evidence_root, repo)
    except BootstrapError as exc:
        text = str(exc)
        if text.startswith("NETWORK_OR_INDEX_UNAVAILABLE"):
            print(f"WAITING_PREREQUISITE — {text}")
            return 2
        print(f"BLOCKED — {text}")
        return 5

    print(
        "READY_FOR_OWNER_PROOF — dedicated .venv + exact dependencies + FBNeo capability ready; "
        f"venv={venv_python}; evidence={evidence}"
    )
    if prepare_only:
        return 0

    cp = launch_beginner_proof(
        venv_python=venv_python,
        repo=repo,
        evidence_root=evidence,
        rom_argument=rom_argument,
        allow_unrecorded_rom=allow_unrecorded_rom,
        run=run,
        base_environment=environment,
    )
    if cp.stdout:
        print(cp.stdout, end="" if cp.stdout.endswith("\n") else "\n")
    if cp.stderr:
        print(cp.stderr, file=sys.stderr, end="" if cp.stderr.endswith("\n") else "\n")
    return int(cp.returncode)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Training Farm R0.4.6 Windows OneClick environment bootstrap"
    )
    ap.add_argument("rom", nargs="?", help="optional external WOF ZIP forwarded to existing beginner launcher")
    ap.add_argument("--local-root", help="local workspace root; default is repository parent")
    ap.add_argument("--evidence-root", help="external evidence root; default is <local-root>/evidence")
    ap.add_argument("--python", dest="explicit_python", help="optional preferred Python executable")
    ap.add_argument("--prepare-only", action="store_true", help="prepare environment and stop before ROM picker/proof")
    ap.add_argument("--diagnostics-json", action="store_true", help="ROM-free diagnostics; no venv/package mutation")
    ap.add_argument("--allow-unrecorded-rom", action="store_true", help="EXPERT ONLY; forwarded unchanged to existing launcher")
    args = ap.parse_args(argv)

    repo = repo_root().resolve(strict=False)
    local = Path(args.local_root).expanduser().resolve(strict=False) if args.local_root else _default_local_root(repo)
    evidence = (
        Path(args.evidence_root).expanduser().resolve(strict=False)
        if args.evidence_root
        else local / "evidence"
    )
    if args.diagnostics_json:
        payload = _diagnostic(
            repo=repo,
            local_root=local,
            evidence_root=evidence,
            explicit_python=args.explicit_python,
            windows=None,
            run=_default_run,
            environment=os.environ,
        )
        print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
        return 0
    return run_bootstrap(
        repo=repo,
        local_root=local,
        evidence_root=evidence,
        explicit_python=args.explicit_python,
        prepare_only=args.prepare_only,
        rom_argument=args.rom,
        allow_unrecorded_rom=args.allow_unrecorded_rom,
        run=_default_run,
        environment=os.environ,
    )


if __name__ == "__main__":
    raise SystemExit(main())
