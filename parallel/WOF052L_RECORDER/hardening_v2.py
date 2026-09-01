from __future__ import annotations

import ipaddress
import re
import time
from typing import Any
from urllib.parse import urlsplit


WORKER_TYPES = {"worker", "shared_worker", "service_worker"}
CROSS_PAGE_AMBIGUITY = "cross-page-worker-association-ambiguous"


def _host_text(host: Any) -> str:
    return str(host or "").strip().lower().strip("[]")


def is_loopback_host(host: Any) -> bool:
    text = _host_text(host)
    if text == "localhost":
        return True
    if not text:
        return False
    try:
        return ipaddress.ip_address(text.split("%", 1)[0]).is_loopback
    except ValueError:
        return False


def validate_endpoint_websocket(request_host: Any, request_port: Any, websocket_url: Any) -> tuple[bool, str]:
    if not is_loopback_host(request_host):
        return False, "remote-cdp-host-rejected"
    try:
        expected_port = int(request_port)
    except (TypeError, ValueError):
        return False, "invalid-cdp-port"
    if not isinstance(websocket_url, str) or not websocket_url:
        return False, "missing-browser-websocket"
    try:
        parsed = urlsplit(websocket_url)
        ws_port = parsed.port
    except ValueError:
        return False, "malformed-browser-websocket"
    if parsed.scheme not in {"ws", "wss"}:
        return False, "invalid-browser-websocket-scheme"
    if not is_loopback_host(parsed.hostname):
        return False, "returned-websocket-remote-host"
    if ws_port != expected_port:
        return False, "returned-websocket-cross-port"
    return True, "ok"


def worker_compatible(target: dict[str, Any], *, related: bool) -> bool:
    """Existing attachable Worker URL shape is a hint only; runtime+identity are authority."""
    if target.get("type") in WORKER_TYPES:
        return True
    return related and bool(re.search(r"gstyphoon", str(target.get("url") or ""), re.I))


def page_for_direct(worker: dict[str, Any], pages: list[dict[str, Any]]) -> dict[str, Any] | None:
    """Never use Worker openerId as parent authority."""
    parent_id = worker.get("parentId")
    if parent_id:
        linked = [page for page in pages if page.get("targetId") == parent_id]
        if len(linked) == 1:
            return linked[0]

    parent_frame_id = worker.get("parentFrameId")
    if parent_frame_id:
        linked = [
            page
            for page in pages
            if page.get("frameId") == parent_frame_id or page.get("targetId") == parent_frame_id
        ]
        if len(linked) == 1:
            return linked[0]

    # Compatibility fallback is intentionally stricter than openerId guessing.
    # Exact World identity still gates the Worker itself; association is allowed
    # only when the endpoint contains one unique page.
    if len(pages) == 1:
        return pages[0]
    return None


def _candidate_worker_id(candidate: Any) -> str:
    target = getattr(candidate, "target", None)
    return str(target.get("targetId") or "") if isinstance(target, dict) else ""


def _candidate_page_id(candidate: Any) -> str:
    page = getattr(candidate, "page", None)
    return str(page.get("targetId") or "") if isinstance(page, dict) else ""


def _live_relations(manager: Any) -> dict[str, set[str]]:
    relations: dict[str, set[str]] = {}
    for target_id, room in list(getattr(manager, "live", {}).items()):
        page = getattr(room, "page", None)
        page_id = str(page.get("targetId") or "") if isinstance(page, dict) else ""
        worker_id = str(target_id or "")
        if worker_id and page_id:
            relations.setdefault(worker_id, set()).add(page_id)
    return relations


