#!/usr/bin/env python
"""
Test script to verify webscraping and data fetching functionality
"""

import sys
import traceback
from datetime import datetime

print("=" * 70)
print("STOCK MARKET PREDICTOR - WEBSCRAPING & DATA FETCHING TEST")
print("=" * 70)
print(f"Timestamp: {datetime.now().isoformat()}")
print()

# Test 1: Import required modules
print("[TEST 1/5] Checking required imports...")
try:
    import yfinance as yf
    import pandas as pd
    import numpy as np
    import feedparser
    import requests
    print("✓ All imports successful")
except Exception as e:
    print(f"✗ Import failed: {e}")
    sys.exit(1)

print()

# Test 2: Test yfinance with proper headers
print("[TEST 2/5] Testing yfinance data fetch (AAPL)...")
try:
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    
    stock = yf.Ticker("AAPL", session=session)
    hist = stock.history(period="1mo")
    
    if hist.empty:
        print("✗ yfinance returned empty data")
    else:
        print(f"✓ yfinance successful!")
        print(f"  - Rows fetched: {len(hist)}")
        print(f"  - Latest close: ${hist['Close'].iloc[-1]:.2f}")
        print(f"  - 30-day range: ${hist['Close'].min():.2f} - ${hist['Close'].max():.2f}")
except Exception as e:
    print(f"✗ yfinance test failed: {e}")
    traceback.print_exc()

print()

# Test 3: Test sentiment analyzer
print("[TEST 3/5] Testing sentiment analyzer...")
try:
    from sentiment_analyzer import SentimentAnalyzer
    analyzer = SentimentAnalyzer()
    
    # Test sentiment analysis
    test_text = "Stock surges on strong earnings growth and bull market momentum"
    sentiment = analyzer.analyze_sentiment(test_text)
    print(f"✓ Sentiment analysis works!")
    print(f"  - Text: '{test_text}'")
    print(f"  - Sentiment: {sentiment['sentiment']}")
    print(f"  - Score: {sentiment['score']:.2f}")
except Exception as e:
    print(f"✗ Sentiment analyzer test failed: {e}")
    traceback.print_exc()

print()

# Test 4: Test news fetching
print("[TEST 4/5] Testing news fetching (AAPL)...")
try:
    from sentiment_analyzer import SentimentAnalyzer
    analyzer = SentimentAnalyzer()
    
    news = analyzer.fetch_news("AAPL", limit=5)
    if news:
        print(f"✓ News fetching works!")
        print(f"  - Articles found: {len(news)}")
        if len(news) > 0:
            print(f"  - Latest: {news[0]['title'][:60]}...")
            print(f"  - Sentiment: {news[0]['sentiment']}")
    else:
        print("⚠ News fetching returned no results (may be normal if no AAPL news)")
except Exception as e:
    print(f"✗ News fetching test failed: {e}")
    traceback.print_exc()

print()

# Test 5: Test data pipeline
print("[TEST 5/5] Testing data pipeline...")
try:
    from data_pipeline import DataPipeline
    pipeline = DataPipeline()
    
    data = pipeline.fetch_stock_data("GOOGL", period="1mo")
    if data.empty:
        print("✗ Data pipeline returned empty data")
    else:
        print(f"✓ Data pipeline works!")
        print(f"  - Ticker: GOOGL")
        print(f"  - Rows: {len(data)}")
        print(f"  - Columns: {list(data.columns)}")
        
        # Test indicator calculation
        data_with_indicators = pipeline.calculate_indicators(data)
        print(f"  - RSI calculated: {not data_with_indicators['RSI'].isna().all()}")
        print(f"  - MACD calculated: {not data_with_indicators['MACD'].isna().all()}")
except Exception as e:
    print(f"✗ Data pipeline test failed: {e}")
    traceback.print_exc()

print()
print("=" * 70)
print("TEST SUMMARY")
print("=" * 70)
print("If all tests passed (✓), the webscraping functionality is working!")
print("If some tests failed (✗), check the error messages above.")
print("⚠ indicates warnings that may be normal (no data available)")
print()
print("Next steps:")
print("1. Start the backend: python api_complete.py")
print("2. Test the API: http://localhost:8000/docs")
print("3. Test data fetch: POST /get-stock-data with ticker AAPL")
print("=" * 70)
