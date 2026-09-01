from __future__ import annotations

import discovery_v2_sync
import hardening_v2
import recorder

discovery_v2_sync.install(recorder)
hardening_v2.install(recorder, discovery_v2_sync)

import owner_zh_cn


if __name__ == "__main__":
    raise SystemExit(owner_zh_cn.main())
