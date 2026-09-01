@echo off
setlocal
chcp 65001 >nul 2>nul
cd /d "%~dp0"

where py >nul 2>nul
if %errorlevel%==0 (
  py -3 endurance_sim.py %*
  exit /b %errorlevel%
)

where python >nul 2>nul
if %errorlevel%==0 (
  python endurance_sim.py %*
  exit /b %errorlevel%
)

echo [失败] 找不到 Python 3。此离线模拟器没有连接浏览器，也不会修改游戏。
exit /b 2
