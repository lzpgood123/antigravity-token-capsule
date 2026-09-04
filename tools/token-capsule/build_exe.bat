@echo off
chcp 65001 >nul
title Building Antigravity Token Capsule EXE

echo ========================================================
echo   Antigravity Token Capsule - Standalone EXE Builder
echo ========================================================
echo.

cd /d "%~dp0"

:: 1. 激活 Python 解释器
if exist ".venv\Scripts\activate.bat" (
    echo [INFO] Activating local virtual environment (.venv)...
    call .venv\Scripts\activate.bat
) else (
    echo [INFO] Using global Python interpreter...
)

:: 2. 检查依赖
python -c "import PySide6, PyInstaller, PIL" 2>nul
if errorlevel 1 (
    echo [WARN] Missing required dependencies. Installing...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [ERROR] Failed to install dependencies. Aborting.
        pause
        exit /b 1
    )
)

:: 3. 确保图标存在
if not exist "capsule.ico" (
    echo [INFO] Generating custom capsule icon (capsule.ico)...
    python generate_icon.py
)

echo.
echo [1/2] Compiling Standalone Single-File EXE (--onefile)...
pyinstaller --noconsole --onefile --clean -y ^
    --name "token-capsule" ^
    --icon "capsule.ico" ^
    --add-data "%~dp0capsule.ico;." ^
    --distpath "dist/onefile" ^
    main.py

if errorlevel 1 (
    echo [ERROR] Single-file build failed!
    pause
    exit /b 1
)

echo.
echo [2/2] Compiling Portable Directory EXE (--onedir)...
pyinstaller --noconsole --onedir --clean -y ^
    --name "token-capsule" ^
    --icon "capsule.ico" ^
    --add-data "%~dp0capsule.ico;." ^
    --distpath "dist/onedir" ^
    main.py

if errorlevel 1 (
    echo [ERROR] Directory build failed!
    pause
    exit /b 1
)

echo.
echo ========================================================
echo   BUILD COMPLETED SUCCESSFULLY!
echo ========================================================
echo.
echo Output Deliverables:
echo   1. Single-file: dist\onefile\token-capsule.exe
echo   2. Portable dir: dist\onedir\token-capsule\token-capsule.exe
echo.
pause
