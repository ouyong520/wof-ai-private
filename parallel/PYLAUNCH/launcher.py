from __future__ import annotations

import argparse
import json
import sys
import threading
import time
from pathlib import Path

from wof_launcher.fleet import select_fleet_instance
from wof_launcher.monitor import LauncherMonitor
from wof_launcher.proof import write_proof_json
from wof_launcher.state import StatusStore
from wof_launcher.tray import TrayApp


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="WOF Future Danger Python Launcher Foundation (READ ONLY)")
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--port", type=int, default=9223)
    p.add_argument("--browser", choices=["auto", "chrome", "edge"], default="auto")
    p.add_argument("--browser-path")
    p.add_argument("--profile-dir")
    p.add_argument("--game-url")
    p.add_argument("--attach-only", action="store_true", help="Do not start a browser; attach only to an existing CDP endpoint")
    p.add_argument("--no-tray", action="store_true", help="CLI diagnostics mode")
    p.add_argument("--once", action="store_true", help="With --no-tray, print one status snapshot and exit")
    p.add_argument("--proof-json", help="Continuously write a compact read-only Windows proof JSON snapshot")
    fleet = p.add_mutually_exclusive_group()
    fleet.add_argument("--fleet-auto", action="store_true", help="Attach to the first live Browser Fleet instance")
    fleet.add_argument("--fleet-instance", type=int, help="Attach to one numbered live Browser Fleet instance")
    p.add_argument("--fleet-manifest", help="Optional Browser Fleet instances.json path")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    if args.fleet_auto or args.fleet_instance is not None:
        selected = select_fleet_instance(
            Path(args.fleet_manifest).expanduser() if args.fleet_manifest else None,
            instance_id=args.fleet_instance,
            live_only=True,
        )
        if selected is None:
            which = f"#{args.fleet_instance}" if args.fleet_instance is not None else "any live instance"
            print(f"Browser Fleet {which} not found; game/browser is unaffected", file=sys.stderr)
            return 3
        args.host = selected.host
        args.port = selected.port
        args.attach_only = True
        if not args.profile_dir:
            args.profile_dir = str(selected.profile_dir)

    status = StatusStore()
    stop = threading.Event()
    tray_holder: dict[str, TrayApp] = {}
    proof_path = Path(args.proof_json).expanduser().resolve() if args.proof_json else None

    def publish_status() -> None:
        if proof_path:
            try:
                write_proof_json(proof_path, status.get().snapshot())
            except OSError:
                # Diagnostics export must never interfere with browser/game attachment.
                pass
        tray = tray_holder.get("tray")
        if tray:
            tray.refresh()

    def request_stop() -> None:
        stop.set()
        monitor.stop()

    monitor = LauncherMonitor(
        status,
        host=args.host,
        port=args.port,
        browser_preference=args.browser,
        browser_path=args.browser_path,
        profile_dir=Path(args.profile_dir).expanduser() if args.profile_dir else None,
        game_url=args.game_url,
        auto_launch_browser=not args.attach_only,
        on_change=publish_status,
    )
    publish_status()
    monitor.start()

    if args.no_tray:
        try:
            last = None
            while not stop.is_set():
                snap = status.get().snapshot()
                encoded = json.dumps(snap, sort_keys=True)
                if encoded != last:
                    print(json.dumps(snap, indent=2, ensure_ascii=False), flush=True)
                    last = encoded
                if args.once and snap["state"] in {"CONNECTED", "WAITING_WOF", "ERROR"}:
                    break
                time.sleep(1)
        except KeyboardInterrupt:
            pass
        finally:
            publish_status()
            request_stop()
        return 0

    try:
        tray = TrayApp(status, reconnect=monitor.reconnect, open_game=monitor.open_game, quit_app=request_stop)
        tray_holder["tray"] = tray
        tray.run()
    except ImportError as exc:
        print(f"Tray dependency missing ({exc}); run pip install -r requirements.txt or use --no-tray", file=sys.stderr)
        publish_status()
        request_stop()
        return 2
    finally:
        publish_status()
        request_stop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
