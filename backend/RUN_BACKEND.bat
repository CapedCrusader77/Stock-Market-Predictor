@echo off
REM ============================================
REM QUICK FIX - Install deps and run
REM ============================================

set BACKEND_DIR=%~dp0
echo Changing directory to "%BACKEND_DIR%"

REM Change to backend directory
cd /d "%BACKEND_DIR%"

echo.
echo Preparing virtual environment and installing dependencies into it...
echo.

if not exist "venv\Scripts\python.exe" (
	echo Virtual environment not found, creating venv...
	python -m venv venv
)

set VENV_PY=venv\Scripts\python.exe

echo Upgrading pip in venv...
%VENV_PY% -m pip install --upgrade pip

echo Installing dependencies into venv (this may take several minutes)...
if exist "requirements.txt" (
	%VENV_PY% -m pip install -r "requirements.txt"
) else (
	%VENV_PY% -m pip install fastapi uvicorn python-dotenv pandas numpy scikit-learn yfinance joblib nltk textblob feedparser requests pydantic
)

echo.
echo ✓ Dependencies installed into venv!
echo.
echo Starting API server using venv python...
echo.

echo Current working directory: %CD%
echo Listing files in current directory:
dir /b

echo.
echo Running api_complete.py...
%VENV_PY% api_complete.py

pause
