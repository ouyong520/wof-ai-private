from __future__ import annotations

import hashlib
import json
import secrets
from pathlib import Path
from typing import Any

from .cdp import CdpClient, CdpError
from .discovery_v2 import TargetChoice
from .probe import WORLD_SHA256
from .projection_recovery import ProjectionRecovery, ProjectionRecoveryError


RELEASE = "wof-alpha-rc3"
SCHEMA = "wof-alpha-v2"
TRANSPORT = "wof-alpha-safe-transport-v1"
SAFETY = {"readOnly": True, "ramWrites": 0, "inputInjection": False}

PAGE_SOURCES = (
    "product/alpha/wof_alpha_bootstrap.user.js",
    "product/alpha/wof_alpha_hud_model.js",
    "product/alpha/wof_alpha_enemy_target_labels.js",
    "product/alpha/wof_alpha_player_head_warning.js",
    "product/alpha/wof_alpha_canonical_anchor_envelope.js",
    "product/alpha/wof_alpha_canonical_overlay_plan.js",
    "product/alpha/wof_alpha_hud.js",
)
WORKER_SOURCES = (
    "product/alpha/wof_alpha_core.js",
    "product/alpha/wof_alpha_enemy_target_labels.js",
    "product/alpha/wof_alpha_player_head_warning.js",
    "product/alpha/wof_alpha_field_adapter.js",
)
PROFILE_PATHS = {
    "enemy": "product/alpha/wof_alpha_enemy_head_projection.json",
    "player": "product/alpha/wof_alpha_player_head_projection.json",
}


class AlphaRuntimeError(RuntimeError):
    pass


