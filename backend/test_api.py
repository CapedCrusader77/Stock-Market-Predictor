#!/usr/bin/env python
"""Test backend API connectivity"""
import subprocess
import time
import requests
import sys

print("=" * 60)
print("Backend API Test Script")
print("=" * 60)

# Check if backend is running
print("\n[1/4] Checking if backend is running on localhost:8000...")
try:
    resp = requests.get("http://localhost:8000/health", timeout=2)
    if resp.status_code == 200:
        print("✓ Backend is responding!")
        print(f"  Response: {resp.json()}")
    else:
        print(f"✗ Backend returned status {resp.status_code}")
except requests.exceptions.ConnectionError:
    print("✗ Cannot connect to backend on http://localhost:8000")
    print("\nTo start backend, run:")
    print("  cd backend")
    print("  venv\\Scripts\\activate")
    print("  python api_complete.py")
    sys.exit(1)
except Exception as e:
    print(f"✗ Error: {e}")
    sys.exit(1)

# Test data loading
print("\n[2/4] Testing data loading for AAPL...")
try:
    resp = requests.post("http://localhost:8000/get-stock-data", 
        json={"ticker": "AAPL", "period": "1y"}, timeout=30)
    if resp.status_code == 200:
        data = resp.json()
        print(f"✓ Data loaded successfully!")
        print(f"  Rows: {data.get('rows')}")
        print(f"  Current Price: ${data.get('current_price', 'N/A'):.2f}")
    else:
        print(f"✗ Error: {resp.status_code}")
        print(f"  {resp.text}")
except Exception as e:
    print(f"✗ Error: {e}")

# Test model training
print("\n[3/4] Testing model training...")
try:
    resp = requests.post("http://localhost:8000/train-model",
        json={"ticker": "AAPL"}, timeout=30)
    if resp.status_code == 200:
        model = resp.json()
        print(f"✓ Model trained!")
        print(f"  Accuracy: {model.get('test_accuracy', 0):.3f}")
    else:
        print(f"✗ Error: {resp.status_code}")
except Exception as e:
    print(f"✗ Error: {e}")

# Test prediction
print("\n[4/4] Testing prediction...")
try:
    resp = requests.post("http://localhost:8000/predict",
        json={"ticker": "AAPL"}, timeout=10)
    if resp.status_code == 200:
        pred = resp.json()
        print(f"✓ Prediction received!")
        print(f"  Trend: {pred.get('trend')}")
        print(f"  Confidence: {pred.get('confidence', 0):.1%}")
    else:
        print(f"✗ Error: {resp.status_code}")
except Exception as e:
    print(f"✗ Error: {e}")

print("\n" + "=" * 60)
print("✓ Backend is working! Frontend should now load data.")
print("=" * 60)
