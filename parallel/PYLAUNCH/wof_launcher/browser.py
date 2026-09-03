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

_SUPPORTED_BROWSER_PRODUCTS = {"chrome", "chromium", "edge", "edg", "microsoft edge"}
_BROWSER_WS_PREFIX = "/devtools/browser/"

@dataclass(frozen=True)
class BrowserEndpoint:
    host: str
    port: int
    browser: str
    websocket_url: str
    @property
    def http_base(self) -> str:
        return f"http://{self.host}:{self.port}"

def _http_json(url: str, timeout: float = 0.8) -> Any:
    request = urllib.request.Request(url, headers={"User-Agent": "WOF-Future-Danger-Launcher/0.1"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))

def is_loopback_host(host: str) -> bool:
    value = str(host or "").strip().lower().rstrip(".")
    if value == "localhost": return True
    try: return ipaddress.ip_address(value).is_loopback
    except ValueError: return False

def browser_metadata_supported(browser: Any) -> bool:
    if not isinstance(browser, str): return False
    value = browser.strip()
    if not value or any(ord(ch) < 0x20 for ch in value): return False
    product, separator, version = value.partition("/")
    if product.strip().casefold() not in _SUPPORTED_BROWSER_PRODUCTS: return False
    if separator and (not version or version != version.strip() or "/" in version or any(ch.isspace() for ch in version)): return False
    return True

def websocket_matches_endpoint(websocket_url: str, host: str, port: int) -> bool:
    if not is_loopback_host(host): return False
    try:
        parsed = urlsplit(websocket_url); ws_host = parsed.hostname; ws_port = parsed.port; configured_port = int(port)
    except (TypeError, ValueError): return False
    if parsed.scheme not in {"ws", "wss"} or not ws_host or ws_port is None: return False
    if parsed.username is not None or parsed.password is not None or parsed.query or parsed.fragment: return False
    if not is_loopback_host(ws_host) or ws_port != configured_port: return False
    if not parsed.path.startswith(_BROWSER_WS_PREFIX): return False
    browser_id = parsed.path[len(_BROWSER_WS_PREFIX):]
    return bool(browser_id) and "/" not in browser_id and not any(ch.isspace() for ch in browser_id)

def probe_endpoint_diagnostic(host: str, port: int) -> tuple[BrowserEndpoint | None, str | None]:
    if not is_loopback_host(host): return None, "启动浏览器校验拒绝：CDP 主机必须是本机 loopback 地址。"
    try: payload = _http_json(f"http://{host}:{port}/json/version")
    except (urllib.error.URLError, OSError): return None, None
    except (ValueError, UnicodeError): return None, "启动浏览器校验拒绝：/json/version 不是有效 JSON。"
    if not isinstance(payload, dict): return None, "启动浏览器校验拒绝：/json/version 必须返回 JSON 对象。"
    browser = payload.get("Browser")
    if not isinstance(browser, str) or not browser.strip(): return None, "启动浏览器校验拒绝：/json/version 缺少有效 Browser 元数据。"
    browser = browser.strip()
    if not browser_metadata_supported(browser): return None, f"启动浏览器校验拒绝：Browser 元数据不是受支持且结构有效的 Chrome/Chromium/Edge 系列：{browser!r}。"
    websocket_url = payload.get("webSocketDebuggerUrl")
    if not isinstance(websocket_url, str) or not websocket_url.strip(): return None, "启动浏览器校验拒绝：/json/version 缺少 browser-level webSocketDebuggerUrl。"
    websocket_url = websocket_url.strip()
    if not websocket_matches_endpoint(websocket_url, host, port): return None, "启动浏览器校验拒绝：webSocketDebuggerUrl 必须是同一 loopback 端口上的 /devtools/browser/<id> 端点。"
    return BrowserEndpoint(host=host, port=int(port), browser=browser, websocket_url=websocket_url), None

def probe_endpoint(host: str, port: int) -> BrowserEndpoint | None:
    endpoint, _ = probe_endpoint_diagnostic(host, port); return endpoint

