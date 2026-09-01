from __future__ import annotations

import json
import queue
import threading
from dataclasses import dataclass
from typing import Any

import websocket


READ_ONLY_METHODS = {
    "Target.getTargets",
    "Target.attachToTarget",
    "Target.detachFromTarget",
    "Runtime.enable",
    "Runtime.evaluate",
}


class CdpError(RuntimeError):
    pass


class CdpClient:
    """Tiny browser-level CDP client with an explicit foundation-stage method allowlist."""

    def __init__(self, websocket_url: str, timeout: float = 5.0) -> None:
        self.websocket_url = websocket_url
        self.timeout = timeout
        self._ws: websocket.WebSocket | None = None
        self._rx_thread: threading.Thread | None = None
        self._next_id = 1
        self._id_lock = threading.Lock()
        self._pending: dict[int, queue.Queue[dict[str, Any]]] = {}
        self._pending_lock = threading.Lock()
        self._closed = threading.Event()

    def connect(self) -> None:
        if self._ws is not None:
            return
        self._ws = websocket.create_connection(self.websocket_url, timeout=self.timeout, suppress_origin=True)
        self._ws.settimeout(1.0)
        self._closed.clear()
        self._rx_thread = threading.Thread(target=self._receiver, name="wof-cdp-rx", daemon=True)
        self._rx_thread.start()

    def close(self) -> None:
        self._closed.set()
        ws, self._ws = self._ws, None
        if ws is not None:
            try:
                ws.close()
            except Exception:
                pass
        with self._pending_lock:
            pending = list(self._pending.values())
            self._pending.clear()
        for q in pending:
            q.put({"error": {"message": "CDP connection closed"}})

    def _receiver(self) -> None:
        assert self._ws is not None
        while not self._closed.is_set():
            try:
                raw = self._ws.recv()
            except websocket.WebSocketTimeoutException:
                continue
            except Exception:
                break
            if not raw:
                break
            try:
                message = json.loads(raw)
            except ValueError:
                continue
            message_id = message.get("id")
            if isinstance(message_id, int):
                with self._pending_lock:
                    q = self._pending.pop(message_id, None)
                if q is not None:
                    q.put(message)
        self._closed.set()

    def request(
        self,
        method: str,
        params: dict[str, Any] | None = None,
        *,
        session_id: str | None = None,
        timeout: float | None = None,
    ) -> dict[str, Any]:
        if method not in READ_ONLY_METHODS:
            raise CdpError(f"foundation read-only policy blocks CDP method: {method}")
        if self._ws is None or self._closed.is_set():
            raise CdpError("CDP is not connected")
        with self._id_lock:
            message_id = self._next_id
            self._next_id += 1
        q: queue.Queue[dict[str, Any]] = queue.Queue(maxsize=1)
        with self._pending_lock:
            self._pending[message_id] = q
        payload: dict[str, Any] = {"id": message_id, "method": method, "params": params or {}}
        if session_id:
            payload["sessionId"] = session_id
        try:
            self._ws.send(json.dumps(payload, separators=(",", ":")))
            response = q.get(timeout=timeout or self.timeout)
        except Exception as exc:
            with self._pending_lock:
                self._pending.pop(message_id, None)
            raise CdpError(f"CDP request failed for {method}: {exc}") from exc
        if "error" in response:
            raise CdpError(f"CDP {method}: {response['error']}")
        result = response.get("result")
        if not isinstance(result, dict):
            raise CdpError(f"CDP {method}: malformed result")
        return result

    def attach(self, target_id: str) -> "CdpSession":
        result = self.request("Target.attachToTarget", {"targetId": target_id, "flatten": True})
        session_id = result.get("sessionId")
        if not isinstance(session_id, str):
            raise CdpError("Target.attachToTarget returned no sessionId")
        return CdpSession(self, target_id, session_id)


@dataclass
class CdpSession:
    client: CdpClient
    target_id: str
    session_id: str

    def request(self, method: str, params: dict[str, Any] | None = None, timeout: float | None = None) -> dict[str, Any]:
        return self.client.request(method, params, session_id=self.session_id, timeout=timeout)

    def evaluate(self, expression: str, *, await_promise: bool = False, timeout: float = 8.0) -> Any:
        result = self.request(
            "Runtime.evaluate",
            {
                "expression": expression,
                "returnByValue": True,
                "awaitPromise": await_promise,
                "silent": True,
            },
            timeout=timeout,
        )
        if result.get("exceptionDetails"):
            raise CdpError(f"Runtime.evaluate exception: {result['exceptionDetails']}")
        remote = result.get("result") or {}
        if "value" in remote:
            return remote["value"]
        if remote.get("subtype") == "null":
            return None
        raise CdpError(f"Runtime.evaluate did not return by value: {remote}")

    def close(self) -> None:
        try:
            self.client.request("Target.detachFromTarget", {"sessionId": self.session_id})
        except Exception:
            pass