def git_blob_sha(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


class AlphaRuntimeManager:
    """Installs package-selected Alpha after exact World authority is accepted.

    Static unproved projection profiles remain fail-closed. When they are unproved,
    a package-selected bounded live proof is automatically attached to the same
    accepted page/Worker pair. A successful proof yields in-memory profiles only for
    this launcher process; arbitrary serialized JSON cannot activate overlays.
    """

    def __init__(self, root: Path) -> None:
        self.root = Path(root).resolve()
        self._manifest: dict[str, Any] | None = None
        self._blob_map: dict[str, str] = {}
        self._authority_key: str | None = None
        self._page_target_id: str | None = None
        self._worker_target_id: str | None = None
        self._status: dict[str, Any] = {"requested": True, "running": False, **SAFETY}
        self._projection = ProjectionRecovery(self._verified_text)

    def _load_manifest(self) -> dict[str, Any]:
        if self._manifest is not None:
            return self._manifest
        candidates = (self.root / "PACKAGE_MANIFEST.json", self.root / "parallel" / "OWNER_ONECLICK" / "package_manifest.json")
        path = next((p for p in candidates if p.is_file()), None)
        if path is None:
            raise AlphaRuntimeError("找不到 package manifest；拒绝从未固定的 main/runtime 启动 Alpha")
        try:
            manifest = json.loads(path.read_text(encoding="utf-8-sig"))
        except Exception as exc:
            raise AlphaRuntimeError(f"package manifest 无法读取：{exc}") from exc
        files = manifest.get("files")
        if not isinstance(files, list):
            raise AlphaRuntimeError("package manifest 缺少 files")
        blob_map: dict[str, str] = {}
        for row in files:
            if not isinstance(row, dict):
                continue
            rel, sha = row.get("path"), row.get("gitBlobSha")
            if isinstance(rel, str) and isinstance(sha, str):
                blob_map[rel] = sha.lower()
        self._manifest = manifest
        self._blob_map = blob_map
        return manifest

    def _verified_bytes(self, rel: str) -> bytes:
        self._load_manifest()
        wanted = self._blob_map.get(rel)
        if not wanted or len(wanted) != 40:
            raise AlphaRuntimeError(f"package manifest 未固定 Alpha runtime 文件：{rel}")
        path = self.root / rel
        try:
            data = path.read_bytes()
        except OSError as exc:
            raise AlphaRuntimeError(f"package-selected runtime 文件缺失：{rel}") from exc
        actual = git_blob_sha(data)
        if actual != wanted:
            raise AlphaRuntimeError(f"package-selected runtime 完整性失败：{rel} expected={wanted} actual={actual}")
        return data

    def _verified_text(self, rel: str) -> str:
        try:
            return self._verified_bytes(rel).decode("utf-8")
        except UnicodeDecodeError as exc:
            raise AlphaRuntimeError(f"package-selected runtime 不是 UTF-8：{rel}") from exc

    @staticmethod
    def _evaluate(client: CdpClient, target_id: str, expression: str, *, await_promise: bool = False, timeout: float = 12.0) -> Any:
        session = client.attach(target_id)
        try:
            session.request("Runtime.enable")
            return session.evaluate(expression, await_promise=await_promise, timeout=timeout)
        finally:
            session.close()

    def _page_install(self, client: CdpClient, page_id: str, pair_nonce: str) -> dict[str, Any]:
        page_sources = [(rel, self._verified_text(rel)) for rel in PAGE_SOURCES]
        bootstrap_rel, bootstrap = page_sources[0]
        cleanup = """(()=>{try{window.WOFALPHAHUD?.dispose?.();}catch(_){}try{window.__WOF_ALPHA_TRANSPORT_V1?.reset?.();}catch(_){}for(const k of ['__WOF_ALPHA_BOOTSTRAP_RC5','__WOF_ALPHA_BOOTSTRAP_RC3','__WOF_ALPHA_TRANSPORT_V1','__WOF_ALPHA_CONFIG','WOFALPHA']){try{delete window[k];}catch(_){}}return true;})()"""
        self._evaluate(client, page_id, cleanup)
        try:
            self._evaluate(client, page_id, f"(0,eval)({json.dumps(bootstrap)}); true")
        except Exception as exc:
            raise AlphaRuntimeError(f"package-selected Alpha page source injection failed: {bootstrap_rel}: {exc}") from exc
        base = self._evaluate(client, page_id, "(()=>{const s=window.__WOF_ALPHA_BOOTSTRAP_RC5,t=window.__WOF_ALPHA_TRANSPORT_V1;return {version:s?.version,session:s?.session,channel:s?.channel,transportVersion:t?.version,listenerReady:s?.listenerReady===true};})()")
        if not isinstance(base, dict) or base.get("listenerReady") is not True or base.get("transportVersion") != TRANSPORT:
            raise AlphaRuntimeError("package-selected Alpha bootstrap 未建立安全传输监听器")
        session, channel = base.get("session"), base.get("channel")
        if not isinstance(session, str) or len(session) != 32 or channel != "WOF_ALPHA_" + session:
            raise AlphaRuntimeError("package-selected Alpha bootstrap session/channel authority 无效")
        pair = self._evaluate(client, page_id, f"window.__WOF_ALPHA_TRANSPORT_V1.bind({json.dumps(pair_nonce)})")
        if not isinstance(pair, dict) or pair.get("bound") is not True or not isinstance(pair.get("pairGeneration"), int):
            raise AlphaRuntimeError("package-selected Alpha pair bind 失败")
        for rel, source in page_sources[1:]:
            try:
                self._evaluate(client, page_id, f"(0,eval)({json.dumps(source)}); true", timeout=15.0)
            except Exception as exc:
                raise AlphaRuntimeError(f"package-selected Alpha page source injection failed: {rel}: {exc}") from exc
        hud_state = self._evaluate(
            client,
            page_id,
            """(()=>{const s=window.__WOF_ALPHA_BOOTSTRAP_RC5,e=window.WOFAlphaCanonicalAnchorEnvelope,p=window.WOFAlphaCanonicalOverlayPlan,h=window.WOFALPHAHUD;const missing=[];if(!e)missing.push('window.WOFAlphaCanonicalAnchorEnvelope');if(!p)missing.push('window.WOFAlphaCanonicalOverlayPlan');if(!h)missing.push('window.WOFALPHAHUD');for(const name of ['bindCanonicalOverlayAuthority','ingestCanonicalAnchorEnvelope','clearCanonicalOverlayAuthority','status'])if(typeof h?.[name]!=='function')missing.push('window.WOFALPHAHUD.'+name);const hudStatus=typeof h?.status==='function'?h.status():null;if(s)s.hudLoaded=!!h;return {hudLoaded:!!h,transport:s?.attachState||null,missingCanonical:missing,hudStatus};})()""",
        )
        if not isinstance(hud_state, dict) or hud_state.get("hudLoaded") is not True:
            raise AlphaRuntimeError("package-selected Alpha HUD 未挂接")
        missing = hud_state.get("missingCanonical")
        if not isinstance(missing, list):
            raise AlphaRuntimeError("package-selected Alpha canonical HUD capability probe 无效")
        if missing:
            raise AlphaRuntimeError("package-selected Alpha canonical HUD capability 缺失: " + ", ".join(str(item) for item in missing))
        hud_status = hud_state.get("hudStatus")
        if not isinstance(hud_status, dict):
            raise AlphaRuntimeError("package-selected Alpha canonical HUD status API 返回无效")
        canonical_status = hud_status.get("canonicalOverlay")
        if not isinstance(canonical_status, dict) or canonical_status.get("bound") is not False:
            raise AlphaRuntimeError("package-selected Alpha canonical HUD 初始未绑定状态无效")
        return {
            "session": session,
            "channel": channel,
            "pairGeneration": pair["pairGeneration"],
            "pairNonce": pair_nonce,
            "canonicalOverlayCapable": True,
            "canonicalOverlayStatus": canonical_status,
        }

    def _profiles_for_worker(self) -> dict[str, dict[str, Any]]:
        live = self._projection.profiles()
        if live is not None:
            return live
        return {name: json.loads(self._verified_text(rel)) for name, rel in PROFILE_PATHS.items()}

    def _worker_install(self, client: CdpClient, worker_id: str, pair: dict[str, Any], identity: dict[str, Any], runtime_epoch: str) -> dict[str, Any]:
        locator = identity.get("locator")
        if not isinstance(locator, dict) or not isinstance(locator.get("heapBase"), int) or not isinstance(locator.get("swap16"), bool):
            raise AlphaRuntimeError("accepted World identity 缺少唯一 launcher locator")
        if identity.get("sha256") != WORLD_SHA256 or identity.get("ok") is not True:
            raise AlphaRuntimeError("accepted World identity SHA authority 无效")
        profiles = self._profiles_for_worker()
        core, labels, player_warning, adapter = (self._verified_text(p) for p in WORKER_SOURCES)
        self._evaluate(client, worker_id, "try{self.__WOF_ALPHA_REAL_TRANSPORT?.stop?.('field-rebind')}catch(_){}; true")
        for source in (core, labels, player_warning):
            self._evaluate(client, worker_id, f"(0,eval)({json.dumps(source)}); true", timeout=15.0)
        self._evaluate(client, worker_id, f"self.__WOF_ALPHA_FIELD_PROFILES={json.dumps(profiles, ensure_ascii=False)}; true")
        self._evaluate(client, worker_id, f"(0,eval)({json.dumps(adapter)}); true", timeout=15.0)
        binding = {
            "release": RELEASE,
            "schema": SCHEMA,
            "transportVersion": TRANSPORT,
            "session": pair["session"],
            "channel": pair["channel"],
            "pairGeneration": pair["pairGeneration"],
            "pairNonce": pair["pairNonce"],
            "runtimeEpoch": runtime_epoch,
            "launcherIdentitySha": WORLD_SHA256,
            "launcherLocator": {"heapBase": locator["heapBase"], "swap16": locator["swap16"]},
        }
        status = self._evaluate(client, worker_id, f"self.WOFAlphaFieldAdapter.install(self,{json.dumps(binding)})", await_promise=True, timeout=30.0)
        if not isinstance(status, dict) or status.get("running") is not True or status.get("readOnly") is not True or status.get("ramWrites") != 0 or status.get("inputInjection") is not False:
            raise AlphaRuntimeError("package-selected Alpha field adapter 未进入安全 running 状态")
        local_identity = status.get("identity")
        if not isinstance(local_identity, dict) or local_identity.get("sha256") != WORLD_SHA256 or local_identity.get("ok") is not True:
            raise AlphaRuntimeError("package-selected Alpha field adapter detector-local identity 未通过")
        return status

    def ensure_running(self, client: CdpClient, choice: TargetChoice, authority_key: str) -> dict[str, Any]:
        if self._authority_key == authority_key and self._status.get("running") is True:
            return dict(self._status)
        self.revoke(client)
        if not choice.page or not choice.worker or not choice.identity or choice.identity.get("ok") is not True:
            raise AlphaRuntimeError("没有可激活 Alpha 的 accepted authority")
        page_id = str(choice.page.get("targetId") or "")
        worker_id = str(choice.worker.get("targetId") or "")
        if not page_id or not worker_id:
            raise AlphaRuntimeError("accepted authority 缺少 page/Worker target")
        pair_nonce, runtime_epoch = secrets.token_hex(16), secrets.token_hex(16)
        try:
            pair = self._page_install(client, page_id, pair_nonce)
            worker_status = self._worker_install(client, worker_id, pair, choice.identity, runtime_epoch)
            page_status = self._evaluate(client, page_id, "(()=>({attachState:window.__WOF_ALPHA_BOOTSTRAP_RC5?.attachState||null,hudLoaded:!!window.WOFALPHAHUD,hudStatus:window.WOFALPHAHUD?.status?.()||null}))()")
            if not isinstance(page_status, dict):
                raise AlphaRuntimeError("package-selected Alpha page status 无效")
            page_status["canonicalOverlayCapable"] = pair["canonicalOverlayCapable"]
            page_status["canonicalOverlayStatus"] = pair["canonicalOverlayStatus"]
            projection_status = self._projection.status()
            if self._projection.profiles() is None:
                projection_status = self._projection.ensure_started(client, choice, authority_key)
        except Exception:
            self._page_target_id, self._worker_target_id = page_id, worker_id
            self.revoke(client)
            raise
        self._authority_key = authority_key
        self._page_target_id, self._worker_target_id = page_id, worker_id
        self._status = {
            "requested": True,
            "running": True,
            "runtimeEpoch": runtime_epoch,
            "authorityKey": authority_key,
            "packageVersion": self._load_manifest().get("packageVersion"),
            "page": page_status,
            "worker": worker_status,
            "projectionRecovery": projection_status,
            "projectionProfilesLive": self._projection.profiles() is not None,
            **SAFETY,
        }
        return dict(self._status)

    def poll_projection_recovery(self, client: CdpClient, choice: TargetChoice, authority_key: str) -> tuple[dict[str, Any], bool]:
        try:
            recovery = self._projection.poll(client, authority_key)
        except (ProjectionRecoveryError, CdpError, OSError, ValueError) as exc:
            recovery = {"state": "ERROR", "error": str(exc), **SAFETY}
        activated = recovery.get("newProfiles") is True
        if activated:
            # Rebind through the normal exact-authority path. No profile mutation is
            # injected into the already-running transport in place.
            self.revoke(client)
            return recovery, True
        if self._status.get("running") is True:
            self._status["projectionRecovery"] = recovery
            self._status["projectionProfilesLive"] = self._projection.profiles() is not None
        return recovery, False

    def projection_proof_result(self) -> dict[str, Any] | None:
        return self._projection.proof_result()

    def revoke(self, client: CdpClient | None = None) -> None:
        self._projection.stop_runtime(client, preserve_state=True)
        if client and self._worker_target_id:
            try:
                self._evaluate(client, self._worker_target_id, "(()=>{try{return self.__WOF_ALPHA_REAL_TRANSPORT?.stop?.('authority-revoked')!==false}catch(_){return false}})()")
            except Exception:
                pass
        if client and self._page_target_id:
            try:
                self._evaluate(client, self._page_target_id, "(()=>{try{window.__WOF_ALPHA_TRANSPORT_V1?.reset?.()}catch(_){}try{window.WOFALPHAHUD?.transportReset?.()}catch(_){}return true})()")
            except Exception:
                pass
        self._authority_key = None
        self._page_target_id = None
        self._worker_target_id = None
        self._status = {"requested": True, "running": False, "projectionRecovery": self._projection.status(), "projectionProfilesLive": self._projection.profiles() is not None, **SAFETY}

    def status(self) -> dict[str, Any]:
        return dict(self._status)
