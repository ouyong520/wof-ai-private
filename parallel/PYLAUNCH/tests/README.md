Run offline foundation tests from `parallel/PYLAUNCH`:

```bat
.venv\Scripts\python -m unittest discover -s tests -v
```

Tests cover Worker URL filtering, exact supported-worker uniqueness / ambiguity fail-closed behavior, and the CDP method allowlist blocking gameplay input injection.
