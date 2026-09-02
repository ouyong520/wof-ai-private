#!/usr/bin/env python3
from __future__ import annotations

import sys

import acceptance_orchestrator as legacy
from repository_preflight_current import preflight_only_success_message, release_gate


def main() -> int:
    # Preserve the bounded Browser/WOF acceptance implementation; replace only
    # its historical repository-gate selector with the current composed policy.
    legacy.release_gate = release_gate
    rc = legacy.main()
    if rc == 0 and "--preflight-only" in sys.argv:
        print(preflight_only_success_message())
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
