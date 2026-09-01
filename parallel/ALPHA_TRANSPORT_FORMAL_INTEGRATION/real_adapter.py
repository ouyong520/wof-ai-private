from __future__ import annotations

import argparse
import json
import secrets
import sys
import time
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
PYLAUNCH = ROOT / "parallel" / "PYLAUNCH"
if str(PYLAUNCH) not in sys.path:
    sys.path.insert(0, str(PYLAUNCH))

from wof_launcher.cdp import CdpClient  # noqa: E402
from wof_launcher.discovery_v2 import TargetChoice, discover  # noqa: E402

RELEASE = "wof-alpha-rc3"
SCHEMA = "wof-alpha-v2"
TRANSPORT = "wof-alpha-safe-transport-v1"
GOLDEN_SHA = "5c369ce2de4f53d8cef87eca5623a1f0d39a779e885532d6f185b81357878f62"
IDENTITY_SIGNATURE = "wof-world-921031-maincpu-sha256-v1:5c369ce2de4f53d8"
WORKER_SOURCE = ROOT / "product" / "alpha" / "wof_alpha_real_worker.js"


def _browser_ws_url(host: str, port: int) -> str:
    url = f"http://{host}:{port}/json/version"
    with urllib.request.urlopen(url, timeout=2.0) as response:
        payload = json.loads(response.read().decode("utf-8"))
    ws = payload.get("webSocketDebuggerUrl")
    if not isinstance(ws, str) or not ws.startswith("ws"):
        raise RuntimeError("浏览器未提供可用的本机 CDP WebSocket")
    return ws


def _eval(client: CdpClient, target_id: str, expression: str, *, await_promise: bool = False, timeout: float = 8.0) -> Any:
    session = client.attach(target_id)
    try:
        session.request("Runtime.enable")
        return session.evaluate(expression, await_promise=await_promise, timeout=timeout)
    finally:
        session.close()


def _safe_target_id(target: dict[str, Any] | None) -> str | None:
    value = target.get("targetId") if isinstance(target, dict) else None
    return value if isinstance(value, str) and value else None


def _choice_supported(choice: TargetChoice) -> bool:
    if choice.reason is not None or not isinstance(choice.page, dict) or not isinstance(choice.worker, dict) or not isinstance(choice.identity, dict):
        return False
    identity = choice.identity
    return (
        identity.get("ok") is True
        and identity.get("sha256") == GOLDEN_SHA
        and identity.get("readOnly") is True
        and identity.get("ramWrites") == 0
        and identity.get("inputInjection") is False
    )


def _choice_identity_sha(choice: TargetChoice) -> str:
    if not _choice_supported(choice) or not isinstance(choice.identity, dict):
        raise RuntimeError("Discovery V2 未提供可绑定的精确 World 921031 身份证据")
    sha = choice.identity.get("sha256")
    if sha != GOLDEN_SHA:
        raise RuntimeError("Discovery V2 World 921031 SHA-256 不匹配")
    return str(sha)


@dataclass(frozen=True)
class ActiveBinding:
    page_id: str
    worker_id: str
    session: str
    pair_generation: int
    pair_nonce: str
    runtime_epoch: str


