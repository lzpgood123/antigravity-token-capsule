@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo [Token Capsule] 正在启动 Antigravity 实时 Token 监控胶囊...

if exist "%~dp0.venv\Scripts\python.exe" (
    echo [Token Capsule] 检测到专用虚拟环境，正在启动: .venv
    "%~dp0.venv\Scripts\python.exe" main.py
) else (
    echo [Token Capsule] 未检测到局部 .venv，尝试调用系统 Python...
    python main.py
)

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] 启动失败，请检查是否已安装依赖：pip install -r requirements.txt
    pause
)
