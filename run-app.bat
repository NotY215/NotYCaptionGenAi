@echo off
chcp 65001 >nul
title NotY Caption Generator AI
color 0A

echo ╔═══════════════════════════════════════════╗
echo ║     NOTY CAPTION GENERATOR AI v1.0       ║
echo ║     Powered by Whisper.cpp               ║
echo ╚═══════════════════════════════════════════╝
echo.

REM Check if JAR exists
if not exist "build\libs\NotYCaptionGenAi-1.0.0.jar" (
    echo Building application...
    call gradlew jar
    if errorlevel 1 (
        echo Build failed!
        pause
        exit /b 1
    )
    echo.
)

echo Starting application...
echo.

REM Run the JAR directly - this opens a proper console
java -jar build\libs\NotYCaptionGenAi-1.0.0.jar

echo.
echo Application finished.
pause