@echo off
chcp 65001 >nul
setlocal EnableExtensions

title WOF 一键下载与真人验证
set "WOF_ROOT=%LOCALAPPDATA%\WOF Future Danger\OneClickProof"
set "WOF_RUN=%WOF_ROOT%\run_%RANDOM%_%RANDOM%"
set "WOF_ZIP=%TEMP%\wof-ai-private-main-%RANDOM%.zip"

echo.
echo ========================================
echo   WOF Launcher 一键下载与真人验证
echo ========================================
echo.
echo 本工具只连接本机 Chrome/Edge CDP：
echo   只读模式：开启
echo   游戏内存写入：0
echo   输入注入：关闭
echo.
echo 正在下载最新 WOF Launcher...

if not exist "%WOF_ROOT%" mkdir "%WOF_ROOT%" >nul 2>&1
if not exist "%WOF_RUN%" mkdir "%WOF_RUN%" >nul 2>&1

powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "$ErrorActionPreference='Stop'; $ProgressPreference='SilentlyContinue'; [Net.ServicePointManager]::SecurityProtocol=[Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -UseBasicParsing 'https://codeload.github.com/ouyong520/wof-ai-private/zip/refs/heads/main' -OutFile $env:WOF_ZIP; Expand-Archive -LiteralPath $env:WOF_ZIP -DestinationPath $env:WOF_RUN -Force"
if errorlevel 1 goto :download_fail

set "WOF_PROJECT=%WOF_RUN%\wof-ai-private-main"
if not exist "%WOF_PROJECT%\parallel\PYLAUNCH\RUN_WINDOWS_PROOF.cmd" goto :download_fail

del /q "%WOF_ZIP%" >nul 2>&1

echo 下载完成，正在启动 WOF Launcher...
echo.
call "%WOF_PROJECT%\parallel\PYLAUNCH\RUN_WINDOWS_PROOF.cmd"
if errorlevel 1 goto :launcher_fail

echo.
echo 已完成启动。
echo 现在只需要在自动打开的专用 Chrome/Edge 中正常进入 WOF 房间。
echo Launcher 会自动验证 WOF 页面、Worker、WASM / 内存和 World 921031。
echo 不需要 DevTools，不需要 Worker Console，不需要粘贴 JavaScript。
echo.
exit /b 0

:download_fail
echo.
echo 无法下载或解压最新 WOF Launcher。
echo 游戏和浏览器本身没有受到影响。
echo 请确认 Windows 可以访问 GitHub，然后重新双击本文件。
pause
exit /b 1

:launcher_fail
echo.
echo WOF Launcher 没有成功启动。
echo 游戏和浏览器本身没有受到影响。
echo 请查看上方中文提示；如果生成了 WINDOWS_PROOF_STATUS.json，只需要把这个文件发回来。
pause
exit /b 1
