from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .browser import probe_endpoint


FLEET_MANIFEST_VERSION = "wof-browser-fleet-v1"


@dataclass(frozen=True)
class FleetInstance:
    instance_id: int
    host: str
    port: int
    browser: str | None
    profile_dir: Path
    pid: int | None
    manager_run_id: str | None
    game_url: str | None

    @property
    def http_base(self) -> str:
        return f"http://{self.host}:{self.port}"


def default_fleet_root() -> Path:
    local = os.environ.get("LOCALAPPDATA")
    root = Path(local) if local else Path.home()
    return root / "WOF Future Danger" / "Fleet"


def default_manifest_path() -> Path:
    return default_fleet_root() / "instances.json"


def load_fleet_manifest(path: Path | str | None = None) -> dict[str, Any]:
    manifest_path = Path(path).expanduser() if path else default_manifest_path()
    try:
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {"version": FLEET_MANIFEST_VERSION, "instances": []}
    if not isinstance(payload, dict) or payload.get("version") != FLEET_MANIFEST_VERSION:
        return {"version": FLEET_MANIFEST_VERSION, "instances": []}
    if not isinstance(payload.get("instances"), list):
        payload["instances"] = []
    return payload


def _coerce_instance(raw: Any) -> FleetInstance | None:
    if not isinstance(raw, dict):
        return None
    try:
        instance_id = int(raw["id"])
        port = int(raw["port"])
        host = str(raw.get("host") or "127.0.0.1")
        profile_dir = Path(str(raw["profileDir"])).expanduser()
    except (KeyError, TypeError, ValueError):
        return None
    pid_raw = raw.get("pid")
    try:
        pid = int(pid_raw) if pid_raw is not None else None
    except (TypeError, ValueError):
        pid = None
    return FleetInstance(
        instance_id=instance_id,
        host=host,
        port=port,
        browser=str(raw.get("browser")) if raw.get("browser") else None,
        profile_dir=profile_dir,
        pid=pid,
        manager_run_id=str(raw.get("managerRunId")) if raw.get("managerRunId") else None,
        game_url=str(raw.get("gameUrl")) if raw.get("gameUrl") else None,
    )


def discover_fleet_instances(
    path: Path | str | None = None,
    *,
    live_only: bool = True,
) -> list[FleetInstance]:
    payload = load_fleet_manifest(path)
    result: list[FleetInstance] = []
    for raw in payload.get("instances", []):
        instance = _coerce_instance(raw)
        if instance is None:
            continue
        if live_only and probe_endpoint(instance.host, instance.port) is None:
            continue
        result.append(instance)
    return sorted(result, key=lambda item: item.instance_id)


def select_fleet_instance(
    path: Path | str | None = None,
    *,
    instance_id: int | None = None,
    live_only: bool = True,
) -> FleetInstance | None:
    instances = discover_fleet_instances(path, live_only=live_only)
    if instance_id is None:
        return instances[0] if instances else None
    return next((item for item in instances if item.instance_id == instance_id), None)
