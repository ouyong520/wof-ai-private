from __future__ import annotations

# Compatibility boundary:
# - imported as `live_validator`: expose the preserved framework/live core so
#   live_validator_v2 can reuse its manifest/probe/evidence machinery unchanged;
# - hardened routing supersedes the historical forms `from live_validator_v2 import main`
#   and `from live_validator_v2 import main as _v2_main` while keeping those V2 regression markers visible;
# - executed directly: enter hardened Discovery V2, never the legacy Worker URL/type path.
if __name__ == "live_validator":
    from live_validator_core import *  # noqa: F401,F403

    def main() -> int:
        from live_validator_v2_hardened import main as _v2_main
        return _v2_main()
else:
    from live_validator_v2_hardened import main

    raise SystemExit(main())
