from __future__ import annotations

import argparse
import json
import time
import uuid
from pathlib import Path
from typing import Any

import live_validator as core
from discovery_v2 import (
    Candidate,
    OwnedSession,
    ambiguous_page_ids,
    discover_candidates,
    discovery_status_zh,
    install_cdp_event_support,
    room_liveness_reason,
)
from validator import ValidationError, validate_session

# Kept explicit for the independent QA fixture. A positive live-topology audit
# interval is forbidden: every evidence ingest cycle performs a full audit.
AUDIT_LIVE_TOPOLOGY_INTERVAL = 0.0

if core.recorder_core is not None:
    install_cdp_event_support(core.recorder_core)


_REASON_ZH = {
    "browser-cdp-disconnect": "浏览器 CDP 已断开",
    "worker-closed-or-reloaded": "Worker 已关闭或重建",
    "page-closed-or-reloaded": "页面已关闭或重载",
    "worker-association-ambiguous": "Worker 关联变得不唯一，已安全停止该房间",
    "worker-association-unverified": "当前 Worker 与页面唯一归属无法重新证明，已安全停止该房间",
    "worker-cdp-error": "Worker CDP 会话已失效",
    "validator-stopped": "验证器已停止",
}


def _identity_sha(payload: Any) -> str | None:
    if not isinstance(payload, dict):
        return None
    inner = payload.get("identity") if isinstance(payload.get("identity"), dict) else payload
    value = inner.get("sha256") if isinstance(inner, dict) else None
    return str(value) if isinstance(value, str) else None


def _room_page_id(room: Any) -> str:
    return str(getattr(room, "page_id", "") or "")


def _room_path(room: Any) -> str:
    return str(getattr(room, "discovery_path", "direct-worker") or "direct-worker")


