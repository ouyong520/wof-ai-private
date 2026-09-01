from __future__ import annotations

import queue
import subprocess
import threading
import time
from dataclasses import dataclass, field
from typing import Any

import unified_live_proof_base as _base

# Re-export the frozen implementation surface first. Focused generation-bound
# overrides below are then installed back into the base module so existing
# functions (including run_live) resolve the hardened objects through their
# original module globals.
for _name in dir(_base):
    if not _name.startswith("__"):
        globals()[_name] = getattr(_base, _name)

_BaseRecorderEvidence = _base.RecorderEvidence
_BaseBuildStatus = _base.build_status
_BaseStartChild = _base.start_child


def _valid_source_generation(value: Any) -> bool:
    if isinstance(value, bool) or value is None:
        return False
    if isinstance(value, int):
        return value > 0
    return isinstance(value, str) and bool(value.strip())


@dataclass
class RecorderEvidence(_BaseRecorderEvidence):
    # Runtime/supervisor generation is immutable for one Recorder child reader.
    source_generation: str | int | None = None
    source_generation_epoch: int = 0
    source_generation_order: int | None = None
    source_generation_started_utc: str | None = None
    admission_source_generation: str | int | None = None
    source_revoked: bool = False

    # Rejected authority-like events remain diagnostic only and never mutate the
    # current authority slot or freshness clock.
    rejected_authority_events: int = 0
    last_rejected_authority_reason: str | None = None
    last_rejected_authority_source_generation: str | int | None = None
    last_rejected_authority_line: str | None = None

    _source_admission_seen: bool = field(default=False, repr=False)
    _legacy_admission_count: int = field(default=0, repr=False)
    _legacy_seen_admission_lines: set[str] = field(default_factory=set, repr=False)

    def _revoke_current_authority(self, *, clear_fatal: bool) -> None:
        self.admitted = False
        self.admission_line = None
        self.admission_generation = None
        self.admission_output_generation = None
        self.admission_authority_generation = None
        self.admission_source_generation = None
        # A rollover/revocation must invalidate freshness immediately.
        self._last_output_monotonic = None
        if clear_fatal:
            self.fatal = False
            self.fatal_line = None

    def begin_source_generation(
        self,
        source_generation: str | int,
        *,
        order: int | None = None,
    ) -> bool:
        """Bind subsequent authority events to one exact Recorder runtime generation."""
        if not _valid_source_generation(source_generation):
            raise ValueError("Recorder source generation must be a non-empty string or positive integer")
        if order is not None and (isinstance(order, bool) or not isinstance(order, int) or order <= 0):
            raise ValueError("Recorder source generation order must be a positive integer")
        if self.source_generation == source_generation:
            return False

        self.source_generation = source_generation
        self.source_generation_epoch += 1
        self.source_generation_order = order
        self.source_generation_started_utc = _base.utc_now()
        self.source_revoked = False
        self._source_admission_seen = False
        self._revoke_current_authority(clear_fatal=True)
        return True

    def _reject_authority(
        self,
        reason: str,
        text: str,
        source_generation: str | int | None,
    ) -> None:
        self.rejected_authority_events += 1
        self.last_rejected_authority_reason = reason
        self.last_rejected_authority_source_generation = source_generation
        self.last_rejected_authority_line = text

    def _accept_fatal(self, text: str) -> None:
        self.generation += 1
        self.fatal = True
        self.fatal_line = text
        self.fatal_generation = self.generation
        self._revoke_current_authority(clear_fatal=False)
        self.ever_fatal = True
        self.last_fatal_line = text

    def _accept_admission(
        self,
        text: str,
        source_generation: str | int | None,
    ) -> None:
        self.generation += 1
        self.admitted = True
        self.admission_line = text
        self.admission_generation = self.generation
        self.admission_output_generation = self.output_generation
        self.admission_source_generation = source_generation
        self.fatal = False
        self.fatal_line = None
        self.ever_admitted = True
        self.last_admission_line = text
        self._advance_authority("admission", text)
        self.admission_authority_generation = self.authority_generation

    def feed(
        self,
        line: str,
        *,
        source_generation: str | int | None = None,
    ) -> None:
        text = line.strip()
        if not text:
            return

        # Generic stdout remains diagnostic only.
        self.output_generation += 1
        self.last_output_utc = _base.utc_now()
        self._last_diagnostic_output_monotonic = time.monotonic()
        self.lines.append(text)
        self.lines[:] = self.lines[-120:]

        is_fatal = any(mark in text for mark in _base.FATAL_MARKERS)
        is_admission = any(mark in text for mark in _base.ADMISSION_MARKERS)
        is_heartbeat = _base._trusted_fleet_supervisor_heartbeat(text)
        if not (is_fatal or is_admission or is_heartbeat):
            return

        # Strict runtime path: once a source generation has been activated,
        # authority-like input without that exact token fails closed.
        if self.source_generation is not None:
            if not _valid_source_generation(source_generation):
                self._reject_authority("missing-source-generation", text, source_generation)
                return
            if source_generation != self.source_generation:
                self._reject_authority("stale-or-wrong-source-generation", text, source_generation)
                return
            if self.source_revoked:
                self._reject_authority("source-generation-revoked", text, source_generation)
                return

            if is_fatal:
                self._accept_fatal(text)
                self.source_revoked = True
                return
            if is_admission:
                if self._source_admission_seen:
                    self._reject_authority("duplicate-admission-same-source-generation", text, source_generation)
                    return
                self._source_admission_seen = True
                self._accept_admission(text, source_generation)
                return
            if (
                is_heartbeat
                and self.admitted
                and not self.fatal
                and self.admission_source_generation == self.source_generation
            ):
                self._advance_authority("supervisor-heartbeat", text)
            return

        # Legacy single-generation compatibility is intentionally narrow so the
        # pre-fix independent QA fixture can be replayed unchanged. After any
        # unbound authority rollover, heartbeat provenance is missing and fails
        # closed; a byte-identical admission replay is also rejected.
        if is_fatal:
            self._accept_fatal(text)
            return
        if is_admission:
            if text in self._legacy_seen_admission_lines:
                self._reject_authority("replayed-unbound-admission", text, None)
                return
            self._legacy_seen_admission_lines.add(text)
            self._legacy_admission_count += 1
            self._accept_admission(text, None)
            return
        if is_heartbeat and self.admitted and not self.fatal:
            if self._legacy_admission_count == 1:
                self._advance_authority("supervisor-heartbeat", text)
            else:
                self._reject_authority("missing-source-generation-after-rollover", text, None)


