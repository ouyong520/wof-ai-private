from __future__ import annotations

import argparse
import json
import os
import threading
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import recorder


FLEET_MANIFEST_VERSION = "wof-browser-fleet-v1"
SUPERVISOR_SCHEMA = "wof-052l-fleet-supervisor-v1"


def utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def default_fleet_manifest() -> Path:
    local = os.environ.get("LOCALAPPDATA")
    root = Path(local) if local else Path.home()
    return root / "WOF Future Danger" / "Fleet" / "instances.json"


@dataclass(frozen=True)
class FleetEndpoint:
    instance_id: int
    host: str
    port: int
    profile_dir: str | None = None

    @property
    def key(self) -> tuple[int, str, int]:
        return self.instance_id, self.host, self.port


def load_fleet_entries(path: Path) -> list[FleetEndpoint]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return []
    if not isinstance(payload, dict) or payload.get("version") != FLEET_MANIFEST_VERSION:
        return []
    rows = payload.get("instances")
    if not isinstance(rows, list):
        return []
    result: list[FleetEndpoint] = []
    for raw in rows:
        if not isinstance(raw, dict):
            continue
        try:
            instance_id = int(raw["id"])
            host = str(raw.get("host") or "127.0.0.1")
            port = int(raw["port"])
        except (KeyError, TypeError, ValueError):
            continue
        # Browser Fleet is localhost-only by contract.
        if host not in {"127.0.0.1", "localhost"}:
            continue
        result.append(
            FleetEndpoint(
                instance_id=instance_id,
                host=host,
                port=port,
                profile_dir=str(raw.get("profileDir")) if raw.get("profileDir") else None,
            )
        )
    return sorted(result, key=lambda item: item.instance_id)


class FleetRecorderManager(recorder.RecorderManager):
    """One strict recorder per Browser Fleet CDP endpoint."""

    def __init__(
        self,
        output_dir: Path,
        args: argparse.Namespace,
        *,
        stop_event: threading.Event,
        fleet_instance_id: int,
    ) -> None:
        super().__init__(output_dir, args)
        self.stop_event = stop_event
        self.fleet_instance_id = fleet_instance_id
        self._strict_wait_announced = False

    def ensure_browser(self) -> bool:
        if self.client and not self.client.closed:
            return True
        if self.client:
            self._browser_lost()

        endpoint = recorder.probe_endpoint(self.args.cdp_host, int(self.args.cdp_port))
        if not endpoint:
            if not self._strict_wait_announced:
                print(
                    f"\nFleet #{self.fleet_instance_id}: WAITING "
                    f"{self.args.cdp_host}:{self.args.cdp_port}; other rooms continue."
                )
                self._strict_wait_announced = True
            return False

        client: recorder.CdpClient | None = None
        try:
            client = recorder.CdpClient(endpoint.websocket_url)
            client.connect()
            client.targets()
        except Exception as exc:
            print(f"\nFleet #{self.fleet_instance_id}: CDP connect failed safely: {exc}")
            if client:
                client.close()
            return False

        self.endpoint = endpoint
        self.client = client
        self._announced_wait = False
        self._strict_wait_announced = False
        print(f"\nFleet #{self.fleet_instance_id}: Browser OK — {endpoint.label}")
        return True

    def run_managed(self) -> None:
        print(
            f"\nWOF-052L fleet recorder #{self.fleet_instance_id} "
            f"-> {self.args.cdp_host}:{self.args.cdp_port}"
        )
        self.write_merged(False)
        try:
            while not self.stop_event.is_set():
                now = time.monotonic()
                if self.ensure_browser():
                    self.discover(now)
                    self.poll_rooms(now)
                if now - self._last_merge >= recorder.ROLLING_MERGE_INTERVAL:
                    self.write_merged(False)
                self.stop_event.wait(0.15)
        finally:
            self.shutdown()


@dataclass
class ChildRecorder:
    endpoint: FleetEndpoint
    manager: FleetRecorderManager
    stop_event: threading.Event
    thread: threading.Thread


