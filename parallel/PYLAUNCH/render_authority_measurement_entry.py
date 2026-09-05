from __future__ import annotations

import argparse
import importlib.util
import os
import tempfile
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from wof_launcher import discovery_v2 as discovery_module
from wof_launcher.browser import probe_endpoint_diagnostic
from wof_launcher.cdp import CdpClient
from wof_launcher.fixed_draw_runtime_gate import fixed_draw_gate_enabled, run_fixed_draw_runtime_gate
from wof_launcher.probe_v2 import IDENTITY_PROBE as FIELD_IDENTITY_PROBE
from wof_launcher.reentry_discovery import recover_page_only
from wof_launcher.render_measurement_ui import MeasurementPublisher, MeasurementTrayApp
from wof_launcher.state import StatusStore

ATTACH_ONLY_ENV = "WOF_ALPHA_MENU6_ATTACH_ONLY"
OWNER_NAVIGATES_ENV = "WOF_ALPHA_OWNER_NAVIGATES"
FEEDBACK_OUTPUT_NAME = "LATEST_ALPHA_FEEDBACK.txt"
FIXED_STATUS_NAME = "ALPHA_FIXED_DRAW_STATUS.json"
FIXED_FEEDBACK_MODE = "fixed-draw-first-gate"


def _load_runner(root: Path):
    runner = root / "parallel/RENDER_AUTHORITY_V3/measurement_runner.py"
    if not runner.is_file():
        raise RuntimeError("render authority V3 measurement runner missing")
    spec = importlib.util.spec_from_file_location("wof_render_authority_v3_runner", runner)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load render authority V3 runner")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _accepted(choice: Any) -> bool:
    return bool(
        choice
        and choice.page
        and choice.worker
        and choice.worker_probe
        and choice.worker_probe.get("moduleOk") is True
        and choice.identity
        and choice.identity.get("ok") is True
    )


def _endpoint_has_exact_wof(host: str, port: int) -> bool:
    endpoint, _ = probe_endpoint_diagnostic(host, port)
    if endpoint is None:
        return False
    client = CdpClient(endpoint.websocket_url, timeout=5.0)
    try:
        client.connect()
        discovery_module.IDENTITY_PROBE = FIELD_IDENTITY_PROBE
        choice = recover_page_only(
            client,
            discovery_module.discover(client, identity_cache={}),
            identity_cache={},
        )
        return _accepted(choice)
    except Exception:
        return False
    finally:
        try:
            client.close()
        except Exception:
            pass


def _choose_runner_port(host: str, preferred: int, owner_navigates: bool = True) -> tuple[int, str]:
    endpoint, _ = probe_endpoint_diagnostic(host, preferred)
    if endpoint is None:
        return preferred, "program-launch-free-port"
    if _endpoint_has_exact_wof(host, preferred):
        return preferred, "reuse-existing-exact-wof"
    if owner_navigates:
        # This is the dedicated Alpha CDP port. During rapid retest we preserve
        # the Owner's browser/tab instead of spawning a new Chrome on every fix.
        return preferred, "reuse-existing-alpha-browser"
    for port in range(preferred + 1, preferred + 11):
        candidate, _ = probe_endpoint_diagnostic(host, port)
        if candidate is None:
            return port, "program-launch-fresh-port"
    raise RuntimeError("no free local CDP port available for program-owned WOF browser")


def _single_line(value: object) -> str:
    return " ".join(str(value).splitlines()).strip()


