"""
Quick test to verify data fetching works
"""
import sys
sys.path.insert(0, r'd:\Projects\Stock_Market_Predictor\backend')

from sample_data import generate_sample_data
import requests
import yfinance as yf
import time

print("=" * 60)
print("DATA FETCH TEST")
print("=" * 60)

# Test 1: Sample data generation
print("\n[TEST 1] Sample Data Generation")
try:
    data = generate_sample_data("AAPL", 252)
    print(f"✓ Generated {len(data)} rows of sample data")
    print(f"  Columns: {list(data.columns)}")
    print(f"  Price range: ${data['Close'].min():.2f} - ${data['Close'].max():.2f}")
except Exception as e:
    print(f"✗ Sample data failed: {e}")

# Test 2: yfinance direct
print("\n[TEST 2] yfinance Direct")
try:
    stock = yf.Ticker("AAPL")
    hist = stock.history(period="1y")
    if not hist.empty:
        print(f"✓ Got {len(hist)} rows from yfinance")
        print(f"  Columns: {list(hist.columns)}")
    else:
        print("✗ yfinance returned empty")
except Exception as e:
    print(f"✗ yfinance failed: {e}")

# Test 3: yfinance with session
print("\n[TEST 3] yfinance With Session")
try:
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    stock = yf.Ticker("AAPL", session=session)
    hist = stock.history(period="1y")
    if not hist.empty:
        print(f"✓ Got {len(hist)} rows from yfinance with session")
        print(f"  Columns: {list(hist.columns)}")
    else:
        print("✗ yfinance with session returned empty")
except Exception as e:
    print(f"✗ yfinance with session failed: {e}")

print("\n" + "=" * 60)
print("If tests pass, backend should work correctly.")
print("Start backend: python api_complete.py")
print("Start frontend: cd ../frontend && npm start")
print("=" * 60)
