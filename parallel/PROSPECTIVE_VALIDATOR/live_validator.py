from __future__ import annotations

# Compatibility boundary:
# - imported as `live_validator`: expose the preserved framework/live core so
#   live_validator_v2 can reuse its manifest/probe/evidence machinery unchanged;
# - executed directly: enter Discovery V2, never the legacy Worker URL/type path.
if __name__ == "live_validator":
    from live_validator_core import *  # noqa: F401,F403
else:
    from live_validator_v2 import main

    raise SystemExit(main())
