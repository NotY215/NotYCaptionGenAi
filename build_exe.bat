@echo off
title Building NotY Caption Generator AI
echo ============================================================
echo Building NotY Caption Generator AI v5.2
echo ============================================================
echo.

:: Activate virtual environment if it exists
if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
)

:: Install/update build tools
echo Installing build tools...
pip install --upgrade nuitka ordered-set zstandard pyinstaller

:: Clean previous builds
echo.
echo Cleaning previous builds...
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"
if exist "*.spec" del /q "*.spec"

:: Run the build
echo.
echo Starting build process...
python build_nuitka.py

if errorlevel 1 (
    echo.
    echo ============================================================
    echo BUILD FAILED!
    echo ============================================================
    pause
    exit /b 1
)

echo.
echo ============================================================
echo BUILD SUCCESSFUL!
echo ============================================================
echo.
echo Executable is in the 'dist' folder
echo.

pause