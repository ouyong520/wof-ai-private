from __future__ import annotations

import argparse
import inspect
import io
import json
import tempfile
import types
import unittest
from contextlib import redirect_stdout
from dataclasses import dataclass
from pathlib import Path

import discovery_v2_sync as discovery
import fleet_recorder
import hardening_v2 as hardening
import recorder
import test_discovery_v2_sync as base_discovery_tests


WORLD = "5c369ce2de4f53d8cef87eca5623a1f0d39a779e885532d6f185b81357878f62"

discovery.AUTOATTACH_WINDOW_SECONDS = min(discovery.AUTOATTACH_WINDOW_SECONDS, 0.01)
discovery.install(recorder)
hardening.install(recorder, discovery)


class FleetRecorderManifestTests(unittest.TestCase):
    def test_loads_sorted_localhost_fleet_entries(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "instances.json"
            path.write_text(
                json.dumps(
                    {
                        "version": fleet_recorder.FLEET_MANIFEST_VERSION,
                        "instances": [
                            {"id": 10, "host": "127.0.0.1", "port": 9332, "profileDir": "P10"},
                            {"id": 1, "host": "127.0.0.1", "port": 9323, "profileDir": "P01"},
                            {"id": 99, "host": "192.0.2.1", "port": 9999, "profileDir": "unsafe"},
                        ],
                    }
                ),
                encoding="utf-8",
            )
            entries = fleet_recorder.load_fleet_entries(path)
            self.assertEqual([item.instance_id for item in entries], [1, 10])
            self.assertEqual([item.port for item in entries], [9323, 9332])
            self.assertTrue(all(item.host == "127.0.0.1" for item in entries))

    def test_wrong_or_missing_manifest_is_fail_open_empty(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "instances.json"
            self.assertEqual(fleet_recorder.load_fleet_entries(path), [])
            path.write_text(json.dumps({"version": "wrong", "instances": []}), encoding="utf-8")
            self.assertEqual(fleet_recorder.load_fleet_entries(path), [])


@dataclass(frozen=True)
class FakeBrowserEndpoint:
    host: str
    port: int
    browser: str
    websocket_url: str


class EndpointGuardTests(unittest.TestCase):
    def _fake_recorder(self, http_json, candidate_ports=None):
        launched: list[tuple] = []
        fake = types.SimpleNamespace(
            http_json=http_json,
            BrowserEndpoint=FakeBrowserEndpoint,
            candidate_ports=candidate_ports or (lambda explicit: [9223, 9224]),
            launch_debug_browser=lambda *args: launched.append(args),
        )
        hardening._install_endpoint_guard(fake)
        return fake, launched

    def test_loopback_aliases_and_remote_host_rejection(self) -> None:
        self.assertTrue(hardening.is_loopback_host("127.0.0.1"))
        self.assertTrue(hardening.is_loopback_host("localhost"))
        self.assertTrue(hardening.is_loopback_host("::1"))
        self.assertFalse(hardening.is_loopback_host("192.0.2.10"))
        self.assertEqual(
            hardening.validate_endpoint_websocket(
                "192.0.2.10", 9223, "ws://127.0.0.1:9223/devtools/browser/x"
            )[1],
            "remote-cdp-host-rejected",
        )

    def test_returned_websocket_requires_loopback_and_same_port(self) -> None:
        self.assertEqual(
            hardening.validate_endpoint_websocket(
                "127.0.0.1", 9223, "ws://localhost:9223/devtools/browser/x"
            ),
            (True, "ok"),
        )
        self.assertEqual(
            hardening.validate_endpoint_websocket(
                "localhost", 9223, "ws://127.0.0.1:9224/devtools/browser/x"
            )[1],
            "returned-websocket-cross-port",
        )
        self.assertEqual(
            hardening.validate_endpoint_websocket(
                "127.0.0.1", 9223, "ws://192.0.2.1:9223/devtools/browser/x"
            )[1],
            "returned-websocket-remote-host",
        )

    def test_explicit_port_never_falls_over_to_another_common_port(self) -> None:
        calls: list[int] = []

        def http_json(url: str):
            port = int(url.split(":")[-1].split("/")[0])
            calls.append(port)
            if port == 9223:
                return {
                    "Browser": "Chromium",
                    "webSocketDebuggerUrl": "ws://127.0.0.1:9224/devtools/browser/wrong-port",
                }
            return {
                "Browser": "Chromium",
                "webSocketDebuggerUrl": f"ws://127.0.0.1:{port}/devtools/browser/ok",
            }

        fake, _ = self._fake_recorder(http_json)
        self.assertIsNone(fake.find_endpoint("127.0.0.1", 9223))
        self.assertEqual(calls, [9223])
        self.assertEqual(fake._WOF052L_LAST_ENDPOINT_REJECTION["reason"], "returned-websocket-cross-port")

    def test_simulated_10_room_one_endpoint_failure_does_not_poison_other_nine(self) -> None:
        def http_json(url: str):
            port = int(url.split(":")[-1].split("/")[0])
            returned_port = 9999 if port == 9305 else port
            return {
                "Browser": "Chromium",
                "webSocketDebuggerUrl": f"ws://localhost:{returned_port}/devtools/browser/{port}",
            }

        fake, launched = self._fake_recorder(
            http_json,
            candidate_ports=lambda explicit: list(range(9300, 9310)),
        )
        rows = [fake.probe_endpoint("127.0.0.1", 9300 + index) for index in range(10)]
        self.assertEqual(sum(row is not None for row in rows), 9)
        self.assertIsNone(rows[5])
        self.assertTrue(all(rows[index] is not None for index in range(10) if index != 5))
        self.assertIsNone(fake.launch_debug_browser("auto", "192.0.2.1", 9223, None))
        self.assertEqual(launched, [])


class PerPageClient(base_discovery_tests.C):
    def __init__(self, state, events_by_page):
        super().__init__(state=state, events=[])
        self.events_by_page = events_by_page
        self.current_page: str | None = None
        self.sent_pages: set[str] = set()

    def attach(self, target_id):
        target_id = str(target_id)
        if target_id.startswith("p"):
            self.current_page = target_id
        return base_discovery_tests.S(self, target_id, "sid-" + target_id)

    def wait_for_events(self, cursor, *, timeout, predicate=None):
        page_id = self.current_page
        if not page_id or page_id in self.sent_pages:
            return cursor, []
        self.sent_pages.add(page_id)
        rows = list(self.events_by_page.get(page_id, []))
        if predicate is not None:
            rows = [row for row in rows if predicate(row)]
        return cursor + 1, rows


class FakeCandidate:
    def __init__(self, worker_id: str, page_id: str):
        self.target = {"targetId": worker_id}
        self.page = {"targetId": page_id}
        self.closed = False

    def close(self):
        self.closed = True


class FakeRoom:
    def __init__(self, worker_id: str, page_id: str):
        self.target = {"targetId": worker_id, "discoveryPath": "page-autoattach"}
        self.page = {"targetId": page_id}


class DiscoveryHardeningTests(unittest.TestCase):
    def test_one_page_one_worker_and_two_pages_two_distinct_workers_still_pass(self) -> None:
        manager = base_discovery_tests.M(
            base_discovery_tests.C(
                {
                    "w1": {"identity": base_discovery_tests.I()},
                    "w2": {"identity": base_discovery_tests.I()},
                }
            )
        )
        rows, diag = discovery.discover_candidates(
            manager,
            [
                base_discovery_tests.P("p1"),
                base_discovery_tests.P("p2"),
                base_discovery_tests.W("w1", parentId="p1"),
                base_discovery_tests.W("w2", parentId="p2"),
            ],
        )
        self.assertEqual({row.target["targetId"] for row in rows}, {"w1", "w2"})
        self.assertEqual(diag["crossPageAmbiguityCount"], 0)
        for row in rows:
            row.close()

        manager_one = base_discovery_tests.M(
            base_discovery_tests.C({"w3": {"identity": base_discovery_tests.I()}})
        )
        rows_one, _ = discovery.discover_candidates(
            manager_one,
            [base_discovery_tests.P("p3"), base_discovery_tests.W("w3", parentId="p3")],
        )
        self.assertEqual(len(rows_one), 1)
        rows_one[0].close()

    def test_same_shared_worker_under_two_pages_is_endpoint_ambiguous(self) -> None:
        shared = base_discovery_tests.W("shared", type="shared_worker")
        events = {
            "p1": [base_discovery_tests.A("sid-p1", shared, "sid-shared-1")],
            "p2": [base_discovery_tests.A("sid-p2", shared, "sid-shared-2")],
        }
        client = PerPageClient(
            {"shared": {"identity": base_discovery_tests.I()}},
            events,
        )
        manager = base_discovery_tests.M(client)
        rows, diag = discovery.discover_candidates(
            manager,
            [base_discovery_tests.P("p1"), base_discovery_tests.P("p2")],
        )
        self.assertEqual(rows, [])
        self.assertEqual(diag["crossPageAmbiguityCount"], 1)
        ambiguity = diag["crossPageWorkerAmbiguities"][0]
        self.assertEqual(ambiguity["status"], hardening.CROSS_PAGE_AMBIGUITY)
        self.assertEqual(ambiguity["workerTargetId"], "shared")
        self.assertEqual(ambiguity["pageTargetIds"], ["p1", "p2"])

    def test_mid_capture_ambiguity_finalizes_only_affected_room_before_more_evidence(self) -> None:
        calls: list[tuple[str, str, bool]] = []

        class Manager:
            def __init__(self):
                self.live = {
                    "shared": FakeRoom("shared", "p1"),
                    "other": FakeRoom("other", "p3"),
                }

            def _finalize_target(self, target_id, reason, try_remote):
                calls.append((target_id, reason, try_remote))
                self.live.pop(target_id, None)

        candidate = FakeCandidate("shared", "p2")
        manager = Manager()
        admitted, topology = hardening.filter_cross_page_ambiguity(
            manager,
            [candidate],
            {"relatedPages": []},
        )
        self.assertEqual(admitted, [])
        self.assertTrue(candidate.closed)
        finalized = hardening.finalize_cross_page_ambiguous_live(manager, topology)
        self.assertEqual(finalized, ["shared"])
        self.assertEqual(
            calls,
            [("shared", hardening.CROSS_PAGE_AMBIGUITY, False)],
        )
        self.assertIn("other", manager.live)

    def test_existing_blob_data_hashed_and_no_extension_worker_urls_are_hints_only(self) -> None:
        urls = (
            "blob:https://example/worker",
            "data:text/javascript;base64,Zm9v",
            "https://cdn.example/a1b2c3d4",
            "https://cdn.example/worker-main.mjs?v=9",
        )
        for url in urls:
            with self.subTest(url=url):
                self.assertTrue(
                    hardening.worker_compatible(
                        base_discovery_tests.W("w", url=url),
                        related=False,
                    )
                )

        for url in urls[:2]:
            with self.subTest(exact_identity_url=url):
                manager = base_discovery_tests.M(
                    base_discovery_tests.C({"w": {"identity": base_discovery_tests.I()}})
                )
                rows, _ = discovery.discover_candidates(
                    manager,
                    [base_discovery_tests.P("p"), base_discovery_tests.W("w", url=url, parentId="p")],
                )
                self.assertEqual(len(rows), 1)
                rows[0].close()

    def test_wrong_identity_still_rejected_even_when_url_shape_is_allowed(self) -> None:
        manager = base_discovery_tests.M(
            base_discovery_tests.C(
                {"w": {"identity": base_discovery_tests.I(False, "0" * 64)}}
            )
        )
        rows, diag = discovery.discover_candidates(
            manager,
            [
                base_discovery_tests.P("p"),
                base_discovery_tests.W("w", url="blob:https://example/worker", parentId="p"),
            ],
        )
        self.assertEqual(rows, [])
        self.assertTrue(any(row.get("status") == "wrong-identity" for row in diag["directWorkers"]))

    def test_direct_fallback_never_uses_misleading_opener_as_parent_authority(self) -> None:
        manager = base_discovery_tests.M(
            base_discovery_tests.C({"w": {"identity": base_discovery_tests.I()}})
        )
        rows, diag = discovery.discover_candidates(
            manager,
            [
                base_discovery_tests.P("p1"),
                base_discovery_tests.P("p2"),
                base_discovery_tests.W("w", openerId="p1"),
            ],
        )
        self.assertEqual(rows, [])
        self.assertTrue(
            any(row.get("status") == "page-association-ambiguous" for row in diag["directWorkers"])
        )

    def test_direct_fallback_accepts_unique_page_and_parentid_overrides_opener(self) -> None:
        manager_unique = base_discovery_tests.M(
            base_discovery_tests.C({"w1": {"identity": base_discovery_tests.I()}})
        )
        rows, _ = discovery.discover_candidates(
            manager_unique,
            [base_discovery_tests.P("p1"), base_discovery_tests.W("w1", openerId="wrong")],
        )
        self.assertEqual(rows[0].page["targetId"], "p1")
        rows[0].close()

        manager_parent = base_discovery_tests.M(
            base_discovery_tests.C({"w2": {"identity": base_discovery_tests.I()}})
        )
        rows_parent, _ = discovery.discover_candidates(
            manager_parent,
            [
                base_discovery_tests.P("p1"),
                base_discovery_tests.P("p2"),
                base_discovery_tests.W("w2", parentId="p2", openerId="p1"),
            ],
        )
        self.assertEqual(rows_parent[0].page["targetId"], "p2")
        rows_parent[0].close()


class SafetyAndChineseUxTests(unittest.TestCase):
    def test_world_gate_read_only_policy_and_no_worker_replacement_remain_intact(self) -> None:
        self.assertEqual(recorder.WORLD_SHA256, WORLD)
        self.assertIn("Target.setAutoAttach", recorder.READ_ONLY_METHODS)
        self.assertFalse(any(str(method).startswith("Input.") for method in recorder.READ_ONLY_METHODS))
        self.assertNotIn("Runtime.callFunctionOn", recorder.READ_ONLY_METHODS)
        self.assertNotIn("Page.addScriptToEvaluateOnNewDocument", recorder.READ_ONLY_METHODS)
        source = inspect.getsource(hardening)
        self.assertNotIn("new Worker(", source)
        self.assertNotIn("window.Worker =", source)
        self.assertNotIn("HEAPU8[", source)
        self.assertNotIn("HEAPU32[", source)
        self.assertTrue(getattr(recorder, "_WOF052L_HARDENING_V2_INSTALLED", False))

    def test_normal_recorder_and_fleet_runtime_messages_are_chinese_first(self) -> None:
        source = "\n".join(
            inspect.getsource(method)
            for method in (
                recorder.RecorderManager.ensure_browser,
                recorder.RecorderManager._finalize_target,
                recorder.RecorderManager.shutdown,
                fleet_recorder.FleetRecorderManager.ensure_browser,
                fleet_recorder.FleetRecorderManager.run_managed,
                fleet_recorder.FleetSupervisor.run,
            )
        )
        for old in (
            "WAITING ",
            "other rooms continue",
            "CDP connect failed safely",
            "Browser OK",
            "WOF-052L fleet recorder #",
            "Stopping fleet recorder",
            "Final merged JSON:",
            " finalized (",
        ):
            self.assertNotIn(old, source)
        for marker in ("等待本机", "浏览器已连接", "技术详情", "已启动", "已完成", "最终合并 JSON"):
            self.assertIn(marker, source)

    def test_remote_host_owner_error_is_chinese_then_technical_detail(self) -> None:
        args = argparse.Namespace(
            cdp_host="192.0.2.1",
            cdp_port=9223,
            no_launch_browser=True,
            browser="auto",
            game_url=None,
        )
        with tempfile.TemporaryDirectory() as temp:
            manager = recorder.RecorderManager(Path(temp), args)
            out = io.StringIO()
            with redirect_stdout(out):
                self.assertFalse(manager.ensure_browser())
        text = out.getvalue()
        chinese_pos = text.find("已安全拒绝连接")
        detail_pos = text.find("技术详情：remote-cdp-host-rejected")
        self.assertGreaterEqual(chinese_pos, 0)
        self.assertGreater(detail_pos, chinese_pos)
        self.assertNotIn("WAITING for Chrome/Edge", text)

    def test_chinese_path_spaces_and_merged_json_contract_remain_valid(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            output_dir = Path(temp) / "中文 路径" / "WOF 采集"
            for child in ("rooms", "checkpoints", "runs"):
                (output_dir / child).mkdir(parents=True, exist_ok=True)
            args = argparse.Namespace(
                cdp_host="127.0.0.1",
                cdp_port=9223,
                no_launch_browser=True,
                browser="auto",
                game_url=None,
            )
            manager = recorder.RecorderManager(output_dir, args)
            manager.write_merged(False)
            payload = json.loads(manager.run_file.read_text(encoding="utf-8"))
        self.assertEqual(payload["schema"], recorder.SCHEMA_VERSION)
        self.assertEqual(payload["safety"], {"readOnly": True, "ramWrites": 0, "inputInjection": False})
        self.assertEqual(payload["identityPolicy"]["sha256"], WORLD)

    def test_existing_cadence_and_checkpoint_constants_are_unchanged(self) -> None:
        self.assertEqual(recorder.DRAIN_INTERVAL, 1.0)
        self.assertEqual(recorder.CHECKPOINT_INTERVAL, 10.0)
        self.assertEqual(recorder.DISCOVERY_INTERVAL, 1.0)
        self.assertEqual(recorder.ROLLING_MERGE_INTERVAL, 15.0)


def load_tests(loader, tests, pattern):
    tests.addTests(loader.loadTestsFromModule(base_discovery_tests))
    return tests


if __name__ == "__main__":
    unittest.main()