class LiveValidatorV2(core.LiveValidator):
    def __init__(self, manifest: dict[str, Any], output: Path, fleet_manifest: Path | None, port: int | None):
        super().__init__(manifest, output, fleet_manifest, port)
        validate_session(self.session, self.manifest)
        self._last_discovery_message: dict[str, str] = {}

    def _announce(self, endpoint: core.Endpoint, message: str) -> None:
        key = f"{endpoint.host}:{endpoint.port}"
        if self._last_discovery_message.get(key) == message:
            return
        self._last_discovery_message[key] = message
        print(f"\n[{endpoint.label}] {message}")

    def attach_candidate(self, endpoint: core.Endpoint, candidate: Candidate) -> None:
        if endpoint.client is None:
            candidate.close()
            return
        target_id = str(candidate.target.get("targetId") or "")
        page_id = str(candidate.page.get("targetId") or "")
        if not target_id or not page_id:
            candidate.close()
            return
        if target_id in endpoint.rooms or any(_room_page_id(room) == page_id for room in endpoint.rooms.values()):
            candidate.close()
            return

        validate_session(self.session, self.manifest)
        if _identity_sha(candidate.identity) != core.recorder_core.WORLD_SHA256:
            candidate.close()
            self._announce(endpoint, "Worker 已发现，但 World 921031 身份不匹配；已安全拒绝准入。")
            return

        session = OwnedSession(candidate.session, candidate.owner_sessions)
        candidate.owner_sessions = []
        candidate.session = None
        try:
            boot = session.evaluate(self.probe_js, timeout=8.0)
            if (
                not isinstance(boot, dict)
                or boot.get("ok") is not True
                or boot.get("manifestId") != self.manifest.get("id")
                or boot.get("readOnly") is not True
                or int(boot.get("ramWrites") or 0) != 0
                or boot.get("inputInjection") is not False
                or boot.get("windowWorkerReplacement") is not False
            ):
                raise RuntimeError("prospective probe bootstrap failed safety/manifest gate")

            room_id = f"{endpoint.label}-{target_id[:10]}-{uuid.uuid4().hex[:6]}"
            room = core.Room(
                room_id=room_id,
                target_id=target_id,
                session=session,
                started_at=core.recorder_core.utc_iso(),
            )
            room.page_id = page_id
            room.discovery_path = candidate.path
            endpoint.rooms[target_id] = room
            self._last_discovery_message.pop(f"{endpoint.host}:{endpoint.port}", None)
            print(f"+ 已连接房间 {room_id}｜Discovery V2｜World 921031 已确认｜只读")
        except Exception as exc:
            session.close()
            self._announce(endpoint, f"Worker 已发现，但前瞻验证准入失败；游戏本身不受影响。技术详情：{exc}")

    def finalize_room(self, endpoint: core.Endpoint, tid: str, reason: str, remote: bool) -> None:
        room = endpoint.rooms.pop(tid, None)
        if not room:
            return
        if remote:
            # Cleanup may stop the in-Worker sampler, but its returned queue is
            # deliberately discarded. Final evidence may only enter via a
            # successful full topology audit immediately before drain().
            try:
                room.session.evaluate(
                    "globalThis.__WOF_PROSPECTIVE_VALIDATOR ? globalThis.__WOF_PROSPECTIVE_VALIDATOR.stop() : null",
                    timeout=5.0,
                )
            except Exception:
                pass
        if room.pending:
            for pending in room.pending:
                trace = dict(pending)
                trace.update({
                    "roomId": room.room_id,
                    "evidenceClass": "prospective",
                    "startedAt": room.started_at,
                    "activeAttack": None,
                    "censored": True,
                    "targetStable": pending.get("targetStart7E") == pending.get("targetLast7E"),
                    "sideStable": pending.get("sideStart") == pending.get("sideLast"),
                    "retargets": pending.get("retargets") or [],
                    "censorReason": reason,
                })
                self.traces.append(trace)
        try:
            room.session.close()
        except Exception:
            pass
        print(f"- 房间结束 {room.room_id}（{_REASON_ZH.get(reason, reason)}）")

    def discover_and_poll(self, endpoint: core.Endpoint, now: float) -> None:
        if not endpoint.connect():
            for tid in list(endpoint.rooms):
                self.finalize_room(endpoint, tid, "browser-cdp-disconnect", remote=False)
            return

        # No prospective evidence is drained between discovery cycles. The only
        # drain path is below, after a fresh full topology scan has positively
        # re-proved every surviving live (page, Worker) ownership pair.
        if now - endpoint.last_discovery < core.DISCOVERY_INTERVAL:
            return

        endpoint.last_discovery = now
        try:
            targets = endpoint.client.targets()
        except Exception:
            for tid in list(endpoint.rooms):
                self.finalize_room(endpoint, tid, "browser-cdp-disconnect", remote=False)
            endpoint.close_client()
            return

        current_target_ids = {
            str(target.get("targetId"))
            for target in targets
            if isinstance(target, dict) and target.get("targetId")
        }
        current_page_ids = {
            str(target.get("targetId"))
            for target in targets
            if isinstance(target, dict) and target.get("type") == "page" and target.get("targetId")
        }
        for tid, room in list(endpoint.rooms.items()):
            reason = room_liveness_reason(
                discovery_path=_room_path(room),
                target_id=tid,
                page_id=_room_page_id(room),
                current_target_ids=current_target_ids,
                current_page_ids=current_page_ids,
            )
            if reason:
                self.finalize_room(endpoint, tid, reason, remote=False)

        try:
            candidates, diag = discover_candidates(
                endpoint.client,
                targets,
                session_factory=core.recorder_core.CdpSession,
                light_probe_js=core.recorder_core.LIGHT_PROBE,
                identity_probe_js=core.IDENTITY_JS,
                expected_sha256=core.recorder_core.WORLD_SHA256,
                skip_page_ids=set(),
                endpoint_label=endpoint.label,
            )
        except Exception as exc:
            # A failed topology proof cannot be followed by a later drain of
            # evidence accumulated during the unverified interval. Censor now.
            self._announce(endpoint, f"Discovery V2 全量拓扑复核失败；在线房间已保守停止，游戏本身不受影响。技术详情：{exc}")
            for tid in list(endpoint.rooms):
                self.finalize_room(endpoint, tid, "worker-association-unverified", remote=False)
            return

        endpoint._prospective_v2_last_audit = now
        endpoint._prospective_v2_last_diag = diag

        ambiguous = ambiguous_page_ids(diag)
        if ambiguous:
            for tid, room in list(endpoint.rooms.items()):
                if _room_page_id(room) in ambiguous:
                    self.finalize_room(endpoint, tid, "worker-association-ambiguous", remote=False)

        # A room is allowed to drain only if this exact full scan produced the
        # same page -> exact supported Worker pair. Absence of ambiguity alone
        # is not sufficient proof.
        proven_pairs = {
            (
                str(candidate.page.get("targetId") or ""),
                str(candidate.target.get("targetId") or ""),
            )
            for candidate in candidates
            if str(candidate.page.get("targetId") or "") and str(candidate.target.get("targetId") or "")
        }

        if not candidates:
            self._announce(endpoint, discovery_status_zh(diag))
        else:
            for candidate in candidates:
                if str(candidate.page.get("targetId") or "") in ambiguous:
                    candidate.close()
                    continue
                try:
                    self.attach_candidate(endpoint, candidate)
                except ValidationError:
                    candidate.close()
                    raise
                except Exception as exc:
                    candidate.close()
                    self._announce(endpoint, f"单个房间准入失败；其他房间继续运行。技术详情：{exc}")

        for tid, room in list(endpoint.rooms.items()):
            pair = (_room_page_id(room), str(tid))
            if pair not in proven_pairs:
                self.finalize_room(endpoint, tid, "worker-association-unverified", remote=False)

        for tid, room in list(endpoint.rooms.items()):
            try:
                payload = room.session.evaluate(
                    "globalThis.__WOF_PROSPECTIVE_VALIDATOR ? globalThis.__WOF_PROSPECTIVE_VALIDATOR.drain() : null",
                    timeout=4.0,
                )
                if not isinstance(payload, dict) or payload.get("ok") is not True:
                    raise RuntimeError("live probe drain malformed")
                self.ingest(room, payload)
            except Exception:
                self.finalize_room(endpoint, tid, "worker-cdp-error", remote=False)

    def write(self, final: bool) -> dict[str, Any]:
        validate_session(self.session, self.manifest)
        corpus = self.corpus(final)
        if "discovery" in corpus or "discoveryDiagnostics" in corpus:
            raise ValidationError("discovery diagnostics must not enter prospective corpus")
        return super().write(final)

    def run(self) -> int:
        print(f"WOF 前瞻验证：{self.manifest['id']}")
        print("Worker 自动发现：Discovery V2（page / iframe / Worker topology）")
        print("安全：只读模式开启｜游戏内存写入 0｜游戏输入注入 无｜window.Worker 替换 无")
        print("正在复用 Browser Fleet / localhost CDP。没有可用端点时只等待，不影响游戏。按 Ctrl+C 结束。")
        rc = 0
        manifest_valid = True
        try:
            while True:
                now = time.monotonic()
                for endpoint in self.endpoints:
                    self.discover_and_poll(endpoint, now)
                if now - self.last_checkpoint >= core.CHECKPOINT_INTERVAL:
                    self.last_checkpoint = now
                    result = self.write(False)
                    p = result["prospective"]
                    rooms = sum(len(endpoint.rooms) for endpoint in self.endpoints)
                    print(
                        f"\r在线房间 {rooms}｜信号 {p['signal']}｜严格命中 {p['strict']}｜抖动命中 {p['jitter']}｜"
                        f"迟到 {p['late']}｜硬失败 {p['hardMiss']}｜已删失 {p['censored']}   ",
                        end="",
                        flush=True,
                    )
                time.sleep(core.DEFAULT_POLL)
        except KeyboardInterrupt:
            pass
        except ValidationError as exc:
            manifest_valid = False
            rc = 2
            print(f"\n冻结候选已发生变化，已停止收集新的 prospective 证据。技术详情：{exc}")
        finally:
            for endpoint in self.endpoints:
                for tid in list(endpoint.rooms):
                    self.finalize_room(endpoint, tid, "validator-stopped", remote=manifest_valid)
                endpoint.close()

        if manifest_valid:
            result = self.write(True)
            compact = core.compact_result(result)
            print("\n验证已结束。")
            print(f"最终判定：{compact.get('verdict')}")
            print(f"证据文件：{self.output}")
            print(f"结果文件：{self.output.with_name(self.output.stem + '.result.json')}")
        return rc


