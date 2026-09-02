@echo off
setlocal
chcp 65001 >nul 2>nul
set "PYTHONUTF8=1"
set "PYTHONIOENCODING=utf-8"
cd /d "%~dp0\..\.."
for %%I in (".") do set "WOF_REPO_ROOT=%%~fI"

if defined WOF_TRAINING_FARM_LOCAL_ROOT (
  set "WOF_LOCAL_ROOT=%WOF_TRAINING_FARM_LOCAL_ROOT%"
) else (
  for %%I in ("%WOF_REPO_ROOT%\..") do set "WOF_LOCAL_ROOT=%%~fI"
)
set "WOF_VENV_PY=%WOF_LOCAL_ROOT%\.venv\Scripts\python.exe"

if defined WOF_BOOTSTRAP_PYTHON (
  "%WOF_BOOTSTRAP_PYTHON%" -c "import sys; raise SystemExit(0 if sys.version_info[0] == 3 and 10 ^<= sys.version_info[1] ^<= 14 else 1)" >nul 2>nul
  if not errorlevel 1 (
    "%WOF_BOOTSTRAP_PYTHON%" -m training.farm.windows_oneclick_bootstrap %*
    set "WOF_BOOTSTRAP_RC=%ERRORLEVEL%"
    goto :done
  )
)

if exist "%WOF_VENV_PY%" (
  "%WOF_VENV_PY%" -c "import sys; raise SystemExit(0 if sys.version_info[0] == 3 and 10 ^<= sys.version_info[1] ^<= 14 else 1)" >nul 2>nul
  if not errorlevel 1 (
    "%WOF_VENV_PY%" -m training.farm.windows_oneclick_bootstrap %*
    set "WOF_BOOTSTRAP_RC=%ERRORLEVEL%"
    goto :done
  )
)

where py >nul 2>nul
if not errorlevel 1 (
  py -3.14 -c "import sys; raise SystemExit(0 if sys.version_info[0] == 3 and sys.version_info[1] == 14 else 1)" >nul 2>nul
  if not errorlevel 1 (
    py -3.14 -m training.farm.windows_oneclick_bootstrap %*
    set "WOF_BOOTSTRAP_RC=%ERRORLEVEL%"
    goto :done
  )
  py -3.13 -c "import sys; raise SystemExit(0 if sys.version_info[0] == 3 and sys.version_info[1] == 13 else 1)" >nul 2>nul
  if not errorlevel 1 (
    py -3.13 -m training.farm.windows_oneclick_bootstrap %*
    set "WOF_BOOTSTRAP_RC=%ERRORLEVEL%"
    goto :done
  )
  py -3.12 -c "import sys; raise SystemExit(0 if sys.version_info[0] == 3 and sys.version_info[1] == 12 else 1)" >nul 2>nul
  if not errorlevel 1 (
    py -3.12 -m training.farm.windows_oneclick_bootstrap %*
    set "WOF_BOOTSTRAP_RC=%ERRORLEVEL%"
    goto :done
  )
  py -3.11 -c "import sys; raise SystemExit(0 if sys.version_info[0] == 3 and sys.version_info[1] == 11 else 1)" >nul 2>nul
  if not errorlevel 1 (
    py -3.11 -m training.farm.windows_oneclick_bootstrap %*
    set "WOF_BOOTSTRAP_RC=%ERRORLEVEL%"
    goto :done
  )
  py -3.10 -c "import sys; raise SystemExit(0 if sys.version_info[0] == 3 and sys.version_info[1] == 10 else 1)" >nul 2>nul
  if not errorlevel 1 (
    py -3.10 -m training.farm.windows_oneclick_bootstrap %*
    set "WOF_BOOTSTRAP_RC=%ERRORLEVEL%"
    goto :done
  )
)

where python >nul 2>nul
if not errorlevel 1 (
  python -c "import sys; raise SystemExit(0 if sys.version_info[0] == 3 and 10 ^<= sys.version_info[1] ^<= 14 else 1)" >nul 2>nul
  if not errorlevel 1 (
    python -m training.farm.windows_oneclick_bootstrap %*
    set "WOF_BOOTSTRAP_RC=%ERRORLEVEL%"
    goto :done
  )
)

where python3 >nul 2>nul
if not errorlevel 1 (
  python3 -c "import sys; raise SystemExit(0 if sys.version_info[0] == 3 and 10 ^<= sys.version_info[1] ^<= 14 else 1)" >nul 2>nul
  if not errorlevel 1 (
    python3 -m training.farm.windows_oneclick_bootstrap %*
    set "WOF_BOOTSTRAP_RC=%ERRORLEVEL%"
    goto :done
  )
)

echo ========================================================================
echo Training Farm R0.4.6 Windows 一键环境准备
echo ========================================================================
echo WAITING_PREREQUISITE - 未找到受支持的 Python 3.10..3.14。
echo 请安装一个 Python 3.10、3.11、3.12、3.13 或 3.14 后重新双击本文件。
echo 不需要卸载现有 Python；本流程不会静默安装 Python，也不会下载 ROM/BIOS。
set "WOF_BOOTSTRAP_RC=2"

:done
echo.
if not defined WOF_BOOTSTRAP_NO_PAUSE pause
exit /b %WOF_BOOTSTRAP_RC%
