from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SETUP = (ROOT / "WOF_ALPHA_SETUP_ONCE.cmd").read_text(encoding="utf-8")
ENTRY = (ROOT / "WOF_ALPHA_TEST.cmd").read_text(encoding="utf-8")
INSTALLER = (ROOT / "parallel/PYLAUNCH/install_live_retest_once.ps1").read_text(encoding="utf-8")
LOOP = (ROOT / "parallel/PYLAUNCH/owner_live_retest_loop.ps1").read_text(encoding="utf-8")


def test_zero_state_setup_bootstraps_repo_over_ssh22_before_using_repo_installer():
    lower = SETUP.lower()
    assert "git@github.com:ouyong520/wof-ai-private.git" in SETUP
    assert " -p 22" in SETUP
    assert " clone " in lower
    assert '--branch "%LIVE_BRANCH%"' in SETUP
    assert lower.index(" clone ") < lower.index("install_live_retest_once.ps1")
    assert "managed alpha repo was not found" not in lower
    assert "https://github.com/ouyong520/wof-ai-private.git" not in lower


def test_setup_preserves_unrelated_ssh_material_and_reuses_dedicated_alpha_key():
    assert r"%USERPROFILE%\.ssh" in SETUP
    assert "wof_alpha_github_ed25519" in SETUP
    assert 'if not exist "%KEY%" (' in SETUP
    assert 'rmdir /s /q "%KEYDIR%"' not in SETUP
    assert 'del /q "%KEY%"' not in SETUP
    assert "It was NOT overwritten" in SETUP


def test_installer_preserves_ssh_config_outside_bounded_alpha_block():
    assert "# WOF_ALPHA_BEGIN" in INSTALLER
    assert "# WOF_ALPHA_END" in INSTALLER
    assert "HostName github.com" in INSTALLER
    assert "Port 22" in INSTALLER
    assert "IdentityFile $keyForward" in INSTALLER
    assert "Remove-Item" not in INSTALLER or ".ssh" not in INSTALLER.split("Remove-Item", 1)[-1]


def test_live_updates_follow_controlled_alpha_live_not_main():
    assert "refs/heads/alpha-live:refs/remotes/origin/alpha-live" in LOOP
    assert "$RemoteRef = 'origin/alpha-live'" in LOOP
    assert "origin/main" not in LOOP
    assert "refs/heads/main" not in LOOP
    assert "Unrelated main/docs commits do not restart Alpha." in LOOP


def test_update_restarts_alpha_runtime_only_and_keeps_browser_out_of_stop_filter():
    start = LOOP.index("function Stop-AlphaRuntime")
    end = LOOP.index("function Ensure-PythonEnvironment")
    stop_block = LOOP[start:end].lower()
    assert "render_authority_measurement_entry.py" in stop_block
    assert "chrome" not in stop_block
    assert "msedge" not in stop_block
    assert "taskkill" not in stop_block
    assert "stop-process" in stop_block


def test_updater_self_update_is_restart_safe_and_release_is_validated_before_reset():
    assert "function Restart-SelfIfChanged" in LOOP
    assert "$script:Mutex.ReleaseMutex()" in LOOP
    assert "Start-Process -FilePath 'powershell.exe'" in LOOP
    assert "function Release-HasRequiredFiles" in LOOP
    assert "cat-file -e" in LOOP
    assert "restored prior commit" in LOOP


def test_one_permanent_desktop_entry_and_obvious_latest_feedback_path():
    assert "Desktop\\WOF_ALPHA_TEST.cmd" in SETUP
    assert "$DesktopEntry = Join-Path $Desktop 'WOF_ALPHA_TEST.cmd'" in INSTALLER
    assert "WOF_ALPHA_RUN_V5" not in INSTALLER
    assert "LATEST_ALPHA_FEEDBACK.txt" in LOOP
    assert "Documents\\WOF_RESULTS\\LATEST_ALPHA_FEEDBACK.txt" in INSTALLER
    assert "owner_live_retest_loop.ps1" in ENTRY
