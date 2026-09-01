from __future__ import annotations

import hudanchor_proof as engine
from proof_policy import evaluate_trace


def main(argv=None) -> int:
    # The engine calls its module-global evaluator. Replace it with the stricter
    # fail-closed proof policy before entering any live CDP session.
    engine.evaluate_trace = evaluate_trace
    return engine.main(argv)


if __name__ == "__main__":
    raise SystemExit(main())
