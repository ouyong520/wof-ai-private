from __future__ import annotations

import argparse
import json
from pathlib import Path

from validator import ValidationError, load_json, make_session, validate_manifest


def main() -> int:
    ap = argparse.ArgumentParser(description="冻结 WOF 候选规则，开始新的 prospective evidence session")
    ap.add_argument("manifest", help="候选 manifest JSON")
    ap.add_argument("--output", default="prospective_session.json", help="session JSON 输出路径")
    args = ap.parse_args()
    try:
        manifest = validate_manifest(load_json(args.manifest))
        session = make_session(manifest)
    except (OSError, json.JSONDecodeError, ValidationError) as exc:
        print(f"无法开始前瞻验证：{exc}")
        return 2
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(session, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"候选已冻结：{manifest['id']}")
    print(f"session：{out}")
    print("从现在之后新启动的房间/采集才可计入 prospective；旧 corpus 仍只算 discovery。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
