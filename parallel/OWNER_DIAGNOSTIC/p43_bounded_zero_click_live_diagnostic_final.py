from __future__ import annotations

from typing import Mapping, Sequence

import p43_bounded_zero_click_live_diagnostic as core
import p43_post_p45_p46_continuation as continuation


def run(args):
    return continuation.run(args)


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
    print(f"p45={((receipt.get('p45') or {}).get('internalState'))}")
    print(f"p42={((receipt.get('p42') or {}).get('state'))}")
    print(f"p46={((receipt.get('p46') or {}).get('state'))}")
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