def _write_feedback_integration_failure(
    output_root: Path,
    *,
    release_sha: str | None,
    runtime_state: str,
    payload: dict[str, Any] | None,
    error: BaseException,
) -> Path:
    output_root.mkdir(parents=True, exist_ok=True)
    output = output_root / FEEDBACK_OUTPUT_NAME
    fixed_payload = payload.get("fixedDrawSmoke") if isinstance(payload, dict) else None
    fixed_state = (
        str(fixed_payload.get("fixedSmokeState") or fixed_payload.get("state") or "").strip()
        if isinstance(fixed_payload, dict)
        else ""
    )
    reason = _single_line(f"{type(error).__name__}: {error}") or type(error).__name__
    lines = [
        "WOF Alpha Owner Feedback",
        "artifactSchema=wof-alpha-owner-feedback-integration-error-v1",
        f"generatedAt={datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')}",
        f"currentReleaseSha={release_sha or 'unknown'}",
        "alphaLive=alpha-live",
        f"liveMode={FIXED_FEEDBACK_MODE}",
        f"runtimeState={runtime_state or 'unknown'}",
        f"fixedSmokeStatusPath={output_root / FIXED_STATUS_NAME}",
        f"fixedSmokeState={fixed_state or 'unknown'}",
        "machineDrawProof=UNKNOWN",
        "ownerVisualConfirmation=NOT_RECORDED",
        "routingClassification=FEEDBACK_INPUT_MALFORMED",
        f"routingReason=OWNER_FEEDBACK_REFRESH_FAILED: {reason}",
    ]
    text = "\n".join(lines) + "\n"
    fd, temp_name = tempfile.mkstemp(prefix=".LATEST_ALPHA_FEEDBACK.p4.", suffix=".tmp", dir=output_root)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(text)
        os.replace(temp_name, output)
    finally:
        try:
            Path(temp_name).unlink(missing_ok=True)
        except OSError:
            pass
    return output


