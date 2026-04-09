@echo off
title NotY Caption Generator AI Builder
color 0A

echo ============================================================
echo Building NotY Caption Generator AI v5.2
echo ============================================================
echo.

:: Get the current directory
set "CURRENT_DIR=%~dp0"
cd /d "%CURRENT_DIR%"

echo Current directory: %CD%
echo.

:: Check if source file exists
if not exist "noty_caption_gen.py" (
    echo [ERROR] noty_caption_gen.py not found in %CD%
    echo.
    echo Please make sure you are running this from the correct directory.
    pause
    exit /b 1
)

echo [OK] Source file found: noty_caption_gen.py
echo.

:: Clean previous builds
echo Cleaning previous builds...
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"
if exist "*.spec" del /q "*.spec"
if exist "Builder\build" rmdir /s /q "Builder\build"

echo.
echo Building executable...
python Builder\build_exe.py

if errorlevel 1 (
    echo.
    echo [ERROR] Build failed!
    pause
    exit /b 1
)

echo.
echo ============================================================
echo BUILD COMPLETE!
echo ============================================================
echo.
echo Executable is in the 'dist' folder
echo Run: dist\Run_App.bat
echo.
pause