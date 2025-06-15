@echo off
curl -s http://localhost:5000/health > nul
if %errorlevel% neq 0 (
    exit /b 1
) else (
    exit /b 0
)
