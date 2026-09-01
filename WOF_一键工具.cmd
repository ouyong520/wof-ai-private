@echo off
setlocal EnableExtensions
chcp 65001 >nul 2>&1
title WOF 一键工具

rem CI/diagnostics may pin an exact bootstrap commit through WOF_BOOTSTRAP_URL.
rem Normal owner use stays on main, with a random query string to avoid stale Raw CDN cache.
if defined WOF_BOOTSTRAP_URL (
  set "BOOT_URL=%WOF_BOOTSTRAP_URL%"
) else (
  set "BOOT_URL=https://raw.githubusercontent.com/ouyong520/wof-ai-private/main/parallel/OWNER_ONECLICK/bootstrap_v2.ps1?cb=%RANDOM%_%RANDOM%"
)
set "BOOT_PS1=%TEMP%\WOF_owner_bootstrap_%RANDOM%_%RANDOM%.ps1"

echo.
echo ================================================
echo              WOF 一键工具
echo ================================================
echo 正在启动 WOF 工具安装/更新程序...

rem Windows PowerShell 5.1 treats UTF-8 .ps1 without BOM as the legacy ANSI code page.
rem Download as text, then write an explicit UTF-8 BOM so Chinese bootstrap source parses safely.
powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "$ErrorActionPreference='Stop'; [Net.ServicePointManager]::SecurityProtocol=[Net.SecurityProtocolType]::Tls12; $r=Invoke-WebRequest -UseBasicParsing -Uri '%BOOT_URL%' -TimeoutSec 45; $enc=New-Object System.Text.UTF8Encoding($true); [System.IO.File]::WriteAllText('%BOOT_PS1%', [string]$r.Content, $enc)"
if errorlevel 1 goto :download_fail

powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%BOOT_PS1%" %*
set "RC=%ERRORLEVEL%"
del /q "%BOOT_PS1%" >nul 2>&1
if not "%RC%"=="0" goto :run_fail
exit /b 0

:download_fail
echo.
echo 无法下载 WOF 更新程序，请检查网络后重新双击。
echo 已安装的旧版本不会被删除，游戏本身没有受到影响。
echo 下载地址：%BOOT_URL%
pause
exit /b 10

:run_fail
echo.
echo WOF 一键工具没有完成，错误代码：%RC%
echo 请把窗口截图，或把下面日志文件发回来：
echo %%LOCALAPPDATA%%\WOF Future Danger\OwnerTools\logs\bootstrap.log
pause
exit /b %RC%