def filter_cross_page_ambiguity(
    manager: Any,
    candidates: list[Any],
    diagnostics: dict[str, Any],
) -> tuple[list[Any], dict[str, Any]]:
    relations = _live_relations(manager)
    for candidate in candidates:
        worker_id = _candidate_worker_id(candidate)
        page_id = _candidate_page_id(candidate)
        if worker_id and page_id:
            relations.setdefault(worker_id, set()).add(page_id)

    ambiguous = {
        worker_id: sorted(page_ids)
        for worker_id, page_ids in relations.items()
        if len(page_ids) > 1
    }
    if not ambiguous:
        diagnostics["crossPageWorkerAmbiguities"] = []
        diagnostics["crossPageAmbiguityCount"] = 0
        diagnostics["candidateCount"] = len(candidates)
        return candidates, diagnostics

    rejected_worker_ids = set(ambiguous)
    admitted: list[Any] = []
    for candidate in candidates:
        if _candidate_worker_id(candidate) in rejected_worker_ids:
            try:
                candidate.close()
            except Exception:
                pass
        else:
            admitted.append(candidate)

    rows = [
        {
            "status": CROSS_PAGE_AMBIGUITY,
            "workerTargetId": worker_id,
            "pageTargetIds": page_ids,
            "pageCount": len(page_ids),
        }
        for worker_id, page_ids in sorted(ambiguous.items())
    ]
    diagnostics["crossPageWorkerAmbiguities"] = rows
    diagnostics["crossPageAmbiguityCount"] = len(rows)
    diagnostics["candidateCount"] = len(admitted)

    affected_pages = {page_id for page_ids in ambiguous.values() for page_id in page_ids}
    for row in diagnostics.get("relatedPages", []):
        if not isinstance(row, dict):
            continue
        page = row.get("page")
        page_id = str(page.get("targetId") or "") if isinstance(page, dict) else ""
        if page_id in affected_pages:
            row["ambiguous"] = True
            row["ambiguityReason"] = CROSS_PAGE_AMBIGUITY

    return admitted, diagnostics


def cross_page_ambiguous_pages(topology: dict[str, Any]) -> set[str]:
    result: set[str] = set()
    for row in topology.get("crossPageWorkerAmbiguities", []):
        if not isinstance(row, dict) or row.get("status") != CROSS_PAGE_AMBIGUITY:
            continue
        for page_id in row.get("pageTargetIds", []):
            if page_id:
                result.add(str(page_id))
    return result


def finalize_cross_page_ambiguous_live(manager: Any, topology: dict[str, Any]) -> list[str]:
    affected = cross_page_ambiguous_pages(topology)
    finalized: list[str] = []
    if not affected:
        return finalized
    for target_id, room in list(getattr(manager, "live", {}).items()):
        page = getattr(room, "page", None)
        page_id = str(page.get("targetId") or "") if isinstance(page, dict) else ""
        if page_id in affected:
            manager._finalize_target(target_id, CROSS_PAGE_AMBIGUITY, try_remote=False)
            finalized.append(str(target_id))
    return finalized


def _endpoint_rejection(recorder_module: Any, host: Any, port: Any, reason: str) -> None:
    recorder_module._WOF052L_LAST_ENDPOINT_REJECTION = {
        "host": str(host or ""),
        "port": port,
        "reason": reason,
        "readOnly": True,
        "ramWrites": 0,
        "inputInjection": False,
    }


def _install_endpoint_guard(recorder_module: Any) -> None:
    if getattr(recorder_module, "_WOF052L_ENDPOINT_GUARD_V2_INSTALLED", False):
        return

    original_launch = recorder_module.launch_debug_browser

    def probe_endpoint(host: str, port: int):
        if not is_loopback_host(host):
            _endpoint_rejection(recorder_module, host, port, "remote-cdp-host-rejected")
            return None
        data = recorder_module.http_json(f"http://{host}:{port}/json/version")
        if not data:
            _endpoint_rejection(recorder_module, host, port, "endpoint-not-ready")
            return None
        ws = data.get("webSocketDebuggerUrl")
        ok, reason = validate_endpoint_websocket(host, port, ws)
        if not ok:
            _endpoint_rejection(recorder_module, host, port, reason)
            return None
        recorder_module._WOF052L_LAST_ENDPOINT_REJECTION = None
        return recorder_module.BrowserEndpoint(
            host,
            int(port),
            str(data.get("Browser") or "Chromium"),
            str(ws),
        )

    def launch_debug_browser(preference: str, host: str, port: int, game_url: str | None):
        if not is_loopback_host(host):
            _endpoint_rejection(recorder_module, host, port, "remote-cdp-host-rejected")
            return None
        return original_launch(preference, host, port, game_url)

    recorder_module.probe_endpoint = probe_endpoint
    recorder_module.launch_debug_browser = launch_debug_browser
    recorder_module._WOF052L_ENDPOINT_GUARD_V2_INSTALLED = True


