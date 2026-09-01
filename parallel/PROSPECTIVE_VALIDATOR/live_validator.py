from __future__ import annotations

# Compatibility boundary:
# - imported as `live_validator`: expose the preserved framework/live core so
#   live_validator_v2 can reuse its manifest/probe/evidence machinery unchanged;
# - any caller that invokes `live_validator.main()` is lazily routed to V2;
# - executed directly: enter Discovery V2, never the legacy Worker URL/type path.
if __name__ == "live_validator":
    from live_validator_core import *  # noqa: F401,F403

    def main() -> int:
        from live_validator_v2 import main as _v2_main
        return _v2_main()
else:
    from live_validator_v2 import main

    raise SystemExit(main())