class FormalRealAdapter:
    """Production-facing, read-only bridge from PYLAUNCH Discovery V2 into Alpha RC5."""

    def __init__(self, client: CdpClient, worker_source: str) -> None:
        self.client = client
        self.worker_source = worker_source
        self.current: ActiveBinding | None = None
        self.last_reason: str | None = None

    def _page_status(self, page_id: str) -> dict[str, Any] | None:
        value = _eval(
            self.client,
            page_id,
            "(()=>{const t=window.__WOF_ALPHA_TRANSPORT_V1;return t&&typeof t.status==='function'?t.status():null})()",
        )
        return value if isinstance(value, dict) else None

    def _worker_status(self, worker_id: str) -> dict[str, Any] | None:
        value = _eval(
            self.client,
            worker_id,
            "(()=>{const r=self.__WOF_ALPHA_REAL_TRANSPORT;return r&&typeof r.status==='function'?r.status():null})()",
        )
        return value if isinstance(value, dict) else None

    def _reset_page(self, page_id: str) -> None:
        value = _eval(
            self.client,
            page_id,
            "(()=>{const t=window.__WOF_ALPHA_TRANSPORT_V1;return t&&typeof t.reset==='function'?t.reset():null})()",
        )
        if not isinstance(value, dict) or value.get("bound") is not False:
            raise RuntimeError("页面旧 warning authority 未确认撤销")

    def _stop_worker(self, worker_id: str) -> bool:
        value = _eval(
            self.client,
            worker_id,
            "(()=>{const r=self.__WOF_ALPHA_REAL_TRANSPORT;return !r||typeof r.stop!=='function'?true:r.stop('adapter-rebind')})()",
        )
        return value is True

    def revoke(self) -> None:
        """Best-effort teardown for disconnect/exit; never creates new authority."""
        old = self.current
        self.current = None
        if old is None:
            return
        try:
            self._reset_page(old.page_id)
        except Exception:
            pass
        try:
            self._stop_worker(old.worker_id)
        except Exception:
            pass

    def _strict_revoke_for_rebind(self, next_page_id: str, next_worker_id: str) -> None:
        """Fail closed if a still-addressable old authority cannot be proven revoked."""
        old = self.current
        self.current = None
        if old is None:
            return

        try:
            self._reset_page(old.page_id)
        except Exception as exc:
            if old.page_id == next_page_id:
                raise RuntimeError("同一页面旧 warning authority 无法确认撤销；拒绝建立新 generation") from exc

        if old.worker_id == next_worker_id:
            try:
                stopped = self._stop_worker(old.worker_id)
            except Exception as exc:
                raise RuntimeError("同一原生 Worker 的旧 observer 无法确认停止；拒绝建立新 generation") from exc
            if not stopped:
                raise RuntimeError("同一原生 Worker 的旧 observer 拒绝停止；拒绝建立新 generation")
        else:
            # A different targetId is a Worker/runtime replacement. The old target may
            # already be gone; page authority was revoked above, so any late old
            # completion cannot pass the new pair generation/nonce gate.
            try:
                self._stop_worker(old.worker_id)
            except Exception:
                pass

    def _read_page_config(self, page_id: str) -> dict[str, Any] | None:
        value = _eval(
            self.client,
            page_id,
            "(()=>{const c=window.__WOF_ALPHA_CONFIG,t=window.__WOF_ALPHA_TRANSPORT_V1;return c&&t?{release:c.release,schema:c.schema,session:c.session,channel:c.channel,transport:t.version}:null})()",
        )
        if not isinstance(value, dict):
            return None
        session = value.get("session")
        return value if (
            value.get("release") == RELEASE
            and value.get("schema") == SCHEMA
            and value.get("transport") == TRANSPORT
            and isinstance(session, str)
            and len(session) == 32
            and value.get("channel") == f"WOF_ALPHA_{session}"
        ) else None

    def _bind_page(self, page_id: str, pair_nonce: str) -> dict[str, Any]:
        expression = "(()=>window.__WOF_ALPHA_TRANSPORT_V1.bind(" + json.dumps(pair_nonce) + "))()"
        value = _eval(self.client, page_id, expression)
        if not isinstance(value, dict) or value.get("bound") is not True:
            raise RuntimeError("Alpha 页面拒绝正式传输绑定")
        return value

    def _install_worker(self, worker_id: str, binding: dict[str, Any]) -> dict[str, Any]:
        source = json.dumps(self.worker_source)
        payload = json.dumps(binding, separators=(",", ":"))
        expression = f"""(async()=>{{
const previous=self.__WOF_ALPHA_REAL_TRANSPORT;
if(previous&&typeof previous.stop==='function'&&previous.stop('formal-rebind')!==true)throw new Error('旧 observer 未安全停止');
self.__WOF_ALPHA_REAL_ADAPTER_BINDING={payload};
(0,eval)({source});
const deadline=Date.now()+30000;
while(Date.now()<deadline){{
  const r=self.__WOF_ALPHA_REAL_TRANSPORT;
  if(r&&typeof r.status==='function'){{const s=r.status();if(s&&s.runtimeEpoch==={json.dumps(binding['runtimeEpoch'])})return s;}}
  if(r&&r.running===false&&r.lastError)throw new Error(String(r.lastError));
  await new Promise(resolve=>setTimeout(resolve,25));
}}
throw new Error('正式 observer 启动超时');
}})()"""
        value = _eval(self.client, worker_id, expression, await_promise=True, timeout=35.0)
        if not isinstance(value, dict) or value.get("running") is not True:
            raise RuntimeError("原生 Worker observer 未进入运行态")
        identity = value.get("identity")
        if not isinstance(identity, dict) or identity.get("ok") is not True or identity.get("sha256") != GOLDEN_SHA:
            raise RuntimeError("检测器本地最新 World 921031 SHA-256 身份证据不匹配")
        if value.get("identitySignature") != IDENTITY_SIGNATURE or identity.get("identitySignature") != IDENTITY_SIGNATURE:
            raise RuntimeError("检测器本地身份签名不匹配")
        if not (
            identity.get("readOnly") is True
            and identity.get("ramWrites") == 0
            and identity.get("inputInjection") is False
            and value.get("readOnly") is True
            and value.get("ramWrites") == 0
            and value.get("inputInjection") is False
            and value.get("workerReplacement") is False
            and value.get("queueDepth") == 0
        ):
            raise RuntimeError("原生 Worker observer 安全状态不满足正式传输合同")
        return value

    def _current_still_authoritative(self, choice: TargetChoice) -> bool:
        current = self.current
        if current is None:
            return False
        if _safe_target_id(choice.page) != current.page_id or _safe_target_id(choice.worker) != current.worker_id:
            return False
        try:
            page = self._page_status(current.page_id)
            worker = self._worker_status(current.worker_id)
        except Exception:
            return False
        identity = worker.get("identity") if isinstance(worker, dict) else None
        return bool(
            page and worker and isinstance(identity, dict)
            and page.get("bound") is True
            and page.get("transportVersion") == TRANSPORT
            and page.get("session") == current.session
            and page.get("pairGeneration") == current.pair_generation
            and page.get("pairNonce") == current.pair_nonce
            and worker.get("running") is True
            and worker.get("identitySignature") == IDENTITY_SIGNATURE
            and identity.get("ok") is True
            and identity.get("sha256") == GOLDEN_SHA
            and identity.get("identitySignature") == IDENTITY_SIGNATURE
            and worker.get("runtimeEpoch") == current.runtime_epoch
            and worker.get("session") == current.session
            and worker.get("pairGeneration") == current.pair_generation
            and worker.get("pairNonce") == current.pair_nonce
            and worker.get("queueDepth") == 0
            and worker.get("readOnly") is True
            and worker.get("ramWrites") == 0
            and worker.get("inputInjection") is False
            and worker.get("workerReplacement") is False
        )

    def bind_choice(self, choice: TargetChoice) -> ActiveBinding:
        if not _choice_supported(choice):
            raise RuntimeError(choice.reason or "Discovery V2 未给出唯一受支持的 World 921031 page/Worker")
        page_id = _safe_target_id(choice.page)
        worker_id = _safe_target_id(choice.worker)
        if not page_id or not worker_id:
            raise RuntimeError("Discovery V2 缺少 page/Worker targetId")
        discovery_identity_sha = _choice_identity_sha(choice)

        # Rebinding starts by revoking old warning/detector authority. If the same
        # live page/Worker cannot prove revocation, no new generation is created.
        self._strict_revoke_for_rebind(page_id, worker_id)
        config = self._read_page_config(page_id)
        if config is None:
            raise RuntimeError("Alpha RC5 页面传输接口尚未就绪")

        pair_nonce = secrets.token_hex(16)
        runtime_epoch = secrets.token_hex(16)
        page_binding = self._bind_page(page_id, pair_nonce)
        binding = {
            "release": RELEASE,
            "schema": SCHEMA,
            "transportVersion": TRANSPORT,
            "session": config["session"],
            "channel": config["channel"],
            "pairGeneration": int(page_binding["pairGeneration"]),
            "pairNonce": pair_nonce,
            "runtimeEpoch": runtime_epoch,
            # Preserve the exact Discovery measurement as provenance only. The
            # installed native Worker must independently re-hash its current ROM.
            "launcherIdentitySha": discovery_identity_sha,
        }
        try:
            self._install_worker(worker_id, binding)
        except Exception:
            try:
                self._reset_page(page_id)
            except Exception:
                pass
            raise
        self.current = ActiveBinding(
            page_id=page_id,
            worker_id=worker_id,
            session=str(config["session"]),
            pair_generation=int(page_binding["pairGeneration"]),
            pair_nonce=pair_nonce,
            runtime_epoch=runtime_epoch,
        )
        self.last_reason = None
        return self.current

    def step(self) -> dict[str, Any]:
        choice = discover(self.client, identity_timeout=20.0, identity_cache={})
        if not _choice_supported(choice):
            self.revoke()
            self.last_reason = choice.reason or "当前发现结果不受支持"
            return {"ok": False, "reason": self.last_reason, "gameplayPlayable": True, "warningAuthority": False}
        if self._current_still_authoritative(choice):
            return {"ok": True, "rebound": False, "binding": self.current, "gameplayPlayable": True}
        binding = self.bind_choice(choice)
        return {"ok": True, "rebound": True, "binding": binding, "gameplayPlayable": True}