def _install_recorder_owner_ux(recorder_module: Any) -> None:
    manager_cls = recorder_module.RecorderManager
    if getattr(manager_cls, "_WOF052L_HARDENED_OWNER_UX", False):
        return

    def ensure_browser(self: Any) -> bool:
        if self.client and not self.client.closed:
            return True
        if self.client:
            self._browser_lost()

        if not is_loopback_host(self.args.cdp_host):
            if not self._announced_wait:
                print("\n浏览器 CDP 主机不是本机 loopback；已安全拒绝连接，游戏本身不受影响。")
                print(f"技术详情：remote-cdp-host-rejected host={self.args.cdp_host}")
                self._announced_wait = True
            return False

        endpoint = recorder_module.find_endpoint(self.args.cdp_host, self.args.cdp_port)
        if self.browser_process is not None and self.browser_process.poll() is not None:
            self.browser_process = None
        if not endpoint and not self.args.no_launch_browser and self.browser_process is None:
            port = self.args.cdp_port or 9223
            proc = recorder_module.launch_debug_browser(
                self.args.browser,
                self.args.cdp_host,
                port,
                self.args.game_url,
            )
            if proc:
                self.browser_process = proc
                print(f"\n已启动可连接的浏览器：{self.args.cdp_host}:{port}。请正常打开 WOF 房间。")
                deadline = time.monotonic() + 8.0
                while time.monotonic() < deadline and not endpoint:
                    endpoint = recorder_module.probe_endpoint(self.args.cdp_host, port)
                    if not endpoint:
                        time.sleep(0.2)
        if not endpoint:
            if not self._announced_wait:
                print("\n浏览器：等待本机 Chrome/Edge CDP。采集器会自动重试，游戏本身不受影响。")
                rejection = getattr(recorder_module, "_WOF052L_LAST_ENDPOINT_REJECTION", None)
                if isinstance(rejection, dict) and rejection.get("reason") not in {None, "endpoint-not-ready"}:
                    print(f"技术详情：{rejection.get('reason')}")
                self._announced_wait = True
            return False

        client = None
        try:
            client = recorder_module.CdpClient(endpoint.websocket_url)
            client.connect()
            client.targets()
        except Exception as exc:
            print("\n暂时无法连接浏览器 CDP；采集器会继续重试，游戏本身不受影响。")
            print(f"技术详情：{exc}")
            if client:
                client.close()
            return False

        self.endpoint = endpoint
        self.client = client
        self._announced_wait = False
        print(f"\n浏览器：已连接 — {endpoint.label}")
        return True

    def finalize_target(self: Any, target_id: str, reason: str, try_remote: bool) -> None:
        room = self.live.pop(target_id, None)
        if not room:
            return
        data = room.finalize(reason, try_remote=try_remote)
        self.completed.append(data)
        self.room_files.append(
            {
                "roomId": room.room_id,
                "file": str(room.final_file.relative_to(self.output_dir)) if room.final_file else None,
                "reason": reason,
                "startedAt": data["startedAt"],
                "finalizedAt": data["finalizedAt"],
            }
        )
        diag = data.get("diagnostics") or {}
        candidate_cycles = ((diag.get("t18") or {}).get("candidateCycles") or 0)
        print(f"\n- 房间 {room.room_id} 已完成｜原因代码：{reason}｜T18 候选周期：{candidate_cycles}")

    def shutdown(self: Any) -> None:
        for target_id in list(self.live):
            self._finalize_target(target_id, "recorder-stopped", try_remote=True)
        self.write_merged(final=True)
        if self.client:
            self.client.close()
        print(f"\n最终合并 JSON 已保存：{self.run_file}")

    manager_cls.ensure_browser = ensure_browser
    manager_cls._finalize_target = finalize_target
    manager_cls.shutdown = shutdown
    manager_cls._WOF052L_HARDENED_OWNER_UX = True


