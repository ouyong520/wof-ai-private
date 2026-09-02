@echo off
setlocal
chcp 65001 >nul 2>nul
cd /d "%~dp0\..\.."
set "WOF_PYTHON_FOUND="

where py >nul 2>nul
if errorlevel 1 goto :try_python
set "WOF_PYTHON_FOUND=1"
py -3 -c "import sys; raise SystemExit(0 if (3, 10) ^<= sys.version_info[:2] ^<= (3, 14) else 1)" >nul 2>nul
if errorlevel 1 goto :try_python
py -3 -m training.farm.beginner_real_wof_launcher %*
set "WOF_BEGINNER_RC=%ERRORLEVEL%"
goto :done

:try_python
where python >nul 2>nul
if errorlevel 1 goto :python_unavailable
set "WOF_PYTHON_FOUND=1"
python -c "import sys; raise SystemExit(0 if (3, 10) ^<= sys.version_info[:2] ^<= (3, 14) else 1)" >nul 2>nul
if errorlevel 1 goto :python_unavailable
python -m training.farm.beginner_real_wof_launcher %*
set "WOF_BEGINNER_RC=%ERRORLEVEL%"
goto :done

:python_unavailable
echo ========================================================================
echo Training Farm R0.4 小白实机证明 / Beginner Real-WOF Proof
echo ========================================================================
if defined WOF_PYTHON_FOUND goto :python_unsupported
echo WAITING_PREREQUISITE - 未找到 Python / Python launcher not found.
echo 请先安装当前 Training Farm 支持的 Python 3.10..3.14，然后重新双击本文件。
goto :python_help_done

:python_unsupported
echo WAITING_PREREQUISITE - 当前 Python 版本不受支持 / unsupported Python version.
echo 严格要求 Python 3.10..3.14；请安装受支持版本后重新双击本文件。

:python_help_done
echo 本 launcher 不会自动下载 ROM、BIOS 或专有游戏资源。
set "WOF_BEGINNER_RC=2"

:done
echo.
if not defined WOF_BEGINNER_NO_PAUSE pause
exit /b %WOF_BEGINNER_RC%
