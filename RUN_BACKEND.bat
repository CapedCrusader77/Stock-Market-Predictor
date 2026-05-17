@echo off
REM ============================================
REM Stock Market Predictor - Backend Startup
REM ============================================

echo.
echo ============================================
echo STOCK MARKET PREDICTOR - BACKEND STARTUP
echo ============================================
echo.

REM Delegate to backend's own startup script
cd /d "%~dp0backend"
call RUN_BACKEND.bat
