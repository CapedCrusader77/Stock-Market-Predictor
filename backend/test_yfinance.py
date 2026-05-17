"""Test yfinance connectivity"""
import yfinance as yf

print("Testing yfinance connection...")
print()

try:
    print("[1] Testing AAPL ticker...")
    stock = yf.Ticker("AAPL")
    hist = stock.history(period="1d")
    print(f"✓ AAPL works! Got {len(hist)} rows")
    print(f"  Latest close: {hist['Close'].iloc[-1]}")
    print()
except Exception as e:
    print(f"✗ Error with AAPL: {e}")
    print()

try:
    print("[2] Testing with period='5y'...")
    stock = yf.Ticker("AAPL")
    hist = stock.history(period="5y")
    print(f"✓ 5y period works! Got {len(hist)} rows")
    print(f"  Latest close: {hist['Close'].iloc[-1]}")
    print()
except Exception as e:
    print(f"✗ Error with 5y period: {e}")
    print()

try:
    print("[3] Testing with start/end dates...")
    from datetime import datetime, timedelta
    end = datetime.now()
    start = end - timedelta(days=365)
    stock = yf.Ticker("AAPL")
    hist = stock.history(start=start, end=end)
    print(f"✓ Date range works! Got {len(hist)} rows")
    print(f"  Latest close: {hist['Close'].iloc[-1]}")
    print()
except Exception as e:
    print(f"✗ Error with date range: {e}")
    print()

print("=" * 60)
print("If all tests pass, the issue is with the backend API.")
print("If tests fail, there's a yfinance/network issue.")
print("=" * 60)
