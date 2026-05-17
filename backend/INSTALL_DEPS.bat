@echo off
REM ============================================
REM INSTALL DEPENDENCIES DIRECTLY
REM ============================================

echo.
echo Installing Python packages (this may take 3-5 minutes)...
echo.

pip install fastapi==0.104.1
pip install uvicorn==0.24.0
pip install python-dotenv==1.0.0
pip install pandas==2.1.3
pip install numpy==1.26.2
pip install scikit-learn==1.3.2
pip install yfinance==0.2.32
pip install joblib==1.3.2
pip install nltk==3.8.1
pip install textblob==0.17.1
pip install feedparser==6.0.10
pip install requests==2.31.0
pip install pydantic==2.5.0

echo.
echo ============================================
echo ✓ All packages installed!
echo ============================================
echo.
echo Now run: python api_complete.py
echo.
pause
