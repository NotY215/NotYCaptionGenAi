@echo off
title Building NotY Caption Generator AI
color 0A

echo ============================================================
echo Building NotY Caption Generator AI v5.2
echo ============================================================
echo.

:: Clean previous builds
echo Cleaning previous builds...
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"
if exist "*.spec" del /q "*.spec"

:: Build executable
echo.
echo Building executable...
python build_exe.py

if errorlevel 1 (
    echo [ERROR] Build failed!
    pause
    exit /b 1
)

:: Build installers
echo.
echo Building installers...
python build_installer.py

echo.
echo ============================================================
echo BUILD COMPLETE!
echo ============================================================
echo.
echo Executable and installers are in the 'dist' folder
echo.
pause