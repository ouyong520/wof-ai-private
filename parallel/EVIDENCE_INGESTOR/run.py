from __future__ import annotations

"""Current-repository compatibility entry for Evidence Auto-Ingestor."""

import ingestor as core

_BASE_CLASSIFY = core.classify


def classify_current(payload, rel):
    toolkit_version = payload.get("toolkit")
    if isinstance(toolkit_version, str) and toolkit_version.startswith("wof-windows-operator-toolkit-v"):
        core.KNOWN_VERSIONS.add(toolkit_version)
        schema = payload.get("schema") if isinstance(payload.get("schema"), str) else None
        if isinstance(payload.get("checks"), list) and "overall" in payload:
            return "Regression", "REGRESSION_SUMMARY", schema, toolkit_version
        if isinstance(payload.get("components"), dict) and "platform" in payload:
            return "Diagnostics", "DIAGNOSTICS_SUMMARY", schema, toolkit_version
        if "included" in payload and "created" in payload:
            return "Toolkit", "PACKAGE_MANIFEST", schema, toolkit_version
    return _BASE_CLASSIFY(payload, rel)


core.classify = classify_current


def main(argv=None):
    return core.main(argv)


if __name__ == "__main__":
    raise SystemExit(main())
