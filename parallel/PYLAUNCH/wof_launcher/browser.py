from __future__ import annotations

import ipaddress
import json
import os
import subprocess
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit


@dataclass(frozen=True)
class BrowserEndpoint:
    host: str
    port: int
    browser: str
    websocket_url: str

    @property
    def http_base(self) -> str:
        return f"http://{self.host}:{self.port}"


def _http_json(url: str, timeout: float = 0.8) -> dict[str, Any]:
    request = urllib.request.Request(url, headers={"User-Agent": "WOF-Future-Danger-Launcher/0.1"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def is_loopback_host(host: str) -> bool:
    value = str(host or "").strip().lower().rstrip(".")
    if value == "localhost":
        return True
    try:
        return ipaddress.ip_address(value).is_loopback
    except ValueError:
        return False


def websocket_matches_endpoint(websocket_url: str, host: str, port: int) -> bool:
    if not is_loopback_host(host):
        return False
    try:
        parsed = urlsplit(websocket_url)
        ws_host = parsed.hostname
        ws_port = parsed.port
    except (TypeError, ValueError):
        return False
    if parsed.scheme not in {"ws", "wss"} or not ws_host or ws_port is None:
        return False
    return is_loopback_host(ws_host) and ws_port == int(port)


def probe_endpoint(host: str, port: int) -> BrowserEndpoint | None:
    if not is_loopback_host(host):
        return None
    try:
        payload = _http_json(f"http://{host}:{port}/json/version")
    except (OSError, ValueError, urllib.error.URLError):
        return None
    ws = payload.get("webSocketDebuggerUrl")
    if not isinstance(ws, str) or not websocket_matches_endpoint(ws, host, port):
        return None
    return BrowserEndpoint(host=host, port=port, browser=str(payload.get("Browser") or "Chromium"), websocket_url=ws)


def browser_candidates(preference: str = "auto") -> list[Path]:
    env = os.environ
    local = Path(env.get("LOCALAPPDATA", ""))
    pf = Path(env.get("PROGRAMFILES", "C:/Program Files"))
    pfx86 = Path(env.get("PROGRAMFILES(X86)", "C:/Program Files (x86)"))
    chrome = [
        local / "Google/Chrome/Application/chrome.exe",
        pf / "Google/Chrome/Application/chrome.exe",
        pfx86 / "Google/Chrome/Application/chrome.exe",
    ]
    edge = [
        pf / "Microsoft/Edge/Application/msedge.exe",
        pfx86 / "Microsoft/Edge/Application/msedge.exe",
        local / "Microsoft/Edge/Application/msedge.exe",
    ]
    order = edge + chrome if preference.lower() == "edge" else chrome + edge
    if preference.lower() == "chrome":
        order = chrome + edge
    seen: set[str] = set()
    result: list[Path] = []
    for path in order:
        key = str(path).lower()
        if key not in seen:
            seen.add(key)
            result.append(path)
    return result


def find_browser(preference: str = "auto", explicit: str | None = None) -> Path | None:
    if explicit:
        p = Path(explicit).expanduser()
        if p.is_file():
            return p
    for candidate in browser_candidates(preference):
        if candidate.is_file():
            return candidate
    return None


def default_profile_dir() -> Path:
    root = Path(os.environ.get("LOCALAPPDATA", str(Path.home()))) / "WOF Future Danger"
    return root / "BrowserProfile"


def launch_debug_browser(
    executable: Path,
    *,
    host: str = "127.0.0.1",
    port: int = 9223,
    user_data_dir: Path | None = None,
    game_url: str | None = None,
) -> subprocess.Popen[Any]:
    if not is_loopback_host(host):
        raise ValueError("PYLAUNCH only permits loopback CDP endpoints")
    profile = (user_data_dir or default_profile_dir()).resolve()
    profile.mkdir(parents=True, exist_ok=True)
    args = [
        str(executable),
        f"--remote-debugging-address={host}",
        f"--remote-debugging-port={port}",
        f"--user-data-dir={profile}",
        "--no-first-run",
        "--no-default-browser-check",
    ]
    if game_url:
        args.append(game_url)
    return subprocess.Popen(args, close_fds=True)


def wait_for_endpoint(host: str, port: int, timeout: float = 8.0) -> BrowserEndpoint | None:
    if not is_loopback_host(host):
        return None
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        endpoint = probe_endpoint(host, port)
        if endpoint:
            return endpoint
        time.sleep(0.2)
    return None