def browser_candidates(preference: str = "auto") -> list[Path]:
    env = os.environ; local = Path(env.get("LOCALAPPDATA", "")); pf = Path(env.get("PROGRAMFILES", "C:/Program Files")); pfx86 = Path(env.get("PROGRAMFILES(X86)", "C:/Program Files (x86)"))
    chrome = [local / "Google/Chrome/Application/chrome.exe", pf / "Google/Chrome/Application/chrome.exe", pfx86 / "Google/Chrome/Application/chrome.exe"]
    edge = [pf / "Microsoft/Edge/Application/msedge.exe", pfx86 / "Microsoft/Edge/Application/msedge.exe", local / "Microsoft/Edge/Application/msedge.exe"]
    order = edge + chrome if preference.lower() == "edge" else chrome + edge
    if preference.lower() == "chrome": order = chrome + edge
    seen: set[str] = set(); result: list[Path] = []
    for path in order:
        key = str(path).lower()
        if key not in seen: seen.add(key); result.append(path)
    return result

def find_browser(preference: str = "auto", explicit: str | None = None) -> Path | None:
    if os.environ.get("WOF_ALPHA_MENU6_ATTACH_ONLY") == "1":
        return None
    if explicit:
        p = Path(explicit).expanduser()
        if p.is_file(): return p
    for candidate in browser_candidates(preference):
        if candidate.is_file(): return candidate
    return None

def default_profile_dir() -> Path:
    root = Path(os.environ.get("LOCALAPPDATA", str(Path.home()))) / "WOF Future Danger"
    return root / "BrowserProfile"

def known_owner_game_url(explicit: str | None = None) -> tuple[str | None, str | None]:
    """Return only an explicitly supplied Owner URL; never mine persisted launch state.

    WOF_GAME_URL, Fleet settings and browser profile history are deliberately not
    navigation authorities. Menu 6 is attach/reuse-only and must never resurrect
    a stale ROM destination from previous sessions.
    """
    value = str(explicit or "").strip()
    if not value:
        return None, None
    try:
        parsed = urlsplit(value)
    except ValueError:
        return None, None
    if parsed.scheme in {"http", "https"} and parsed.netloc:
        return value, "explicit"
    return None, None

def launch_debug_browser(executable: Path, *, host: str = "127.0.0.1", port: int = 9223, user_data_dir: Path | None = None, game_url: str | None = None, restore_last_session: bool = False) -> subprocess.Popen[Any]:
    if os.environ.get("WOF_ALPHA_MENU6_ATTACH_ONLY") == "1":
        raise RuntimeError("menu 6 is attach/reuse-only and cannot launch or restore a browser")
    if not is_loopback_host(host): raise ValueError("PYLAUNCH only permits loopback CDP endpoints")
    profile = (user_data_dir or default_profile_dir()).resolve(); profile.mkdir(parents=True, exist_ok=True)
    args = [str(executable), f"--remote-debugging-address={host}", f"--remote-debugging-port={port}", f"--user-data-dir={profile}", "--no-first-run", "--no-default-browser-check"]
    if game_url:
        args.append(game_url)
    elif restore_last_session:
        args.extend(["--restore-last-session", "--disable-session-crashed-bubble"])
    return subprocess.Popen(args, close_fds=True)

def wait_for_endpoint_diagnostic(host: str, port: int, timeout: float = 8.0) -> tuple[BrowserEndpoint | None, str | None]:
    if not is_loopback_host(host): return None, "启动浏览器校验拒绝：CDP 主机必须是本机 loopback 地址。"
    deadline = time.monotonic() + timeout; last_rejection: str | None = None
    while time.monotonic() < deadline:
        endpoint, rejection = probe_endpoint_diagnostic(host, port)
        if endpoint: return endpoint, None
        if rejection: last_rejection = rejection
        time.sleep(0.2)
    return None, last_rejection

def wait_for_endpoint(host: str, port: int, timeout: float = 8.0) -> BrowserEndpoint | None:
    endpoint, _ = wait_for_endpoint_diagnostic(host, port, timeout); return endpoint
