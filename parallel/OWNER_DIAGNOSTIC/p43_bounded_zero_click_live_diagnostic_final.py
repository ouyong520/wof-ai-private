from __future__ import annotations

from typing import Any, Mapping, Sequence

import p43_bounded_zero_click_live_diagnostic as core
import p43_bounded_zero_click_live_diagnostic_entry as integrated


def _preflight_before_p42(args: Any) -> tuple[bool, str | None]:
    try:
        git = core.GitReader(args.repo_root)
        binding = core.verify_candidate_binding(
            git,
            metadata_commit=args.metadata_commit,
            source_commit=args.source_commit,
            pointer_path=args.pointer,
            provenance_path=args.provenance,
        )
        core.verify_source_checkout(args.source_checkout, args.source_commit)
        core.verify_dedicated_python()
        if binding.get("state") != "PASS":
            return False, "CANDIDATE_BINDING_NOT_PASS"
        return True, None
    except Exception as exc:
        return False, f"{type(exc).__name__}: {exc}"


def run(args: Any) -> tuple[dict[str, Any], int, dict[str, Any]]:
    preflight_ok, preflight_reason = _preflight_before_p42(args)
    if preflight_ok:
        p42_start = integrated._start_p42(args)
    else:
        p42_start = {
            "state": "P42_CORRELATION_PROBE_NOT_PRESENT",
            "present": False,
            "reason": f"P43_PREFLIGHT_DID_NOT_PASS:{preflight_reason}",
            "testedCommit": integrated.P42_TESTED_COMMIT,
            "testedBlob": integrated.P42_TESTED_BLOB,
        }

    receipt, rc = core.run_live_diagnostic(args)
    bound_raw: dict[str, Any] = {}
    try:
        bound_raw = integrated._raw_binding_artifacts(args, receipt.get("candidateBinding") or {})
    except Exception as exc:
        receipt.setdefault("errors", []).append({
            "atUtc": core.utc_now(),
            "where": "CANDIDATE_BINDING_RAW_ARCHIVE",
            "type": type(exc).__name__,
            "message": str(exc),
            "repr": repr(exc),
        })

    page_target = (receipt.get("authoritativeAssociation") or {}).get("pageTargetId")
    if not page_target:
        identity, _ = integrated._p16_binding(args)
        page_target = identity.get("pageTargetId") if identity else None
    p42_final = integrated._stop_p42(args, page_target) if p42_start.get("present") is True else dict(p42_start)
    stable = integrated._stable_receipts(args, receipt, p42_start, p42_final, bound_raw)
    return receipt, rc, stable


def main(argv: Sequence[str] | None = None) -> int:
    args = core._parser().parse_args(argv)
    if not (0.1 <= args.duration <= 60.0):
        raise SystemExit("--duration must be in [0.1, 60] seconds")
    receipt, rc, stable = run(args)
    first = receipt.get("firstFailingGate")
    print(f"receipt={stable.get('receiptPath')}")
    print(f"receiptSha256={stable.get('receiptSha256')}")
    print(f"humanReceipt={stable.get('humanReceiptPath')}")
    print(f"humanReceiptSha256={stable.get('humanReceiptSha256')}")
    print(f"firstFailingGate={first.get('gate') if isinstance(first, Mapping) else 'NONE'}")
    print("passedBeforeFirstFailure=" + ",".join(receipt.get("passedBeforeFirstFailure") or []))
    print(f"p42={((receipt.get('p42') or {}).get('state'))}")
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
