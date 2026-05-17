"""
Debug script to test data fetching
"""
import requests
import yfinance as yf
import pandas as pd
from sample_data import generate_sample_data

def test_yfinance_direct():
    """Test yfinance directly"""
    print("=" * 50)
    print("1. Testing yfinance directly...")
    print("=" * 50)
    try:
        ticker = yf.Ticker("AAPL")
        hist = ticker.history(period="1y")
        print(f"✓ Direct fetch worked: {len(hist)} rows")
        print(hist.head())
        return hist
    except Exception as e:
        print(f"✗ Direct fetch failed: {e}")
        return None

def test_yfinance_with_session():
    """Test yfinance with session"""
    print("\n" + "=" * 50)
    print("2. Testing yfinance with session...")
    print("=" * 50)
    try:
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        ticker = yf.Ticker("AAPL", session=session)
        hist = ticker.history(period="1y")
        print(f"✓ Session fetch worked: {len(hist)} rows")
        print(hist.head())
        return hist
    except Exception as e:
        print(f"✗ Session fetch failed: {e}")
        return None

def test_sample_data():
    """Test sample data generation"""
    print("\n" + "=" * 50)
    print("3. Testing sample data generation...")
    print("=" * 50)
    try:
        data = generate_sample_data("AAPL", 252)
        print(f"✓ Sample data generated: {len(data)} rows")
        print(data.head())
        return data
    except Exception as e:
        print(f"✗ Sample data failed: {e}")
        return None

def test_api_endpoint():
    """Test API endpoint"""
    print("\n" + "=" * 50)
    print("4. Testing API endpoint...")
    print("=" * 50)
    try:
        response = requests.post(
            "http://localhost:8000/get-stock-data",
            json={"ticker": "AAPL", "period": "1y"},
            timeout=10
        )
        print(f"Status: {response.status_code}")
        if response.ok:
            data = response.json()
            print(f"✓ API returned data: {data.get('count', 0)} rows")
            print(f"First row: {data.get('data', [{}])[0] if data.get('data') else 'None'}")
        else:
            print(f"✗ API error: {response.text}")
    except requests.exceptions.ConnectionError:
        print("✗ Cannot connect to API - is backend running?")
    except Exception as e:
        print(f"✗ API test failed: {e}")

if __name__ == "__main__":
    print("\n📊 DATA FETCH DEBUG SCRIPT\n")
    
    # Run tests
    test_yfinance_direct()
    test_yfinance_with_session()
    test_sample_data()
    
    print("\n" + "=" * 50)
    print("Start the backend with: python api_complete.py")
    print("=" * 50)
    
    # Wait a moment then test API
    import time
    time.sleep(2)
    test_api_endpoint()
