from __future__ import annotations

import argparse
import base64
import json
import secrets
import time
import zipfile
from datetime import datetime
from pathlib import Path

from wof_launcher.browser import find_browser, launch_debug_browser, probe_endpoint_diagnostic, wait_for_endpoint_diagnostic
from wof_launcher.cdp import CdpClient
from wof_launcher import discovery_v2 as discovery_module
from wof_launcher.probe_v2 import IDENTITY_PROBE as FIELD_IDENTITY_PROBE
from wof_launcher.reentry_discovery import recover_page_only
from wof_launcher.render_authority_capture import RenderAuthorityCapture
from wof_launcher.runtime_authority import RuntimeAuthorityGuard

SAFETY = {"readOnly": True, "ramWrites": 0, "inputInjection": False, "overlayEnabled": False}
SCHEMA = "wof-render-authority-measurement-session-v2"
VERIFY_INTERVAL_S = 2.5
VERIFY_MAX_FRAMES = 12


def _write(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _page_cleanup_and_surface(client: CdpClient, target_id: str) -> dict:
    session = client.attach(target_id)
    try:
        session.request("Runtime.enable")
        expr = """(()=>{try{window.WOFOWNERPROJECTION?.stop?.()}catch(_){}try{window.WOFALPHAHUD?.dispose?.()}catch(_){}try{delete window.__WOF_OWNER_MARKER_SNAPSHOT__}catch(_){}const cs=[...document.querySelectorAll('canvas')].map((c,i)=>({index:i,width:c.width,height:c.height,clientWidth:c.clientWidth,clientHeight:c.clientHeight}));return {href:String(location.href),title:String(document.title||''),canvases:cs,legacyProjectionStopped:true,legacyAlphaHudDisposed:true,readOnly:true};})()"""
        value = session.evaluate(expr, timeout=10.0)
        return value if isinstance(value, dict) else {"readOnly": True}
    finally:
        session.close()


def _capture_verification_png(client: CdpClient, target_id: str, path: Path) -> dict:
    """Read-only Page.captureScreenshot used only as verification evidence."""
    session = client.attach(target_id)
    try:
        result = session.request("Page.captureScreenshot", {"format": "png", "fromSurface": True}, timeout=10.0)
    finally:
        session.close()
    data = result.get("data")
    if not isinstance(data, str) or not data:
        raise RuntimeError("Page.captureScreenshot returned no PNG data")
    raw = base64.b64decode(data, validate=True)
    if not raw.startswith(b"\x89PNG\r\n\x1a\n"):
        raise RuntimeError("Page.captureScreenshot payload is not PNG")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(raw)
    return {"path": path.name, "bytes": len(raw)}


def _zip_dir(session_dir: Path, zip_path: Path) -> None:
    zip_path.parent.mkdir(parents=True, exist_ok=True)
    tmp = zip_path.with_suffix(zip_path.suffix + ".partial")
    tmp.unlink(missing_ok=True)
    try:
        with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zf:
            for p in sorted(session_dir.rglob("*")):
                if p.is_file():
                    zf.write(p, p.relative_to(session_dir).as_posix())
        tmp.replace(zip_path)
    finally:
        tmp.unlink(missing_ok=True)


def run(root: Path, output_root: Path, host: str, port: int, browser: str, browser_path: str | None) -> int:
    root = root.resolve()
    output_root = output_root.resolve()
    stamp = datetime.now().astimezone().strftime("%Y%m%d_%H%M%S") + "_" + secrets.token_hex(4)
    session_dir = output_root / f"render_authority_{stamp}"
    zip_path = output_root / "packages" / f"WOF_LIVE_ACCEPTANCE_{session_dir.name}.zip"
    session_dir.mkdir(parents=True, exist_ok=True)
    events: list[dict] = []
    verification_frames: list[dict] = []
    started = datetime.now().astimezone().isoformat(timespec="seconds")

    def event(kind: str, **payload: object) -> None:
        events.append({"at": datetime.now().astimezone().isoformat(timespec="milliseconds"), "kind": kind, **payload})
        if len(events) > 160:
            del events[:-160]
        _write(session_dir / "EVENTS.json", {"schema": SCHEMA, "events": events, "safety": SAFETY})

    print("Render Authority V2 自动采集已启动。")
    print("正常进入 WOF 并正常玩 20-30 秒；无需点头、点脚、人工校准、Y/Y-Z/Y+Z 选择或 DevTools。")
    print("截图只作为 renderer/object authority 的验证证据，不作为每帧 production 位置 authority。")
    event("SESSION_STARTED", ownerAction="NORMAL_PLAY_ONLY")

    endpoint, rejection = probe_endpoint_diagnostic(host, port)
    browser_proc = None
    if endpoint is None:
        exe = find_browser(browser, browser_path)
        if not exe:
            event("BLOCKED", reason="Chrome/Edge not found")
            print("BLOCKED：未找到 Chrome/Edge。")
            return 3
        try:
            browser_proc = launch_debug_browser(exe, host=host, port=port, user_data_dir=None, game_url=None)
            endpoint, rejection = wait_for_endpoint_diagnostic(host, port, timeout=15.0)
        except Exception as exc:
            event("BLOCKED", reason=str(exc))
            print("BLOCKED：无法启动只读调试浏览器。", exc)
            return 4
    if endpoint is None:
        event("BLOCKED", reason=rejection or "browser endpoint unavailable")
        print("BLOCKED：浏览器调试端口不可用。", rejection or "")
        return 5

    client = CdpClient(endpoint.websocket_url, timeout=5.0)
    client.connect()
    guard = RuntimeAuthorityGuard()
    identity_cache: dict[str, dict] = {}
    capture = RenderAuthorityCapture(lambda rel: (root / rel).read_text(encoding="utf-8"))
    accepted = None
    authority_key = None
    runtime_epoch = None
    page_surface = None
    next_verify = 0.0
    try:
        while True:
            if accepted is None:
                discovery_module.IDENTITY_PROBE = FIELD_IDENTITY_PROBE
                choice = recover_page_only(
                    client,
                    discovery_module.discover(client, identity_cache=identity_cache),
                    identity_cache=identity_cache,
                )
                ok = bool(
                    choice.page
                    and choice.worker
                    and choice.worker_probe
                    and choice.worker_probe.get("moduleOk") is True
                    and choice.identity
                    and choice.identity.get("ok") is True
                )
                if not ok:
                    print("等待 exact World 921031 Page/Worker/WASM；正常进入游戏即可。", end="\r", flush=True)
                    time.sleep(1.0)
                    continue
                fp = guard.accept(client, choice)
                authority_key = fp.key()
                runtime_epoch = secrets.token_hex(16)
                accepted = choice
                page_id = str(choice.page.get("targetId"))
                page_surface = _page_cleanup_and_surface(client, page_id)
                started_capture = capture.ensure_started(client, choice, authority_key, runtime_epoch)
                event(
                    "EXACT_AUTHORITY_ACCEPTED",
                    authorityKey=authority_key,
                    worldSha256=choice.identity.get("sha256"),
                    runtimeEpoch=runtime_epoch,
                    rendererEpoch=started_capture.get("rendererEpoch"),
                    pageSurface=page_surface,
                )
                next_verify = time.monotonic()
                print("\n已锁定 exact World 921031。现在只需正常玩 20-30 秒。")

            healthy, reason, diag = guard.healthy(client, accepted)
            if not healthy:
                event("AUTHORITY_REVOKED", reason=reason, diagnostics=diag)
                capture.stop_runtime(client)
                guard.clear()
                identity_cache.clear()
                accepted = None
                authority_key = None
                runtime_epoch = None
                verification_frames.clear()
                _write(session_dir / "VERIFICATION_FRAMES.json", {"schema": SCHEMA, "frames": []})
                print("运行时已更换，旧采集/renderer epoch 已自动撤销；正在重新发现新 Worker。")
                time.sleep(0.5)
                continue

            polled = capture.poll(client, authority_key, runtime_epoch)
            remote = polled.get("remote") if isinstance(polled, dict) else None
            if isinstance(remote, dict):
                print(
                    f"自动采集：{remote.get('sampleCount',0)} samples / "
                    f"{remote.get('candidateCount',0)} candidates / "
                    f"{remote.get('candidateTimelineFrames',0)} timeline",
                    end="\r",
                    flush=True,
                )

            now_mono = time.monotonic()
            if (
                accepted
                and len(verification_frames) < VERIFY_MAX_FRAMES
                and now_mono >= next_verify
                and isinstance(remote, dict)
            ):
                page_id = str(accepted.page.get("targetId"))
                frame_name = f"VERIFY_{len(verification_frames):02d}.png"
                frame_meta = _capture_verification_png(client, page_id, session_dir / "verification" / frame_name)
                row = {
                    "at": datetime.now().astimezone().isoformat(timespec="milliseconds"),
                    "sampleCount": remote.get("sampleCount"),
                    "runtimeEpoch": remote.get("runtimeEpoch"),
                    "rendererEpoch": remote.get("rendererEpoch"),
                    "authorityKey": remote.get("authorityKey"),
                    "file": f"verification/{frame_meta['path']}",
                    "bytes": frame_meta["bytes"],
                    "role": "VERIFICATION_ONLY_NOT_POSITION_AUTHORITY",
                }
                verification_frames.append(row)
                _write(
                    session_dir / "VERIFICATION_FRAMES.json",
                    {"schema": SCHEMA, "frames": verification_frames, "safety": SAFETY},
                )
                next_verify = now_mono + VERIFY_INTERVAL_S

            if polled.get("state") == "ERROR":
                event("CAPTURE_ERROR", error=polled.get("error"))
                raise RuntimeError(str(polled.get("error")))
            if isinstance(remote, dict) and remote.get("captureComplete") is True:
                result = polled.get("result")
                if not isinstance(result, dict):
                    raise RuntimeError("capture result missing after captureComplete")
                result["pageSurface"] = page_surface
                result["verificationFrames"] = verification_frames
                result["sessionSafety"] = SAFETY
                _write(session_dir / "RENDER_AUTHORITY_CAPTURE_RESULT.json", result)
                event(
                    "MEASUREMENT_COMPLETE",
                    sampleCount=result.get("sampleCount"),
                    candidateCount=len(result.get("candidateRegions") or []),
                    candidateTimelineFrames=len(result.get("candidateTimeline") or []),
                    verificationFrameCount=len(verification_frames),
                )
                summary = {
                    "schema": SCHEMA,
                    "startedAt": started,
                    "endedAt": datetime.now().astimezone().isoformat(timespec="seconds"),
                    "verdict": "BOUNDED_CAPTURE_READY_FOR_RENDER_AUTHORITY_ANALYSIS",
                    "ownerAction": "NORMAL_PLAY_ONLY",
                    "worldSha256": result.get("worldSha256"),
                    "runtimeEpoch": result.get("runtimeEpoch"),
                    "rendererEpoch": result.get("rendererEpoch"),
                    "authorityKey": result.get("authorityKey"),
                    "sampleCount": result.get("sampleCount"),
                    "candidateCount": len(result.get("candidateRegions") or []),
                    "candidateTimelineFrames": len(result.get("candidateTimeline") or []),
                    "verificationFrameCount": len(verification_frames),
                    "screenshotRole": "VERIFICATION_ONLY_NOT_POSITION_AUTHORITY",
                    "legacyProjectionUsed": False,
                    "manualCalibrationUsed": False,
                    "productionOverlaySuppressedUntilAuthorityVerified": True,
                    "safety": SAFETY,
                    "zipPath": str(zip_path),
                }
                _write(session_dir / "SESSION_SUMMARY.json", summary)
                _zip_dir(session_dir, zip_path)
                (session_dir / "FINAL_ZIP.txt").write_text(str(zip_path) + "\n", encoding="utf-8")
                print("\n自动采集完成。结果包：" + str(zip_path))
                return 0
            time.sleep(0.75)
    except KeyboardInterrupt:
        event("OWNER_STOPPED")
        return 130
    except Exception as exc:
        event("CAPTURE_FAILED", error=str(exc))
        print("\n采集失败，已保留现有只读证据：", exc)
        return 6
    finally:
        try:
            capture.stop_runtime(client)
        except Exception:
            pass
        try:
            client.close()
        except Exception:
            pass
        _write(session_dir / "EVENTS.json", {"schema": SCHEMA, "events": events, "safety": SAFETY})
        _write(
            session_dir / "VERIFICATION_FRAMES.json",
            {"schema": SCHEMA, "frames": verification_frames, "safety": SAFETY},
        )
        if browser_proc is not None:
            event("BROWSER_LEFT_RUNNING_FOR_OWNER")


def main() -> int:
    p = argparse.ArgumentParser(description="Alpha V1 Render Authority V2 bounded automatic measurement")
    p.add_argument("--root", required=True)
    p.add_argument("--output-root", required=True)
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--port", type=int, default=9223)
    p.add_argument("--browser", choices=["auto", "chrome", "edge"], default="auto")
    p.add_argument("--browser-path")
    a = p.parse_args()
    return run(Path(a.root), Path(a.output_root), a.host, a.port, a.browser, a.browser_path)


if __name__ == "__main__":
    raise SystemExit(main())
