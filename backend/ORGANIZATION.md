# Backend Organization Guide

This file documents the organization of backend files:

## Current Structure

### Root Level (Entry Point)
- `api_complete.py` - Main FastAPI server (DO NOT MOVE)
- `requirements.txt` - Python dependencies
- `RUN_BACKEND.bat` - Batch file to run backend
- `INSTALL_DEPS.bat` - Install dependencies

### Core Logic Files
- `stock_predictor.py` - ML predictions
- `data_pipeline.py` - Data fetching & processing
- `sentiment_analyzer.py` - News sentiment analysis
- `backtester.py` - Backtesting engine
- `sample_data.py` - Fallback sample data generator

### Test Files
- `test_api.py` - API endpoint tests
- `test_data_fetch.py` - Data fetching tests
- `test_webscraping.py` - Web scraping tests
- `test_yfinance.py` - yfinance connectivity tests
- `debug_fetch.py` - Debug data fetch issues

### Directories
- `app/` - FastAPI app structure
- `models/` - Trained ML models (pickle files)
- `data/` - Stock data cache
- `__pycache__/` - Python cache (ignore)
- `venv/` - Virtual environment (ignore)

### Old/Unused Files
- `DATA_PIPELINE_STUB.py` - Old stub (can delete)
- `api_server.py` - Old API file (can delete)
- `setup.py` - Setup script (can keep for reference)

## Recommended Organization (if reorganizing)

### Proposed Structure:
```
backend/
├── api_complete.py          # Keep at root
├── requirements.txt
├── core/                    # Core functionality
│   ├── stock_predictor.py
│   ├── data_pipeline.py
│   └── sentiment_analyzer.py
├── utils/                   # Utility modules
│   ├── backtester.py
│   └── sample_data.py
├── tests/                   # Test files
│   ├── test_api.py
│   ├── test_data_fetch.py
│   └── test_webscraping.py
├── models/                  # ML models
├── data/                    # Cache
└── config/                  # Configuration
```

## Notes
- Moving files requires updating imports in api_complete.py
- Currently all modules are imported at top level
- Reorganization is optional - current flat structure works fine
