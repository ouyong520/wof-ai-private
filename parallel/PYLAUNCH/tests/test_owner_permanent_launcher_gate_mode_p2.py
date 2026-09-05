from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
LOOP = (ROOT / "parallel/PYLAUNCH/owner_live_retest_loop.ps1").read_text(encoding="utf-8")
MARKER = (ROOT / "parallel/PYLAUNCH/alpha_live_mode.txt").read_text(encoding="utf-8")
SETUP = (ROOT / "WOF_ALPHA_SETUP_ONCE.cmd").read_text(encoding="utf-8")
ENTRY = (ROOT / "WOF_ALPHA_TEST.cmd").read_text(encoding="utf-8")


def _block(start_name: str, end_name: str) -> str:
    start = LOOP.index(start_name)
    end = LOOP.index(end_name, start)
    return LOOP[start:end]


def test_first_owner_candidate_marker_is_repo_controlled_fixed_draw_gate():
    assert MARKER == "fixed-draw-first-gate\n"
    assert "$LiveModeMarker = Join-Path $Repo 'parallel\\PYLAUNCH\\alpha_live_mode.txt'" in LOOP


def test_live_mode_parser_accepts_only_normal_or_fixed_draw_first_gate():
    block = _block("function Resolve-AlphaLiveMode", "function Write-LatestFeedback")
    assert "switch -CaseSensitive ($requestedMode)" in block
    assert "'normal' {" in block
    assert "'fixed-draw-first-gate' {" in block
    assert "$markerLines.Count -ne 1" in block
    assert "$requestedMode -ne $requestedMode.Trim()" in block


def test_unknown_missing_or_malformed_mode_fails_closed_to_normal():
    block = _block("function Resolve-AlphaLiveMode", "function Write-LatestFeedback")
    assert block.count("$script:LiveMode = 'normal'") >= 3
    assert "fail-closed: live-mode marker missing" in block
    assert "fail-closed: live-mode marker unreadable" in block
    assert "fail-closed: live-mode marker must contain exactly one line" in block
    assert "fail-closed: unsupported live-mode marker" in block
    default = block[block.index("default {"):]
    assert "WOF_ALPHA_FIXED_DRAW_SMOKE = '1'" not in default


def test_fixed_draw_mode_sets_smoke_only_for_child_launch_and_restores_controller_env():
    block = _block("function Start-AlphaRuntime", "function Fetch-Latest")
    set_pos = block.index("$env:WOF_ALPHA_FIXED_DRAW_SMOKE = '1'")
    launch_pos = block.index("Start-Process -FilePath $script:Py")
    finally_pos = block.index("} finally {")
    restore_pos = block.index("$env:WOF_ALPHA_FIXED_DRAW_SMOKE = $previousSmokeFlag")
    assert set_pos < launch_pos < finally_pos < restore_pos
    assert "$hadSmokeFlag = Test-Path Env:WOF_ALPHA_FIXED_DRAW_SMOKE" in block
    assert "Remove-Item Env:WOF_ALPHA_FIXED_DRAW_SMOKE -ErrorAction SilentlyContinue" in block


def test_normal_mode_does_not_leak_smoke_flag_into_alpha_runtime():
    block = _block("function Start-AlphaRuntime", "function Fetch-Latest")
    fixed = block.index("if ($script:LiveMode -eq 'fixed-draw-first-gate')")
    otherwise = block.index("} else {", fixed)
    remove = block.index("Remove-Item Env:WOF_ALPHA_FIXED_DRAW_SMOKE -ErrorAction SilentlyContinue", otherwise)
    launch = block.index("Start-Process -FilePath $script:Py")
    assert otherwise < remove < launch


def test_every_alpha_runtime_restart_re_resolves_marker_so_future_normal_auto_restores():
    start_block = _block("function Start-AlphaRuntime", "function Fetch-Latest")
    apply_block = _block("function Apply-LiveRelease", "$createdNew = $false")
    assert "Resolve-AlphaLiveMode" in start_block
    assert "Start-AlphaRuntime $TargetSha" in apply_block
    assert "Start-AlphaRuntime $PreviousSha" in apply_block


def test_status_surface_exposes_current_sha_and_current_live_mode():
    block = _block("function Write-LatestFeedback", "function Stop-AlphaRuntime")
    assert "('currentSha=' + $Sha)" in block
    assert "('liveMode=' + $script:LiveMode)" in block
    assert "('liveModeReason=' + $script:LiveModeReason)" in block


def test_w1_zero_state_ssh22_and_key_preservation_contract_remains_present():
    lower = SETUP.lower()
    assert "git@github.com:ouyong520/wof-ai-private.git" in SETUP
    assert " -p 22" in SETUP
    assert " clone " in lower
    assert '--branch "%LIVE_BRANCH%"' in SETUP
    assert r"%USERPROFILE%\.ssh" in SETUP
    assert 'if not exist "%KEY%" (' in SETUP
    assert 'rmdir /s /q "%KEYDIR%"' not in SETUP
    assert "https://github.com/ouyong520/wof-ai-private.git" not in lower


def test_alpha_live_ssh22_browser_preservation_and_single_permanent_entry_remain():
    assert "$Remote = 'git@wof-alpha-github:ouyong520/wof-ai-private.git'" in LOOP
    assert "refs/heads/alpha-live:refs/remotes/origin/alpha-live" in LOOP
    assert "origin/main" not in LOOP
    stop_block = _block("function Stop-AlphaRuntime", "function Ensure-PythonEnvironment").lower()
    assert "render_authority_measurement_entry.py" in stop_block
    assert "chrome" not in stop_block
    assert "taskkill" not in stop_block
    assert "owner_live_retest_loop.ps1" in ENTRY
    assert "WOF_ALPHA_TEST" in ENTRY
    assert "WOF_ALPHA_RUN_V" not in ENTRY
