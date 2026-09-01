from __future__ import annotations

import argparse
import json
import secrets
import shutil
import subprocess
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import analyze
import local_capture

VERSION = "wof-runtime-speed-one-shot-v1"
DEFAULT_OUT_DIR = Path("parallel/RUNTIMESPEED_PROBE/out")
MAX_UPLOAD_BYTES = 320 * 1024 * 1024


def _status(message: str) -> None:
    print(message, file=sys.stderr, flush=True)


def _copy_clipboard(text: str) -> bool:
    commands: list[list[str]] = []
    if sys.platform.startswith("win"):
        commands.append(["clip.exe"])
    elif sys.platform == "darwin":
        commands.append(["pbcopy"])
    else:
        if shutil.which("wl-copy"):
            commands.append(["wl-copy"])
        if shutil.which("xclip"):
            commands.append(["xclip", "-selection", "clipboard"])
    for command in commands:
        try:
            subprocess.run(command, input=text, text=True, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True
        except Exception:
            continue
    return False


def _add_cors(handler: BaseHTTPRequestHandler) -> None:
    handler.send_header("Access-Control-Allow-Origin", "*")
    handler.send_header("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
    handler.send_header("Access-Control-Allow-Headers", "Content-Type,X-WOF-Speed-Token,X-WOF-Speed-Format")
    handler.send_header("Access-Control-Allow-Private-Network", "true")
    handler.send_header("Access-Control-Max-Age", "600")
    handler.send_header("Cache-Control", "no-store")
    handler.send_header("Cross-Origin-Resource-Policy", "cross-origin")


def _make_server(probe_source: str, token: str, out_dir: Path, seconds: float, interval_ms: float):
    event = threading.Event()
    state: dict[str, object] = {"browserPath": None, "error": None}
    server_ref: dict[str, ThreadingHTTPServer] = {}

    class Handler(BaseHTTPRequestHandler):
        server_version = "WOFSpeedProbe/1"

        def log_message(self, fmt: str, *args) -> None:
            return

        def _token_ok(self) -> bool:
            query = parse_qs(urlparse(self.path).query)
            return query.get("token", [""])[0] == token

        def _plain(self, status: int, body: bytes, content_type: str = "text/plain; charset=utf-8") -> None:
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            _add_cors(self)
            self.end_headers()
            self.wfile.write(body)

        def do_OPTIONS(self) -> None:
            self.send_response(204)
            _add_cors(self)
            self.end_headers()

        def do_GET(self) -> None:
            parsed = urlparse(self.path)
            if parsed.path != "/probe.js" or not self._token_ok():
                self._plain(404, b"not found")
                return
            server = server_ref["server"]
            port = int(server.server_address[1])
            config = {
                "seconds": seconds,
                "intervalMs": interval_ms,
                "uploadUrl": f"http://127.0.0.1:{port}/upload?token={token}",
                "token": token,
            }
            body = ("self.__WOF_SPEED_PROBE_CONFIG=" + json.dumps(config, separators=(",", ":")) + ";\n" + probe_source).encode("utf-8")
            self._plain(200, body, "application/javascript; charset=utf-8")

        def do_POST(self) -> None:
            parsed = urlparse(self.path)
            if parsed.path != "/upload" or not self._token_ok() or self.headers.get("X-WOF-Speed-Token", "") != token:
                self._plain(403, b"forbidden")
                return
            try:
                length = int(self.headers.get("Content-Length", "0"))
                if length <= 0 or length > MAX_UPLOAD_BYTES:
                    raise RuntimeError(f"invalid upload size {length}")
                payload = self.rfile.read(length)
                if len(payload) != length:
                    raise RuntimeError("browser upload truncated")
                fmt = self.headers.get("X-WOF-Speed-Format", "plain").lower()
                if fmt not in {"gzip", "plain"}:
                    raise RuntimeError(f"unsupported browser capture format {fmt!r}")
                suffix = ".wofsp.gz" if fmt == "gzip" else ".wofsp"
                path = out_dir / ("browser_speed_capture" + suffix)
                part = path.with_suffix(path.suffix + ".part")
                out_dir.mkdir(parents=True, exist_ok=True)
                part.write_bytes(payload)
                part.replace(path)
                state["browserPath"] = path
                body = json.dumps({"ok": True, "saved": path.name}, separators=(",", ":")).encode("utf-8")
                self._plain(200, body, "application/json; charset=utf-8")
            except Exception as exc:
                state["error"] = f"{type(exc).__name__}: {exc}"
                self._plain(500, str(state["error"]).encode("utf-8"))
            finally:
                event.set()

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    server.daemon_threads = True
    server_ref["server"] = server
    return server, event, state


def _tool_error(message: str) -> dict:
    return {
        "schemaVersion": analyze.RESULT_SCHEMA,
        "analyzerVersion": analyze.VERSION,
        "orchestratorVersion": VERSION,
        "verdict": "INCONCLUSIVE_TOOL_ERROR",
        "confidence": "LOW",
        "error": message,
        "readOnly": True,
        "writesGameMemory": False,
        "inputInjection": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="One-shot paired WOF WinKawaks/Browser simulation-speed probe")
    parser.add_argument("--seconds", type=float, default=15.0)
    parser.add_argument("--local-hz", type=float, default=120.0)
    parser.add_argument("--browser-interval-ms", type=float, default=8.0)
    parser.add_argument("--bridge-root", default=None)
    parser.add_argument("--out-dir", default=DEFAULT_OUT_DIR.as_posix())
    parser.add_argument("--browser-wait", type=float, default=600.0, help="seconds to wait for the one-line Browser Worker capture")
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    local_path = out_dir / "local_speed_capture.wofsp.gz"
    result_path = out_dir / "runtime_speed_result.json"
    loader_path = out_dir / "browser_worker_loader.txt"

    try:
        bridge_root = local_capture._bridge_root(args.bridge_root)
        _status("[1/3] WinKawaks: keep game active/unpaused and stop input; starting read-only ~15 s full-RAM capture.")
        local_summary = local_capture.capture(args.seconds, args.local_hz, local_path, bridge_root)
        _status(
            f"[1/3] WinKawaks done: {local_summary['sampleCount']} samples, "
            f"{local_summary['achievedHz']} reads/s. This is capture cadence, not game speed."
        )

        probe_source = (HERE / "browser_capture.js").read_text(encoding="utf-8")
        token = secrets.token_urlsafe(24)
        server, event, state = _make_server(probe_source, token, out_dir, args.seconds, args.browser_interval_ms)
        thread = threading.Thread(target=server.serve_forever, name="wof-speed-probe-http", daemon=True)
        thread.start()
        port = int(server.server_address[1])
        loader = (
            f"fetch('http://127.0.0.1:{port}/probe.js?token={token}',{{cache:'no-store'}})"
            ".then(r=>{if(!r.ok)throw new Error('probe '+r.status);return r.text()})"
            ".then(t=>(0,eval)(t))"
        )
        loader_path.write_text(loader + "\n", encoding="utf-8")
        copied = _copy_clipboard(loader)
        _status("[2/3] Browser: open the WOF page DevTools Console and select the existing gstyphoon Worker execution context.")
        if copied:
            _status("[2/3] The one-line loader is already on the clipboard. Press Ctrl+V then Enter once; then do not input for the capture.")
        else:
            _status(f"[2/3] Clipboard copy was unavailable. Paste the single line from: {loader_path.as_posix()}")
        _status("[2/3] Browser probe waits 3 s, captures ~15 s read-only, then uploads only to this loopback process.")

        completed = event.wait(timeout=max(1.0, args.browser_wait))
        server.shutdown()
        server.server_close()
        thread.join(timeout=2.0)
        if not completed:
            raise TimeoutError("Browser capture did not arrive before --browser-wait expired")
        if state.get("error"):
            raise RuntimeError(str(state["error"]))
        browser_path = state.get("browserPath")
        if not isinstance(browser_path, Path) or not browser_path.is_file():
            raise RuntimeError("Browser capture upload completed without a saved capture file")
        _status(f"[2/3] Browser done: saved {browser_path.as_posix()}")

        _status("[3/3] Automatically finding common U8/U16 game heartbeat/frame-counter candidates and comparing simulation rates.")
        local_cap = analyze.load_capture(local_path)
        if local_cap.runtime != "winkawaks":
            raise RuntimeError(f"unexpected local runtime {local_cap.runtime!r}")
        local_analysis = analyze.analyze_capture(local_cap)
        del local_cap

        browser_cap = analyze.load_capture(browser_path)
        if browser_cap.runtime != "browser":
            raise RuntimeError(f"unexpected browser runtime {browser_cap.runtime!r}")
        browser_analysis = analyze.analyze_capture(browser_cap)
        del browser_cap

        result = analyze.build_result(local_analysis, browser_analysis)
        result["orchestratorVersion"] = VERSION
        result["captures"] = {
            "winkawaks": local_path.as_posix(),
            "browser": browser_path.as_posix(),
        }
        result_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        _status(f"[3/3] Finished. Final JSON: {result_path.as_posix()}")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if not str(result.get("verdict", "")).startswith("INCONCLUSIVE") else 20
    except Exception as exc:
        result = _tool_error(f"{type(exc).__name__}: {exc}")
        result_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 30


if __name__ == "__main__":
    raise SystemExit(main())