def run(host: str, port: int, interval: float) -> int:
    source = WORKER_SOURCE.read_text(encoding="utf-8")
    while True:
        client: CdpClient | None = None
        adapter: FormalRealAdapter | None = None
        try:
            client = CdpClient(_browser_ws_url(host, port), timeout=5.0)
            client.connect()
            adapter = FormalRealAdapter(client, source)
            print("WOF Alpha 正式只读传输已连接；等待唯一 World 921031 原生 Worker。", flush=True)
            while True:
                result = adapter.step()
                if result.get("rebound") is True:
                    b = result["binding"]
                    print(f"Alpha 已安全配对：generation={b.pair_generation}，原生 Worker 未替换。", flush=True)
                time.sleep(interval)
        except KeyboardInterrupt:
            if adapter:
                adapter.revoke()
            if client:
                client.close()
            return 0
        except Exception as exc:
            if adapter:
                adapter.revoke()
            if client:
                client.close()
            print("Alpha 传输暂不可用，警告保持关闭；游戏不受影响：" + str(exc), flush=True)
            time.sleep(max(1.0, interval))


def main() -> int:
    parser = argparse.ArgumentParser(description="WOF Alpha 正式 Safe Transport real-adapter（只读）")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=9223)
    parser.add_argument("--interval", type=float, default=1.0)
    args = parser.parse_args()
    return run(args.host, args.port, max(0.25, args.interval))


if __name__ == "__main__":
    raise SystemExit(main())
