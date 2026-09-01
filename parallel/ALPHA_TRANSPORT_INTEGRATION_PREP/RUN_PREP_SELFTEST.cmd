@echo off
setlocal
chcp 65001 >nul
cd /d "%~dp0"
echo [WOF Alpha Transport] 运行 Real Adapter Prep 仓库自检...
where node >nul 2>nul
if errorlevel 1 (
  echo [失败] 未找到 Node.js。此检查只需要仓库和 Node.js，不需要启动浏览器或 WOF。
  exit /b 2
)
node selftest.mjs
if errorlevel 1 (
  echo [失败] Real Adapter Prep 自检未通过。
  exit /b 1
)
echo [通过] Real Adapter Prep 自检通过；无需 Owner 浏览器操作。
exit /b 0