def _refresh_fixed_owner_feedback(
    output_root: Path,
    repo_root: Path,
    *,
    release_sha: str | None,
    runtime_state: str,
    payload: dict[str, Any] | None,
) -> tuple[str | None, str | None]:
    try:
        from wof_launcher.owner_feedback_acceptance import write_feedback

        _, classification = write_feedback(output_root, repo_root=repo_root)
        return classification, None
    except Exception as exc:
        detail = _single_line(f"{type(exc).__name__}: {exc}") or type(exc).__name__
        try:
            _write_feedback_integration_failure(
                output_root,
                release_sha=release_sha,
                runtime_state=runtime_state,
                payload=payload,
                error=exc,
            )
        except Exception as fallback_exc:
            fallback_detail = _single_line(f"{type(fallback_exc).__name__}: {fallback_exc}") or type(fallback_exc).__name__
            detail = f"{detail}; FALLBACK_WRITE_FAILED: {fallback_detail}"
        return "FEEDBACK_INPUT_MALFORMED", detail


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="WOF Render Authority V3 owner-visible entry")
    p.add_argument("--root", required=True)
    p.add_argument("--output-root", required=True)
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--port", type=int, default=9223)
    p.add_argument("--browser", choices=["auto", "chrome", "edge"], default="chrome")
    p.add_argument("--browser-path")
    p.add_argument("--game-url")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    root = Path(args.root).expanduser().resolve()
    output_root = Path(args.output_root).expanduser().resolve()
    output_root.mkdir(parents=True, exist_ok=True)

    store = StatusStore()
    stop = threading.Event()
    publisher = MeasurementPublisher(store)

    def request_stop() -> None:
        stop.set()

    tray = MeasurementTrayApp(store, quit_app=request_stop)
    publisher.on_change = tray.refresh
    source_commit = str(os.environ.get("WOF_ALPHA_ACCEPTANCE_COMMIT") or "").strip()
    source_label = source_commit[:8] if source_commit else "runtime"
    fixed_mode_active = fixed_draw_gate_enabled()

    def notify_blocked(reason: object) -> None:
        text = str(reason or "当前路径已 BLOCKED").strip()
        if len(text) > 240:
            text = text[:237] + "..."
        try:
            if tray.icon:
                tray.icon.notify(text, f"WOF Alpha {source_label} BLOCKED")
        except Exception:
            pass

    def forward_status(state: str, payload: dict[str, Any]) -> None:
        routed_payload = dict(payload)
        if fixed_mode_active:
            feedback_state, feedback_error = _refresh_fixed_owner_feedback(
                output_root,
                root,
                release_sha=source_commit or None,
                runtime_state=state,
                payload=routed_payload,
            )
            routed_payload["ownerFeedbackClassification"] = feedback_state
            routed_payload["ownerFeedbackRefreshOk"] = feedback_error is None
            if feedback_error is not None:
                routed_payload["ownerFeedbackRefreshError"] = feedback_error
        publisher.publish(state, **routed_payload)
        if state == "BLOCKED":
            notify_blocked(routed_payload.get("blockedReason"))

    publisher.publish(
        "STARTING",
        browserConnected=False,
        wofPageFound=False,
        workerFound=False,
        wasmFound=False,
        heapFound=False,
        browserLaunchAttempted=False,
        navigationAttempted=False,
        ownerNavigationRequired=True,
        staleGameUrlIgnored=True,
        sourceCommit=source_commit or None,
    )

    result = {"code": None}

    def worker() -> None:
        previous_attach_only = os.environ.get(ATTACH_ONLY_ENV)
        previous_owner_navigates = os.environ.get(OWNER_NAVIGATES_ENV)
        os.environ.pop(ATTACH_ONLY_ENV, None)
        os.environ[OWNER_NAVIGATES_ENV] = "1"
        try:
            if fixed_mode_active:
                result["code"] = int(
                    run_fixed_draw_runtime_gate(
                        root,
                        output_root,
                        args.host,
                        args.port,
                        args.browser,
                        args.browser_path,
                        forward_status,
                        stop,
                        acceptance_sha=source_commit or None,
                    )
                    or 0
                )
                return

            runner = _load_runner(root)
            run_port, entry_source = _choose_runner_port(args.host, args.port, owner_navigates=True)
            browser_already_running = entry_source in {"reuse-existing-exact-wof", "reuse-existing-alpha-browser"}
            publisher.publish(
                "WAITING_FOR_WOF",
                browserConnected=browser_already_running,
                wofPageFound=entry_source == "reuse-existing-exact-wof",
                workerFound=False,
                wasmFound=False,
                heapFound=False,
                browserEntrySource=entry_source,
                browserLaunchAttempted=not browser_already_running,
                navigationAttempted=False,
                ownerNavigationRequired=entry_source != "reuse-existing-exact-wof",
                staleGameUrlIgnored=True,
                configuredGameUrl=None,
                browserPort=run_port,
            )
            code = int(
                runner.run(
                    root,
                    output_root,
                    args.host,
                    run_port,
                    args.browser,
                    args.browser_path,
                    None,
                    forward_status,
                    stop,
                )
                or 0
            )
            result["code"] = code
        except Exception as exc:
            reason = f"V3 启动失败：{type(exc).__name__}: {exc}"
            publisher.publish("BLOCKED", blockedReason=reason)
            notify_blocked(reason)
            result["code"] = 12
        finally:
            if fixed_mode_active:
                feedback_state, feedback_error = _refresh_fixed_owner_feedback(
                    output_root,
                    root,
                    release_sha=source_commit or None,
                    runtime_state="STOPPED",
                    payload=None,
                )
                if feedback_error is not None:
                    publisher.publish(
                        "BLOCKED",
                        blockedReason=f"Owner feedback integration failed closed: {feedback_error}",
                        ownerFeedbackClassification=feedback_state,
                        ownerFeedbackRefreshOk=False,
                        ownerFeedbackRefreshError=feedback_error,
                    )
            if previous_attach_only is None:
                os.environ.pop(ATTACH_ONLY_ENV, None)
            else:
                os.environ[ATTACH_ONLY_ENV] = previous_attach_only
            if previous_owner_navigates is None:
                os.environ.pop(OWNER_NAVIGATES_ENV, None)
            else:
                os.environ[OWNER_NAVIGATES_ENV] = previous_owner_navigates

    thread = threading.Thread(target=worker, name="wof-render-authority-v3", daemon=True)
    thread.start()
    try:
        tray.run()
    except ImportError as exc:
        stop.set()
        try:
            import tkinter as tk
            from tkinter import messagebox

            r = tk.Tk()
            r.withdraw()
            messagebox.showerror(
                "WOF Render Authority BLOCKED",
                f"缺少托盘依赖：{exc}\n请重新运行 WOF 一键工具完成依赖安装。",
                parent=r,
            )
            r.destroy()
        except Exception:
            pass
        return 13
    finally:
        stop.set()
        thread.join(timeout=3.0)
    return int(result["code"] or 0)


if __name__ == "__main__":
    raise SystemExit(main())
