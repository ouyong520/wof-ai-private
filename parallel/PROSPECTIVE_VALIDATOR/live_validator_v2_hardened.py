from __future__ import annotations

import live_validator_v2 as v2
from discovery_v2_hardening import install_live_hardening

install_live_hardening(v2)


def main() -> int:
    return v2.main()


if __name__ == "__main__":
    raise SystemExit(main())
