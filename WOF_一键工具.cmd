@echo off
setlocal EnableExtensions
chcp 65001 >nul 2>&1
title WOF 一键工具

set "BOOT_URL=https://raw.githubusercontent.com/ouyong520/wof-ai-private/main/parallel/OWNER_ONECLICK/bootstrap.ps1"
set "BOOT_PS1=%TEMP%\WOF_owner_bootstrap_%RANDOM%_%RANDOM%.ps1"

echo.
echo ================================================
echo              WOF 一键工具
echo ================================================
echo 正在启动 WOF 工具安装/更新程序...

powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "$ErrorActionPreference='Stop'; [Net.ServicePointManager]::SecurityProtocol=[Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -UseBasicParsing -Uri '%BOOT_URL%' -OutFile '%BOOT_PS1%' -TimeoutSec 45"
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
