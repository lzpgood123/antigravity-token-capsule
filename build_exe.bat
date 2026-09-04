@echo off
chcp 65001 >nul
title Building Antigravity Token Capsule EXE

echo ========================================================
echo   Antigravity Token Capsule - Standalone EXE Builder
echo ========================================================
echo.

cd /d "%~dp0"

:: 1. 终止旧实例防止文件占用
taskkill /f /im token-capsule.exe >nul 2>nul
timeout /t 1 /nobreak >nul

:: 2. 激活 Python 解释器
if exist ".venv\Scripts\activate.bat" (
    echo [INFO] Activating local virtual environment .venv...
    call .venv\Scripts\activate.bat
) else (
    echo [INFO] Using global Python interpreter...
)

:: 3. 检查依赖
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

:: 4. 确保图标存在
if not exist "capsule.ico" (
    echo [INFO] Generating custom capsule icon capsule.ico...
    python generate_icon.py
)

:: 清理旧 spec 避免干扰
if exist "token-capsule.spec" del /f /q "token-capsule.spec"

echo.
echo [1/4] Compiling Standalone Single-File EXE (--onefile)...
pyinstaller --noconsole --onefile --clean -y ^
    --name "token-capsule" ^
    --icon "%~dp0capsule.ico" ^
    --add-data "%~dp0capsule.ico;." ^
    --specpath "build/onefile" ^
    --workpath "build/onefile" ^
    --distpath "dist/onefile" ^
    main.py

if errorlevel 1 (
    echo [ERROR] Single-file build failed!
    pause
    exit /b 1
)

echo.
echo [2/4] Compiling Portable Directory EXE (--onedir)...
if exist "dist\onedir" rmdir /s /q "dist\onedir" 2>nul
pyinstaller --noconsole --onedir --clean -y ^
    --name "token-capsule" ^
    --icon "%~dp0capsule.ico" ^
    --add-data "%~dp0capsule.ico;." ^
    --specpath "build/onedir" ^
    --workpath "build/onedir" ^
    --distpath "dist/onedir" ^
    main.py

if errorlevel 1 (
    echo [ERROR] Directory build failed!
    pause
    exit /b 1
)

:: 校验 onedir 内置 Python 解释器完整性
if not exist "dist\onedir\token-capsule\_internal\base_library.zip" (
    echo [ERROR] Critical verification failed: _internal\base_library.zip is missing!
    pause
    exit /b 1
)

echo.
echo [3/4] Creating Portable ZIP Archive...
if not exist "dist\zip" mkdir "dist\zip"
powershell -Command "Compress-Archive -Path 'dist\onedir\token-capsule\*' -DestinationPath 'dist\zip\token-capsule-v1.1.0-windows-x64.zip' -Force"

echo.
echo [4/4] Checking and Compiling Inno Setup Installer...
set "ISCC_PATH="
if exist "%LOCALAPPDATA%\Programs\Inno Setup 6\ISCC.exe" set "ISCC_PATH=%LOCALAPPDATA%\Programs\Inno Setup 6\ISCC.exe"
if exist "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" set "ISCC_PATH=C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
if exist "C:\Program Files\Inno Setup 6\ISCC.exe" set "ISCC_PATH=C:\Program Files\Inno Setup 6\ISCC.exe"

if defined ISCC_PATH (
    echo [INFO] Found Inno Setup compiler at "%ISCC_PATH%"
    "%ISCC_PATH%" installer.iss
    if errorlevel 1 (
        echo [WARN] Inno Setup compilation failed!
    ) else (
        echo [INFO] Installer created successfully!
    )
) else (
    echo [WARN] ISCC.exe not found in common locations. Skipping installer compilation.
)

echo.
echo ========================================================
echo   BUILD COMPLETED SUCCESSFULLY!
echo ========================================================
echo.
echo Output Deliverables:
echo   1. Windows Installer: dist\installer\token-capsule-Setup-v1.1.0.exe
echo   2. Portable ZIP:      dist\zip\token-capsule-v1.1.0-windows-x64.zip
echo   3. Standalone EXE:    dist\onefile\token-capsule.exe
echo   4. Portable dir:      dist\onedir\token-capsule\
echo.
pause