_child_generation_lock = threading.Lock()
_child_generation_counter = 0


def start_child(cmd: list[str], cwd: Any) -> subprocess.Popen[str]:
    global _child_generation_counter
    proc = _BaseStartChild(cmd, cwd)
    with _child_generation_lock:
        _child_generation_counter += 1
        order = _child_generation_counter
    pid = getattr(proc, "pid", None)
    token = f"recorder-child:{order}:pid:{pid if isinstance(pid, int) else 'unknown'}"
    setattr(proc, "_wof_authority_generation", token)
    setattr(proc, "_wof_authority_generation_order", order)
    return proc


def _reader_generation(proc: Any) -> tuple[str | int | None, int | None]:
    token = getattr(proc, "_wof_authority_generation", None)
    order = getattr(proc, "_wof_authority_generation_order", None)
    if _valid_source_generation(token):
        return token, order if isinstance(order, int) and not isinstance(order, bool) and order > 0 else None
    pid = getattr(proc, "pid", None)
    if isinstance(pid, int) and not isinstance(pid, bool) and pid > 0:
        return f"recorder-pid:{pid}:object:{id(proc):x}", None
    return None, None


def reader(
    proc: subprocess.Popen[str],
    prefix: str,
    evidence: RecorderEvidence | None,
    q: "queue.Queue[tuple[str, str]]",
    source_generation: str | int | None = None,
) -> None:
    if proc.stdout is None:
        return

    token = source_generation
    order: int | None = None
    if evidence is not None:
        if token is None:
            token, order = _reader_generation(proc)
        if _valid_source_generation(token):
            if evidence.source_generation is None:
                evidence.begin_source_generation(token, order=order)
            elif token != evidence.source_generation:
                current_order = evidence.source_generation_order
                if (
                    order is not None
                    and current_order is not None
                    and order > current_order
                ):
                    evidence.begin_source_generation(token, order=order)
                # If order is older/unknown, do not roll authority backward;
                # feed below will reject its authority-like events by token.

    buf: list[str] = []

    def emit() -> None:
        if not buf:
            return
        line = "".join(buf)
        buf.clear()
        if evidence is not None:
            evidence.feed(line, source_generation=token)
        q.put((prefix, line))

    while True:
        ch = proc.stdout.read(1)
        if not ch:
            break
        if ch in {"\r", "\n"}:
            emit()
            continue
        buf.append(ch)
        if len(buf) >= 16384:
            emit()
    emit()


def build_status(*args: Any, **kwargs: Any) -> dict[str, Any]:
    value = _BaseBuildStatus(*args, **kwargs)
    recorder = kwargs.get("recorder")
    if isinstance(recorder, RecorderEvidence):
        live = value.get("live") if isinstance(value.get("live"), dict) else {}
        admission = (
            live.get("recorderDiscoveryV2Admission")
            if isinstance(live.get("recorderDiscoveryV2Admission"), dict)
            else None
        )
        if admission is not None:
            admission.update({
                "sourceGeneration": recorder.source_generation,
                "sourceGenerationEpoch": recorder.source_generation_epoch,
                "sourceGenerationOrder": recorder.source_generation_order,
                "sourceGenerationStartedUtc": recorder.source_generation_started_utc,
                "admissionSourceGeneration": recorder.admission_source_generation,
                "sourceRevoked": recorder.source_revoked,
                "rejectedAuthorityEvents": recorder.rejected_authority_events,
                "lastRejectedAuthorityReason": recorder.last_rejected_authority_reason,
                "lastRejectedAuthoritySourceGeneration": recorder.last_rejected_authority_source_generation,
                "lastRejectedAuthorityEvidence": recorder.last_rejected_authority_line,
            })
    return value


# Install hardened symbols into the frozen implementation module. Functions
# defined there resolve these names at call time, so run_live keeps its existing
# orchestration while its Recorder child/reader now carries immutable generation.
_base.RecorderEvidence = RecorderEvidence
_base.start_child = start_child
_base.reader = reader
_base.build_status = build_status

globals().update({
    "RecorderEvidence": RecorderEvidence,
    "start_child": start_child,
    "reader": reader,
    "build_status": build_status,
})


def main() -> int:
    return _base.main()


if __name__ == "__main__":
    raise SystemExit(main())