def _install_discovery_hardening(recorder_module: Any, discovery_module: Any) -> None:
    if getattr(discovery_module, "_WOF052L_DISCOVERY_V2_HARDENING_INSTALLED", False):
        return

    discovery_module._worker_compatible = worker_compatible
    discovery_module._page_for_direct = page_for_direct
    original_discover_candidates = discovery_module.discover_candidates

    def discover_candidates(manager: Any, targets: list[dict[str, Any]], *, skip_page_ids=None):
        candidates, diagnostics = original_discover_candidates(
            manager,
            targets,
            skip_page_ids=skip_page_ids,
        )
        return filter_cross_page_ambiguity(manager, candidates, diagnostics)

    def discover(self: Any, now: float) -> None:
        if not self.client or now - self._last_discovery < recorder_module.DISCOVERY_INTERVAL:
            return
        self._last_discovery = now
        try:
            targets = self.client.targets()
        except Exception:
            self._browser_lost()
            return

        current_ids = {str(target.get("targetId")) for target in targets if target.get("targetId")}
        page_ids = {
            str(target.get("targetId"))
            for target in targets
            if target.get("type") == "page" and target.get("targetId")
        }
        for target_id, room in list(self.live.items()):
            path = str(room.target.get("discoveryPath") or "direct-worker") if isinstance(room.target, dict) else "direct-worker"
            page_id = str(room.page.get("targetId") or "") if room.page else ""
            if path == "direct-worker" and target_id not in current_ids:
                self._finalize_target(target_id, "worker-closed-or-reloaded", try_remote=False)
            elif path == "page-autoattach" and page_id and page_id not in page_ids:
                self._finalize_target(target_id, "page-closed-or-reloaded", try_remote=False)

        live_page_ids = {
            str(room.page.get("targetId") or "")
            for room in self.live.values()
            if room.page and room.page.get("targetId")
        }
        audit_live = now - self._wof052l_last_live_topology_audit >= 10.0
        if audit_live:
            self._wof052l_last_live_topology_audit = now

        candidates, topology = discovery_module.discover_candidates(
            self,
            targets,
            skip_page_ids=set() if audit_live else live_page_ids,
        )
        self._wof052l_last_topology = topology

        cross_pages = cross_page_ambiguous_pages(topology)
        if cross_pages:
            finalized = finalize_cross_page_ambiguous_live(self, topology)
            if finalized:
                discovery_module._announce(
                    self,
                    "\n检测到同一个 exact Worker 同时关联多个页面；受影响房间已先完成并停止继续收证据。"
                    f"\n技术详情：{CROSS_PAGE_AMBIGUITY}",
                )

        local_ambiguous_pages = {
            str((row.get("page") or {}).get("targetId") or "")
            for row in topology.get("relatedPages", [])
            if isinstance(row, dict)
            and row.get("ambiguous") is True
            and row.get("ambiguityReason") != CROSS_PAGE_AMBIGUITY
        }
        local_ambiguous_pages.update(
            str(row.get("pageTargetId") or "")
            for row in topology.get("directWorkers", [])
            if isinstance(row, dict) and row.get("status") == "ambiguous-supported-workers"
        )
        if local_ambiguous_pages:
            for target_id, room in list(self.live.items()):
                page_id = str(room.page.get("targetId") or "") if room.page else ""
                if page_id in local_ambiguous_pages:
                    self._finalize_target(target_id, "worker-association-ambiguous", try_remote=False)

        if not candidates:
            if cross_pages:
                discovery_module._announce(
                    self,
                    "\n发现跨页面共享 Worker 归属歧义；为避免跨房间串采，当前已安全拒绝准入。"
                    f"\n技术详情：{CROSS_PAGE_AMBIGUITY}",
                )
            else:
                discovery_module._announce(self, discovery_module._discovery_status(topology))
            return

        for candidate in candidates:
            discovery_module._attach_candidate(self, candidate, now, topology)

    discovery_module.discover_candidates = discover_candidates
    recorder_module.RecorderManager.discover = discover
    discovery_module._WOF052L_DISCOVERY_V2_HARDENING_INSTALLED = True
    recorder_module._WOF052L_DISCOVERY_V2_HARDENING_INSTALLED = True