class FleetSupervisor:
    def __init__(
        self,
        output_dir: Path,
        base_args: argparse.Namespace,
        manifest_path: Path,
    ) -> None:
        self.output_dir = output_dir
        self.base_args = base_args
        self.manifest_path = manifest_path
        self.started_at = utc_iso()
        self.run_id = f"fleet-{recorder.local_stamp()}"
        self.children: dict[tuple[int, str, int], ChildRecorder] = {}
        self._stop = threading.Event()

    def _child_args(self, endpoint: FleetEndpoint) -> argparse.Namespace:
        values = vars(self.base_args).copy()
        values["cdp_host"] = endpoint.host
        values["cdp_port"] = endpoint.port
        values["no_launch_browser"] = True
        values["game_url"] = None
        return argparse.Namespace(**values)

    def start_endpoint(self, endpoint: FleetEndpoint) -> None:
        if endpoint.key in self.children:
            return
        stop_event = threading.Event()
        manager = FleetRecorderManager(
            self.output_dir,
            self._child_args(endpoint),
            stop_event=stop_event,
            fleet_instance_id=endpoint.instance_id,
        )
        thread = threading.Thread(
            target=manager.run_managed,
            name=f"wof052l-fleet-{endpoint.instance_id}",
            daemon=True,
        )
        self.children[endpoint.key] = ChildRecorder(endpoint, manager, stop_event, thread)
        thread.start()

    def sync_manifest(self) -> list[FleetEndpoint]:
        entries = load_fleet_entries(self.manifest_path)
        for endpoint in entries:
            self.start_endpoint(endpoint)
        return entries

    def merged_index(self) -> dict[str, Any]:
        child_runs: list[dict[str, Any]] = []
        totals: dict[str, int] = {}
        rooms: list[dict[str, Any]] = []
        candidate_evidence: list[dict[str, Any]] = []
        for child in sorted(self.children.values(), key=lambda item: item.endpoint.instance_id):
            run_file = child.manager.run_file
            payload: dict[str, Any] | None = None
            try:
                loaded = json.loads(run_file.read_text(encoding="utf-8"))
                payload = loaded if isinstance(loaded, dict) else None
            except (OSError, ValueError):
                pass
            row: dict[str, Any] = {
                "fleetInstanceId": child.endpoint.instance_id,
                "host": child.endpoint.host,
                "port": child.endpoint.port,
                "runFile": str(run_file),
            }
            if payload:
                row["runId"] = payload.get("runId")
                row["status"] = payload.get("status")
                counts = payload.get("counts")
                if isinstance(counts, dict):
                    for key, value in counts.items():
                        if isinstance(value, int):
                            totals[key] = totals.get(key, 0) + value
                child_rooms = payload.get("rooms")
                if isinstance(child_rooms, list):
                    for item in child_rooms:
                        if isinstance(item, dict):
                            rooms.append({"fleetInstanceId": child.endpoint.instance_id, **item})
                evidence = payload.get("t18CandidateEvidence")
                if isinstance(evidence, list):
                    for item in evidence:
                        if len(candidate_evidence) >= 5000:
                            break
                        if isinstance(item, dict):
                            candidate_evidence.append(
                                {"fleetInstanceId": child.endpoint.instance_id, **item}
                            )
            child_runs.append(row)

        return {
            "schema": SUPERVISOR_SCHEMA,
            "runId": self.run_id,
            "status": "complete",
            "startedAt": self.started_at,
            "finalizedAt": utc_iso(),
            "fleetManifest": str(self.manifest_path),
            "safety": {
                "readOnly": True,
                "ramWrites": 0,
                "inputInjection": False,
                "windowWorkerReplacement": False,
            },
            "counts": totals,
            "t18CandidateSequenceSummary": recorder.t18_sequence_summary(candidate_evidence),
            "t18CandidateEvidence": candidate_evidence,
            "rooms": rooms,
            "childRuns": child_runs,
            "notes": {
                "isolation": "Each Browser Fleet CDP endpoint has an independent RecorderManager.",
                "t23": "Full T23 detail remains in each child merged run; fleet index preserves child run paths.",
            },
        }

    def write_final_index(self) -> Path:
        path = self.output_dir / "runs" / f"{recorder.safe_name(self.run_id)}_merged.json"
        recorder.atomic_write_json(path, self.merged_index())
        return path

    def stop_all(self) -> None:
        self._stop.set()
        for child in self.children.values():
            child.stop_event.set()
        for child in self.children.values():
            child.thread.join(timeout=15.0)

    def run(self) -> int:
        print("WOF-052L Browser Fleet supervisor")
        print(f"Fleet manifest: {self.manifest_path}")
        print(f"Save folder: {self.output_dir}")
        print("Safety: READ ONLY / RAM writes 0 / no input injection / no window.Worker replacement")
        print("Press Ctrl+C to stop all recorder workers and finalize JSON.\n")
        try:
            while not self._stop.is_set():
                entries = self.sync_manifest()
                live_threads = sum(1 for child in self.children.values() if child.thread.is_alive())
                print(
                    f"\rFleet entries {len(entries)} | Recorder workers {live_threads} | "
                    f"READ ONLY / RAM writes 0".ljust(120),
                    end="",
                    flush=True,
                )
                self._stop.wait(1.0)
        except KeyboardInterrupt:
            print("\nStopping fleet recorder...")
        finally:
            self.stop_all()
            final_path = self.write_final_index()
            print(f"\nFleet merged JSON: {final_path}")
        return 0


def build_parser() -> argparse.ArgumentParser:
    parser = recorder.build_parser()
    parser.add_argument(
        "--fleet-manifest",
        help="Optional Browser Fleet instances.json path (default: WOF Future Danger Fleet manifest)",
    )
    parser.add_argument(
        "--ignore-browser-fleet",
        action="store_true",
        help="Force the original single-CDP recorder behavior even if a Fleet manifest exists",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.self_test:
        return recorder.run_self_test()

    output_dir = recorder.resolve_output_dir(args.output_dir, args.reset_output)
    manifest_path = (
        Path(args.fleet_manifest).expanduser().resolve()
        if args.fleet_manifest
        else default_fleet_manifest()
    )
    entries = [] if args.ignore_browser_fleet else load_fleet_entries(manifest_path)
    if not entries:
        print("Browser Fleet manifest has no entries; using original WOF-052L single-CDP mode.")
        recorder.RecorderManager(output_dir, args).run()
        return 0

    supervisor = FleetSupervisor(output_dir, args, manifest_path)
    for endpoint in entries:
        supervisor.start_endpoint(endpoint)
    return supervisor.run()


if __name__ == "__main__":
    raise SystemExit(main())