def main() -> int:
    ap = argparse.ArgumentParser(description="WOF 通用 live prospective validator Discovery V2（只读）")
    ap.add_argument("manifest", help="候选 manifest JSON")
    ap.add_argument("--output", help="统一 prospective corpus JSON 输出")
    ap.add_argument("--fleet-manifest", help="Browser Fleet instances.json；省略使用默认路径")
    ap.add_argument("--cdp-port", type=int, help="只连接指定 localhost CDP 端口")
    ap.add_argument("--dump-probe", help="仅输出生成的 JS probe 到文件并退出（测试用）")
    args = ap.parse_args()
    try:
        manifest = core.validate_manifest(core.load_json(args.manifest))
    except (OSError, json.JSONDecodeError, core.ValidationError) as exc:
        print(f"候选 manifest 无效：{exc}")
        return 2
    if args.dump_probe:
        Path(args.dump_probe).write_text(core.build_probe_js(manifest) + "\n", encoding="utf-8")
        return 0
    if core.recorder_core is None:
        print("找不到 parallel/WOF052L_RECORDER/recorder.py，无法使用只读 CDP 基础设施。")
        return 2
    stamp = time.strftime("%Y%m%d_%H%M%S")
    output = Path(args.output).expanduser().resolve() if args.output else core.HERE / "results" / f"{stamp}_{manifest['id']}_live_corpus.json"
    fleet = Path(args.fleet_manifest).expanduser().resolve() if args.fleet_manifest else None
    return LiveValidatorV2(manifest, output, fleet, args.cdp_port).run()


if __name__ == "__main__":
    raise SystemExit(main())