def _install_fleet_owner_ux(recorder_module: Any) -> None:
    try:
        import fleet_recorder
    except Exception:
        return
    if getattr(fleet_recorder, "_WOF052L_FLEET_HARDENING_INSTALLED", False):
        return

    def ensure_browser(self: Any) -> bool:
        if self.client and not self.client.closed:
            return True
        if self.client:
            self._browser_lost()

        endpoint = recorder_module.probe_endpoint(self.args.cdp_host, int(self.args.cdp_port))
        if not endpoint:
            if not self._strict_wait_announced:
                print(
                    f"\n集群房间 #{self.fleet_instance_id}：等待本机浏览器 "
                    f"{self.args.cdp_host}:{self.args.cdp_port}；其他房间继续运行。"
                )
                rejection = getattr(recorder_module, "_WOF052L_LAST_ENDPOINT_REJECTION", None)
                if isinstance(rejection, dict) and rejection.get("reason") not in {None, "endpoint-not-ready"}:
                    print(f"技术详情：{rejection.get('reason')}")
                self._strict_wait_announced = True
            return False

        client = None
        try:
            client = recorder_module.CdpClient(endpoint.websocket_url)
            client.connect()
            client.targets()
        except Exception as exc:
            print(f"\n集群房间 #{self.fleet_instance_id}：浏览器 CDP 连接失败；其他房间继续运行。")
            print(f"技术详情：{exc}")
            if client:
                client.close()
            return False

        self.endpoint = endpoint
        self.client = client
        self._announced_wait = False
        self._strict_wait_announced = False
        print(f"\n集群房间 #{self.fleet_instance_id}：浏览器已连接 — {endpoint.label}")
        return True

    def run_managed(self: Any) -> None:
        print(
            f"\nWOF-052L 集群采集房间 #{self.fleet_instance_id} 已启动 -> "
            f"{self.args.cdp_host}:{self.args.cdp_port}"
        )
        self.write_merged(False)
        try:
            while not self.stop_event.is_set():
                now = time.monotonic()
                if self.ensure_browser():
                    self.discover(now)
                    self.poll_rooms(now)
                if now - self._last_merge >= recorder_module.ROLLING_MERGE_INTERVAL:
                    self.write_merged(False)
                self.stop_event.wait(0.15)
        finally:
            self.shutdown()

    def supervisor_run(self: Any) -> int:
        print("WOF-052L 多房间浏览器采集管理器")
        print(f"浏览器集群状态文件：{self.manifest_path}")
        print(f"保存目录：{self.output_dir}")
        print("安全状态：只读模式开启 / 游戏内存写入 0 / 无游戏输入注入 / 不替换 window.Worker")
        print("按 Ctrl+C 停止全部采集房间，并完成最终 JSON。\n")
        try:
            while not self._stop.is_set():
                entries = self.sync_manifest()
                live_threads = sum(1 for child in self.children.values() if child.thread.is_alive())
                print(
                    f"\r集群房间 {len(entries)} | 采集进程 {live_threads} | "
                    f"只读模式 开启 / 游戏内存写入 0".ljust(120),
                    end="",
                    flush=True,
                )
                self._stop.wait(1.0)
        except KeyboardInterrupt:
            print("\n正在停止多房间采集器……")
        finally:
            self.stop_all()
            final_path = self.write_final_index()
            print(f"\n多房间合并 JSON 已保存：{final_path}")
        return 0

    fleet_recorder.FleetRecorderManager.ensure_browser = ensure_browser
    fleet_recorder.FleetRecorderManager.run_managed = run_managed
    fleet_recorder.FleetSupervisor.run = supervisor_run
    fleet_recorder._WOF052L_FLEET_HARDENING_INSTALLED = True


def install(recorder_module: Any, discovery_module: Any) -> None:
    """Install repository-side Discovery V2 hardening after discovery_v2_sync.install()."""
    if getattr(recorder_module, "_WOF052L_HARDENING_V2_INSTALLED", False):
        return
    _install_endpoint_guard(recorder_module)
    _install_recorder_owner_ux(recorder_module)
    _install_discovery_hardening(recorder_module, discovery_module)
    _install_fleet_owner_ux(recorder_module)
    recorder_module._WOF052L_HARDENING_V2_INSTALLED = True
