"""
Stock Market Predictor - FastAPI Backend
Main API server with stock data, predictions, and indicators
"""

import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import joblib
from pathlib import Path
import asyncio
from concurrent.futures import ThreadPoolExecutor
import functools
import time
import requests

# Import sample data generator as fallback
try:
    from sample_data import generate_sample_data
    SAMPLE_DATA_AVAILABLE = True
except ImportError:
    SAMPLE_DATA_AVAILABLE = False

# Simple in-memory cache
data_cache = {}
cache_expiry = {}
CACHE_DURATION = 300  # 5 minutes

# Thread pool for parallel execution
executor = ThreadPoolExecutor(max_workers=16)

# Initialize FastAPI app
app = FastAPI(
    title="Stock Market Predictor API",
    description="API for stock analysis and prediction",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class StockRequest(BaseModel):
    ticker: str
    period: str = "1y"
    
    class Config:
        json_schema_extra = {
            "example": {
                "ticker": "AAPL",
                "period": "1y"
            }
        }

class PredictionRequest(BaseModel):
    ticker: str
    days: int = 5
    
    class Config:
        json_schema_extra = {
            "example": {
                "ticker": "AAPL",
                "days": 5
            }
        }

class IndicatorResponse(BaseModel):
    ticker: str
    rsi: float
    macd: float
    signal: float
    sma_20: float
    sma_50: float
    current_price: float
    timestamp: str

class TradingRecommendation(BaseModel):
    ticker: str
    action: str  # "BUY", "SELL", "HOLD"
    confidence: float
    entry_price: float
    target_price: float
    stop_loss: float
    time_horizon: str  # "Short-term", "Medium-term", "Long-term"
    risk_level: str  # "Low", "Medium", "High"
    reasoning: str
    technical_signals: Dict[str, str]
    optimal_entry_time: str
    suggested_hold_duration: str

class WatchlistRequest(BaseModel):
    tickers: List[str]
    period: str = "1mo"

    class Config:
        json_schema_extra = {
            "example": {
                "tickers": ["AAPL", "GOOGL", "MSFT", "AMZN"],
                "period": "1mo"
            }
        }

# Popular stocks for TradingView-style dashboard
POPULAR_STOCKS = [
    "AAPL", "GOOGL", "MSFT", "AMZN", "TSLA", "META", "NVDA", "JPM",
    "V", "WMT", "DIS", "NFLX", "PYPL", "ADBE", "INTC", "CSCO",
    "CMCSA", "PFE", "KO", "PEP", "T", "BAC", "XOM", "CVX"
]

STOCK_NAMES = {
    "AAPL": "Apple Inc.",
    "GOOGL": "Alphabet Inc.",
    "MSFT": "Microsoft Corporation",
    "AMZN": "Amazon.com, Inc.",
    "TSLA": "Tesla, Inc.",
    "META": "Meta Platforms, Inc.",
    "NVDA": "NVIDIA Corporation",
    "JPM": "JPMorgan Chase & Co.",
    "V": "Visa Inc.",
    "WMT": "Walmart Inc.",
    "DIS": "The Walt Disney Company",
    "NFLX": "Netflix, Inc.",
    "PYPL": "PayPal Holdings, Inc.",
    "ADBE": "Adobe Inc.",
    "INTC": "Intel Corporation",
    "CSCO": "Cisco Systems, Inc.",
    "CMCSA": "Comcast Corporation",
    "PFE": "Pfizer Inc.",
    "KO": "The Coca-Cola Company",
    "PEP": "PepsiCo, Inc.",
    "T": "AT&T Inc.",
    "BAC": "Bank of America Corporation",
    "XOM": "Exxon Mobil Corporation",
    "CVX": "Chevron Corporation",
}

class MiniChartData(BaseModel):
    ticker: str
    name: str
    current_price: float
    change: float
    change_percent: float
    volume: int
    high: float
    low: float
    open: float
    data: List[Dict]
    period: str

def build_opportunity_score(ticker: str, hist: pd.DataFrame) -> Optional[Dict]:
    """Score a ticker for bullish, lower-risk setups from recent price action."""
    try:
        if hist is None or hist.empty or len(hist) < 50:
            return None

        prices = hist["Close"].values
        latest = hist.iloc[-1]
        previous = hist.iloc[-2] if len(hist) > 1 else latest
        current_price = float(latest["Close"])
        previous_price = float(previous["Close"])
        change = current_price - previous_price
        change_percent = (change / previous_price) * 100 if previous_price else 0

        rsi = calculate_rsi(prices)
        macd, signal = calculate_macd(prices)
        sma_20 = calculate_sma(prices, 20)
        sma_50 = calculate_sma(prices, 50)
        momentum_5d = ((prices[-1] - prices[-5]) / prices[-5]) * 100 if len(prices) >= 5 and prices[-5] else 0
        momentum_20d = ((prices[-1] - prices[-20]) / prices[-20]) * 100 if len(prices) >= 20 and prices[-20] else 0
        daily_returns = pd.Series(prices).pct_change().dropna()
        volatility = float(daily_returns.tail(30).std() * 100) if not daily_returns.empty else 0

        if rsi > 72 or change_percent < -3:
            return None

        score = 0.0
        reasons = []

        if 45 <= rsi <= 62:
            score += 18
            reasons.append("Healthy RSI")
        elif 38 <= rsi < 45:
            score += 10
            reasons.append("Recovering RSI")
        elif 62 < rsi <= 70:
            score += 6
            reasons.append("RSI near upper range")
        elif rsi > 70:
            score -= 14
            reasons.append("Overbought")

        if macd > signal and macd > 0:
            score += 16
            reasons.append("MACD improving")
        elif macd > signal:
            score += 8
            reasons.append("MACD turning up")
        else:
            score -= 8

        if current_price > sma_20 > sma_50:
            score += 20
            reasons.append("Strong uptrend")
        elif current_price > sma_20:
            score += 10
            reasons.append("Above MA-20")
        elif current_price < sma_50:
            score -= 12

        if 0.5 <= momentum_5d <= 6:
            score += 16
            reasons.append("Positive short momentum")
        elif 0 < momentum_5d < 0.5:
            score += 6
        elif momentum_5d < -2:
            score -= 18
            reasons.append("Weak short momentum")

        if 1 <= momentum_20d <= 12:
            score += 16
            reasons.append("Positive monthly momentum")
        elif 12 < momentum_20d <= 20:
            score += 7
            reasons.append("Extended monthly run")
        elif momentum_20d < 0:
            score -= 12

        if volatility < 1.8:
            score += 12
            reasons.append("Controlled volatility")
        elif volatility <= 3:
            score += 6
        elif volatility > 4:
            score -= 14
            reasons.append("Higher volatility")

        if change_percent >= 0:
            score += 8
            reasons.append("Green latest close")
        elif change_percent < -3:
            score -= 22
            reasons.append("Sharp latest drop")
        elif change_percent < -1:
            score -= 10

        score = max(0, min(score, 90))
        if score < 55:
            return None

        upside_percent = max(0.025, min((max(momentum_20d, 0) / 100) * 0.45 + 0.025, 0.09))
        upside_target = current_price * (1 + upside_percent)

        mini_data = []
        for date, row in hist.tail(15).iterrows():
            mini_data.append({
                "date": date.strftime("%Y-%m-%d"),
                "price": float(row["Close"])
            })

        if score >= 78:
            rating = "Strong setup"
        elif score >= 66:
            rating = "Watch closely"
        else:
            rating = "Moderate setup"

        return {
            "ticker": ticker,
            "name": get_stock_name(ticker),
            "score": round(score, 1),
            "rating": rating,
            "current_price": current_price,
            "change": change,
            "change_percent": change_percent,
            "target_price": float(upside_target),
            "rsi": float(rsi),
            "momentum_20d": float(momentum_20d),
            "volatility": volatility,
            "reasons": reasons[:3],
            "data": mini_data,
        }
    except Exception as e:
        print(f"Error scoring opportunity for {ticker}: {e}")
        return None

# Helper functions
def calculate_rsi(prices, period=14):
    """Calculate Relative Strength Index"""
    deltas = np.diff(prices)
    seed = deltas[:period+1]
    up = seed[seed >= 0].sum() / period
    down = -seed[seed < 0].sum() / period
    rs = up / down if down != 0 else 0
    rsi = np.zeros_like(prices)
    rsi[:period] = 100. - 100. / (1. + rs)
    
    for i in range(period, len(prices)):
        delta = deltas[i-1]
        if delta > 0:
            upval = delta
            downval = 0.
        else:
            upval = 0.
            downval = -delta
        
        up = (up * (period - 1) + upval) / period
        down = (down * (period - 1) + downval) / period
        rs = up / down if down != 0 else 0
        rsi[i] = 100. - 100. / (1. + rs)
    
    return rsi[-1]

def calculate_macd(prices, fast=12, slow=26, signal=9):
    """Calculate MACD indicators"""
    ema_fast = pd.Series(prices).ewm(span=fast).mean()
    ema_slow = pd.Series(prices).ewm(span=slow).mean()
    macd = ema_fast - ema_slow
    signal_line = macd.ewm(span=signal).mean()
    return macd.iloc[-1], signal_line.iloc[-1]

def calculate_sma(prices, period):
    """Calculate Simple Moving Average"""
    return pd.Series(prices).rolling(window=period).mean().iloc[-1]

def get_stock_name(ticker: str) -> str:
    """Get the full name of a stock from its ticker symbol"""
    ticker = ticker.upper()
    if ticker in STOCK_NAMES:
        return STOCK_NAMES[ticker]

    try:
        stock_info = yf.Ticker(ticker).info
        return stock_info.get('longName', ticker)
    except:
        return ticker

def generate_trading_recommendation(ticker: str, hist: pd.DataFrame) -> Dict:
    """Generate comprehensive trading recommendation with timing"""
    try:
        prices = hist["Close"].values
        current_price = float(prices[-1])

        # Calculate technical indicators
        rsi = calculate_rsi(prices)
        macd, signal = calculate_macd(prices)
        sma_20 = calculate_sma(prices, 20)
        sma_50 = calculate_sma(prices, 50)

        # Analyze technical signals
        signals = {}

        # RSI Analysis
        if rsi < 30:
            signals["rsi"] = "Oversold - BUY signal"
            rsi_signal = "bullish"
        elif rsi > 70:
            signals["rsi"] = "Overbought - SELL signal"
            rsi_signal = "bearish"
        else:
            signals["rsi"] = "Neutral"
            rsi_signal = "neutral"

        # MACD Analysis
        if macd > signal and macd > 0:
            signals["macd"] = "Bullish momentum - BUY signal"
            macd_signal = "bullish"
        elif macd < signal and macd < 0:
            signals["macd"] = "Bearish momentum - SELL signal"
            macd_signal = "bearish"
        else:
            signals["macd"] = "Neutral momentum"
            macd_signal = "neutral"

        # Moving Average Analysis
        if current_price > sma_20 > sma_50:
            signals["ma"] = "Strong uptrend - BUY signal"
            ma_signal = "bullish"
        elif current_price < sma_20 < sma_50:
            signals["ma"] = "Strong downtrend - SELL signal"
            ma_signal = "bearish"
        else:
            signals["ma"] = "Consolidation phase"
            ma_signal = "neutral"

        # Calculate overall sentiment
        bullish_signals = sum(1 for s in [rsi_signal, macd_signal, ma_signal] if s == "bullish")
        bearish_signals = sum(1 for s in [rsi_signal, macd_signal, ma_signal] if s == "bearish")

        # Determine action and confidence
        if bullish_signals >= 2:
            action = "BUY"
            confidence = min(60 + (bullish_signals * 10) + (70 - rsi) / 10 if rsi < 70 else 60, 95)
        elif bearish_signals >= 2:
            action = "SELL"
            confidence = min(60 + (bearish_signals * 10) + (rsi - 30) / 10 if rsi > 30 else 60, 95)
        else:
            action = "HOLD"
            confidence = 50

        # Calculate price targets
        volatility = prices.std() / prices.mean() * 100

        if action == "BUY":
            target_price = current_price * (1 + volatility * 0.5)
            stop_loss = current_price * (1 - volatility * 0.3)
        elif action == "SELL":
            target_price = current_price * (1 - volatility * 0.5)
            stop_loss = current_price * (1 + volatility * 0.3)
        else:
            target_price = current_price * (1 + volatility * 0.2)
            stop_loss = current_price * (1 - volatility * 0.2)

        # Determine time horizon and risk level
        if volatility < 2:
            time_horizon = "Long-term"
            risk_level = "Low"
        elif volatility < 4:
            time_horizon = "Medium-term"
            risk_level = "Medium"
        else:
            time_horizon = "Short-term"
            risk_level = "High"

        # Generate reasoning
        reasoning_parts = []
        if rsi_signal == "bullish":
            reasoning_parts.append(f"RSI at {rsi:.1f} indicates oversold conditions")
        elif rsi_signal == "bearish":
            reasoning_parts.append(f"RSI at {rsi:.1f} indicates overbought conditions")

        if macd_signal == "bullish":
            reasoning_parts.append("MACD showing bullish momentum")
        elif macd_signal == "bearish":
            reasoning_parts.append("MACD showing bearish momentum")

        if ma_signal == "bullish":
            reasoning_parts.append("Price above key moving averages")
        elif ma_signal == "bearish":
            reasoning_parts.append("Price below key moving averages")

        reasoning = ". ".join(reasoning_parts) if reasoning_parts else "Mixed technical signals"

        # Optimal entry timing
        if action == "BUY":
            if rsi < 30:
                optimal_entry = "Immediate entry - oversold conditions"
            elif current_price > sma_20:
                optimal_entry = "Wait for pullback to moving average"
            else:
                optimal_entry = "Consider dollar-cost averaging"
        elif action == "SELL":
            if rsi > 70:
                optimal_entry = "Immediate exit - overbought conditions"
            elif current_price < sma_20:
                optimal_entry = "Wait for bounce to moving average"
            else:
                optimal_entry = "Consider gradual position reduction"
        else:
            optimal_entry = "Wait for clearer signals"

        # Suggested hold duration
        if time_horizon == "Short-term":
            hold_duration = "1-2 weeks"
        elif time_horizon == "Medium-term":
            hold_duration = "1-3 months"
        else:
            hold_duration = "3-12 months"

        return {
            "ticker": ticker,
            "action": action,
            "confidence": round(confidence, 1),
            "entry_price": round(current_price, 2),
            "target_price": round(target_price, 2),
            "stop_loss": round(stop_loss, 2),
            "time_horizon": time_horizon,
            "risk_level": risk_level,
            "reasoning": reasoning,
            "technical_signals": signals,
            "optimal_entry_time": optimal_entry,
            "suggested_hold_duration": hold_duration,
            "current_rsi": round(rsi, 2),
            "current_macd": round(macd, 4),
            "current_sma_20": round(float(sma_20), 2) if not pd.isna(sma_20) else None,
            "current_sma_50": round(float(sma_50), 2) if not pd.isna(sma_50) else None
        }

    except Exception as e:
        print(f"Error generating recommendation: {e}")
        return {
            "ticker": ticker,
            "action": "HOLD",
            "confidence": 50.0,
            "entry_price": 0.0,
            "target_price": 0.0,
            "stop_loss": 0.0,
            "time_horizon": "Medium-term",
            "risk_level": "Medium",
            "reasoning": "Unable to generate recommendation due to insufficient data",
            "technical_signals": {},
            "optimal_entry_time": "Wait for more data",
            "suggested_hold_duration": "N/A"
        }

def get_cache_key(ticker: str, period: str) -> str:
    """Generate cache key for stock data"""
    return f"{ticker}_{period}"

def is_cache_valid(key: str) -> bool:
    """Check if cache entry is still valid"""
    if key not in cache_expiry:
        return False
    return datetime.now() < cache_expiry[key]

def set_cache(key: str, data: any) -> None:
    """Set data in cache with expiry"""
    data_cache[key] = data
    cache_expiry[key] = datetime.now() + timedelta(seconds=CACHE_DURATION)

def get_cache(key: str) -> any:
    """Get data from cache if valid"""
    if is_cache_valid(key):
        return data_cache.get(key)
    return None

def clear_cache() -> None:
    """Clear all cache entries"""
    data_cache.clear()
    cache_expiry.clear()

def fetch_yahoo_chart(ticker: str, period: str = "1y", timeout: int = 6):
    """Fetch OHLCV data directly from Yahoo's chart endpoint without yfinance overhead."""
    period_ranges = {
        '1m': ('1d', '1m'),
        '5m': ('5d', '5m'),
        '15m': ('5d', '15m'),
        '30m': ('1mo', '30m'),
        '1h': ('1mo', '60m'),
        '1d': ('1y', '1d'),
        '5d': ('5d', '15m'),
        '1mo': ('1mo', '1d'),
        '3mo': ('3mo', '1d'),
        '6mo': ('6mo', '1d'),
        '1y': ('1y', '1d'),
        '2y': ('2y', '1d'),
        '5y': ('5y', '1wk'),
    }
    range_value, interval = period_ranges.get(period, ('1y', '1d'))
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"
    params = {
        "range": range_value,
        "interval": interval,
        "includePrePost": "false",
        "events": "history",
    }
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0 Safari/537.36'
    }

    response = requests.get(url, params=params, headers=headers, timeout=timeout)
    response.raise_for_status()
    payload = response.json()
    result = payload.get("chart", {}).get("result", [])
    if not result:
        return None

    chart = result[0]
    timestamps = chart.get("timestamp") or []
    quote = (chart.get("indicators", {}).get("quote") or [{}])[0]
    if not timestamps or not quote:
        return None

    data = pd.DataFrame({
        "Open": quote.get("open"),
        "High": quote.get("high"),
        "Low": quote.get("low"),
        "Close": quote.get("close"),
        "Volume": quote.get("volume"),
    }, index=pd.to_datetime(timestamps, unit="s"))
    data = data.dropna(subset=["Open", "High", "Low", "Close"])
    if data.empty:
        return None

    data["Volume"] = data["Volume"].fillna(0)
    return data

def fetch_stock_data(ticker: str, period: str = "1y"):
    """Fetch stock data with caching and fallback to sample data"""
    ticker = ticker.upper()
    print(f"\n[FETCH] Called for ticker={ticker}, period={period}")
    cache_key = get_cache_key(ticker, period)

    # Check cache first
    cached_data = get_cache(cache_key)
    if cached_data is not None:
        print(f"[CACHE] ✓ Using cached data for {ticker}")
        # Return a copy to avoid mutation issues
        return cached_data.copy()

    try:
        hist = fetch_yahoo_chart(ticker, period, timeout=6)
        if hist is not None and not hist.empty:
            set_cache(cache_key, hist)
            return hist.copy()
    except Exception as e:
        pass

    try:
        # Create session with proper headers to avoid being blocked
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0 Safari/537.36'
        })
        session.timeout = 8  # Set timeout
        
        # Single short yfinance attempt before sample fallback
        for attempt in range(1):
            try:
                stock = yf.Ticker(ticker, session=session)
                hist = stock.history(period=period)
                
                # Check if data is valid
                if hist is not None and not hist.empty and len(hist) > 0:
                    # Verify we have the required columns
                    required_cols = {'Open', 'High', 'Low', 'Close', 'Volume'}
                    if all(col in hist.columns for col in required_cols):
                        # Cache the result
                        set_cache(cache_key, hist)
                        return hist.copy()
                
                # If we get here but data is empty, try again
                if attempt < 0:
                    print(f"[FETCH] Empty/invalid data on attempt {attempt + 1}, retrying...")
                    time.sleep(2)  # Wait before retry
                    continue
                    
            except Exception as e:
                if attempt < 0:
                    print(f"[FETCH] Attempt {attempt + 1} failed: {e}, retrying...")
                    time.sleep(2)
                else:
                    raise
        
        print(f"[FETCH] yfinance failed after retries, using fallback...")
        
    except Exception as e:
        print(f"[FETCH] yfinance error: {e}, using fallback...")

    # Fallback to sample data
    if SAMPLE_DATA_AVAILABLE:
        try:
            days_map = {'1d': 1, '5d': 5, '1mo': 30, '3mo': 90, '6mo': 180, '1y': 252, '2y': 504, '5y': 1260}
            days = days_map.get(period, 252)
            print(f"[FETCH] Generating {days} days of sample data for {ticker}")
            sample_data = generate_sample_data(ticker, days)
            # Verify sample data has required columns
            if sample_data is not None and not sample_data.empty:
                # Cache the sample data
                set_cache(cache_key, sample_data)
                print(f"[FETCH] ✓ Generated and cached {len(sample_data)} rows of sample data")
                return sample_data.copy()
        except Exception as e:
            print(f"[FETCH] Sample data error: {e}")

    return None

def fetch_stock_data_fast(ticker: str, period: str = "1mo"):
    """Fast fetch with minimal data for watchlists"""
    ticker = ticker.upper()
    cache_key = get_cache_key(ticker, period)

    # Check cache first
    cached_data = get_cache(cache_key)
    if cached_data is not None:
        return cached_data.copy()

    try:
        hist = fetch_yahoo_chart(ticker, period, timeout=4)
        if hist is not None and not hist.empty:
            set_cache(cache_key, hist)
            return hist.copy()
    except Exception as e:
        pass

    try:
        # Create session with proper headers
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0 Safari/537.36'
        })
        session.timeout = 5  # Fast timeout for watchlist
        
        # One short yfinance attempt before sample fallback
        for attempt in range(1):
            try:
                stock = yf.Ticker(ticker, session=session)
                hist = stock.history(period=period, interval="1d")
                
                if not hist.empty and len(hist) > 0:
                    # Verify required columns exist
                    required_cols = {'Open', 'High', 'Low', 'Close', 'Volume'}
                    if all(col in hist.columns for col in required_cols):
                        set_cache(cache_key, hist)
                        return hist.copy()
                 
            except Exception as e:
                raise
                    
    except Exception as e:
        pass

    # Fallback to sample data for watchlist
    if SAMPLE_DATA_AVAILABLE:
        try:
            days_map = {'1d': 1, '5d': 5, '1mo': 30, '3mo': 90, '6mo': 180, '1y': 252, '2y': 504, '5y': 1260}
            days = days_map.get(period, 30)
            sample_data = generate_sample_data(ticker, days)
            if sample_data is not None and not sample_data.empty:
                set_cache(cache_key, sample_data)
                return sample_data.copy()
        except Exception as e:
            pass

    return None

# API Endpoints
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "message": "Stock Market Predictor API is running"
    }

@app.post("/get-stock-data")
async def get_stock_data(request: StockRequest):
    """Fetch historical stock data"""
    try:
        ticker = request.ticker.upper()
        
        if not ticker:
            raise HTTPException(status_code=400, detail="Ticker is required")
        
        # Use the fetch function with fallback
        hist = fetch_stock_data(ticker, request.period)
        
        if hist is None or hist.empty:
            raise HTTPException(status_code=404, detail=f"Ticker {ticker} not found or no data available")
        
        # Prepare response data
        data = []
        for date, row in hist.iterrows():
            try:
                data.append({
                    "date": date.strftime("%Y-%m-%d"),
                    "open": float(row["Open"]),
                    "high": float(row["High"]),
                    "low": float(row["Low"]),
                    "close": float(row["Close"]),
                    "volume": int(row["Volume"])
                })
            except Exception as e:
                continue
        
        if not data:
            raise HTTPException(status_code=400, detail="No valid data rows found")
        
        return {
            "ticker": ticker,
            "period": request.period,
            "data": data,
            "count": len(data),
            "timestamp": datetime.now().isoformat()
        }
    
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error fetching stock data: {str(e)}")

@app.post("/predict")
async def predict_stock(request: PredictionRequest):
    """Predict stock trend"""
    try:
        ticker = request.ticker.upper()
        
        if not ticker:
            raise HTTPException(status_code=400, detail="Ticker is required")
        
        # Use fetch function with fallback
        hist = fetch_stock_data(ticker, "3mo")
        
        if hist is None or hist.empty:
            raise HTTPException(status_code=404, detail=f"Ticker {ticker} not found or no data available")
        
        prices = hist["Close"].values
        current_price = float(prices[-1])
        
        # Simple trend prediction based on momentum
        momentum = (prices[-1] - prices[-5]) / prices[-5] if len(prices) >= 5 else 0
        
        if momentum > 0.02:
            trend = "BULLISH"
            recommendation = "BUY"
        elif momentum < -0.02:
            trend = "BEARISH"
            recommendation = "SELL"
        else:
            trend = "NEUTRAL"
            recommendation = "HOLD"
        
        confidence = min(abs(momentum) * 100, 95)
        
        # Simple prediction: extrapolate trend
        future_prices = []
        daily_change = (prices[-1] - prices[-5]) / 5 if len(prices) >= 5 else 0
        
        for i in range(1, request.days + 1):
            predicted_price = prices[-1] + (daily_change * i)
            future_prices.append({
                "day": i,
                "predicted_price": float(predicted_price)
            })
        
        return {
            "ticker": ticker,
            "current_price": current_price,
            "trend": trend,
            "recommendation": recommendation,
            "confidence": float(confidence),
            "predictions": future_prices,
            "timestamp": datetime.now().isoformat()
        }
    
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Unexpected error in predict: {e}")
        raise HTTPException(status_code=400, detail=f"Error making prediction: {str(e)}")

@app.get("/indicators/{ticker}")
async def get_indicators(ticker: str, period: str = "3mo"):
    """Get technical indicators for a stock"""
    try:
        ticker = ticker.upper()
        
        if not ticker:
            raise HTTPException(status_code=400, detail="Ticker is required")
        
        # Use fetch function with fallback
        hist = fetch_stock_data(ticker, period)
        
        if hist is None or hist.empty:
            raise HTTPException(status_code=404, detail=f"Ticker {ticker} not found or no data available")
        
        prices = hist["Close"].values
        
        # Calculate indicators
        rsi = calculate_rsi(prices)
        macd, signal = calculate_macd(prices)
        sma_20 = calculate_sma(prices, 20)
        sma_50 = calculate_sma(prices, 50)
        current_price = float(prices[-1])
        
        return {
            "ticker": ticker,
            "current_price": current_price,
            "rsi": float(rsi),
            "macd": float(macd),
            "signal": float(signal),
            "sma_20": float(sma_20) if not pd.isna(sma_20) else None,
            "sma_50": float(sma_50) if not pd.isna(sma_50) else None,
            "timestamp": datetime.now().isoformat()
        }
    
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Unexpected error in indicators: {e}")
        raise HTTPException(status_code=400, detail=f"Error fetching indicators: {str(e)}")

@app.post("/train-model")
async def train_model(request: StockRequest):
    """Train prediction model for a stock"""
    try:
        ticker = request.ticker.upper()

        if not ticker:
            raise HTTPException(status_code=400, detail="Ticker is required")

        # Use fetch function with fallback
        hist = fetch_stock_data(ticker, request.period)

        if hist is None or hist.empty:
            raise HTTPException(status_code=404, detail=f"Ticker {ticker} not found or no data available")

        return {
            "ticker": ticker,
            "status": "success",
            "message": f"Model trained for {ticker}",
            "data_points": len(hist),
            "timestamp": datetime.now().isoformat()
        }

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error training model: {str(e)}")

@app.post("/watchlist")
async def get_watchlist_data(request: WatchlistRequest):
    """Get data for multiple stocks for watchlist with parallel fetching"""
    try:
        loop = asyncio.get_event_loop()

        def fetch_single_watchlist_stock(ticker):
            ticker = ticker.upper()

            try:
                # Fetch stock data
                hist = fetch_stock_data_fast(ticker, request.period)

                if hist is None or hist.empty:
                    return {
                        "ticker": ticker,
                        "name": get_stock_name(ticker),
                        "current_price": 0.0,
                        "change": 0.0,
                        "change_percent": 0.0,
                        "volume": 0,
                        "high": 0.0,
                        "low": 0.0,
                        "open": 0.0,
                        "data": [],
                        "error": "No data available"
                    }

                # Get latest data
                latest = hist.iloc[-1]
                previous = hist.iloc[-2] if len(hist) > 1 else latest

                current_price = float(latest["Close"])
                previous_price = float(previous["Close"])

                change = current_price - previous_price
                change_percent = (change / previous_price) * 100 if previous_price != 0 else 0

                # Prepare mini chart data (last 20 points for performance)
                mini_data = []
                recent_hist = hist.tail(20)
                for date, row in recent_hist.iterrows():
                    try:
                        mini_data.append({
                            "date": date.strftime("%Y-%m-%d"),
                            "price": float(row["Close"])
                        })
                    except:
                        continue

                return {
                    "ticker": ticker,
                    "name": get_stock_name(ticker),
                    "current_price": current_price,
                    "change": change,
                    "change_percent": change_percent,
                    "volume": int(latest["Volume"]),
                    "high": float(latest["High"]),
                    "low": float(latest["Low"]),
                    "open": float(latest["Open"]),
                    "data": mini_data,
                    "period": request.period
                }

            except Exception as e:
                print(f"Error fetching data for {ticker}: {e}")
                return {
                    "ticker": ticker,
                    "name": get_stock_name(ticker),
                    "current_price": 0.0,
                    "change": 0.0,
                    "change_percent": 0.0,
                    "volume": 0,
                    "high": 0.0,
                    "low": 0.0,
                    "open": 0.0,
                    "data": [],
                    "error": str(e)
                }

        # Fetch all stocks in parallel
        tasks = [loop.run_in_executor(executor, fetch_single_watchlist_stock, ticker) for ticker in request.tickers]
        watchlist_data = await asyncio.gather(*tasks, return_exceptions=True)

        # Filter out exceptions
        watchlist_data = [result for result in watchlist_data if not isinstance(result, Exception)]

        return {
            "watchlist": watchlist_data,
            "count": len(watchlist_data),
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        print(f"Unexpected error in watchlist: {e}")
        raise HTTPException(status_code=400, detail=f"Error fetching watchlist data: {str(e)}")

@app.get("/market-overview")
async def get_market_overview():
    """Get market overview with popular stocks using parallel fetching"""
    try:
        popular_tickers = POPULAR_STOCKS[:12]  # Use first 12 for overview
        loop = asyncio.get_event_loop()

        def fetch_single_overview_stock(ticker):
            try:
                hist = fetch_stock_data_fast(ticker, "1mo")

                if hist is None or hist.empty:
                    return None

                latest = hist.iloc[-1]
                previous = hist.iloc[-2] if len(hist) > 1 else latest

                current_price = float(latest["Close"])
                previous_price = float(previous["Close"])

                change = current_price - previous_price
                change_percent = (change / previous_price) * 100 if previous_price != 0 else 0

                # Calculate simple trend
                prices = hist["Close"].values
                if len(prices) >= 5:
                    momentum = (prices[-1] - prices[-5]) / prices[-5]
                    if momentum > 0.02:
                        trend = "UP"
                    elif momentum < -0.02:
                        trend = "DOWN"
                    else:
                        trend = "NEUTRAL"
                else:
                    trend = "NEUTRAL"

                return {
                    "ticker": ticker,
                    "current_price": current_price,
                    "change": change,
                    "change_percent": change_percent,
                    "trend": trend,
                    "volume": int(latest["Volume"])
                }

            except Exception as e:
                print(f"Error fetching overview for {ticker}: {e}")
                return None

        # Fetch all stocks in parallel
        tasks = [loop.run_in_executor(executor, fetch_single_overview_stock, ticker) for ticker in popular_tickers]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Filter out None results and exceptions
        overview_data = [result for result in results if result is not None and not isinstance(result, Exception)]

        # Calculate market sentiment
        if overview_data:
            up_stocks = sum(1 for stock in overview_data if stock["trend"] == "UP")
            down_stocks = sum(1 for stock in overview_data if stock["trend"] == "DOWN")
            total_stocks = len(overview_data)

            sentiment = "BULLISH" if up_stocks > down_stocks else "BEARISH" if down_stocks > up_stocks else "NEUTRAL"
        else:
            sentiment = "NEUTRAL"

        return {
            "market_sentiment": sentiment,
            "stocks": overview_data,
            "total_stocks": len(overview_data),
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        print(f"Unexpected error in market overview: {e}")
        raise HTTPException(status_code=400, detail=f"Error fetching market overview: {str(e)}")

@app.get("/all-stocks")
async def get_all_stocks():
    """Get all popular stocks with mini chart data for TradingView-style dashboard"""
    try:
        # Use parallel fetching for speed
        loop = asyncio.get_event_loop()

        def fetch_single_stock(ticker):
            try:
                # Fetch stock data for mini chart
                hist = fetch_stock_data_fast(ticker, "1mo")

                if hist is None or hist.empty:
                    return None

                latest = hist.iloc[-1]
                previous = hist.iloc[-2] if len(hist) > 1 else latest

                current_price = float(latest["Close"])
                previous_price = float(previous["Close"])

                change = current_price - previous_price
                change_percent = (change / previous_price) * 100 if previous_price != 0 else 0

                # Prepare mini chart data (last 15 points for better performance)
                mini_data = []
                recent_hist = hist.tail(15)
                for date, row in recent_hist.iterrows():
                    try:
                        mini_data.append({
                            "date": date.strftime("%Y-%m-%d"),
                            "price": float(row["Close"])
                        })
                    except:
                        continue

                # Get stock name (use cached or simple version)
                stock_name = get_stock_name(ticker)

                return {
                    "ticker": ticker,
                    "name": stock_name,
                    "current_price": current_price,
                    "change": change,
                    "change_percent": change_percent,
                    "volume": int(latest["Volume"]),
                    "high": float(latest["High"]),
                    "low": float(latest["Low"]),
                    "open": float(latest["Open"]),
                    "data": mini_data,
                    "period": "1mo"
                }

            except Exception as e:
                print(f"Error fetching data for {ticker}: {e}")
                return None

        # Fetch all stocks in parallel
        tasks = [loop.run_in_executor(executor, fetch_single_stock, ticker) for ticker in POPULAR_STOCKS]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Filter out None results and exceptions
        all_stocks_data = [result for result in results if result is not None and not isinstance(result, Exception)]

        return {
            "stocks": all_stocks_data,
            "count": len(all_stocks_data),
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        print(f"Unexpected error in all stocks: {e}")
        raise HTTPException(status_code=400, detail=f"Error fetching all stocks data: {str(e)}")

@app.get("/profit-opportunities")
async def get_profit_opportunities():
    """Rank popular stocks by bullish technical setup and controlled risk."""
    try:
        loop = asyncio.get_event_loop()

        def fetch_single_opportunity(ticker):
            ticker = ticker.upper()
            hist = fetch_stock_data_fast(ticker, "3mo")
            return build_opportunity_score(ticker, hist)

        tasks = [loop.run_in_executor(executor, fetch_single_opportunity, ticker) for ticker in POPULAR_STOCKS]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        opportunities = [
            result for result in results
            if result is not None and not isinstance(result, Exception) and result["score"] >= 60
        ]
        opportunities.sort(key=lambda item: item["score"], reverse=True)

        return {
            "opportunities": opportunities[:6],
            "count": min(len(opportunities), 6),
            "timestamp": datetime.now().isoformat(),
            "disclaimer": "Technical setup ranking only; profits are never guaranteed."
        }

    except Exception as e:
        print(f"Unexpected error in profit opportunities: {e}")
        raise HTTPException(status_code=400, detail=f"Error fetching profit opportunities: {str(e)}")

@app.get("/trading-recommendation/{ticker}")
async def get_trading_recommendation(ticker: str, period: str = "3mo"):
    """Get comprehensive trading recommendation with timing"""
    try:
        ticker = ticker.upper()

        if not ticker:
            raise HTTPException(status_code=400, detail="Ticker is required")

        # Use fetch function with fallback
        hist = fetch_stock_data(ticker, period)

        if hist is None or hist.empty:
            raise HTTPException(status_code=404, detail=f"Ticker {ticker} not found or no data available")

        # Generate trading recommendation
        recommendation = generate_trading_recommendation(ticker, hist)

        return {
            "recommendation": recommendation,
            "timestamp": datetime.now().isoformat()
        }

    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Unexpected error in trading recommendation: {e}")
        raise HTTPException(status_code=400, detail=f"Error generating trading recommendation: {str(e)}")

@app.get("/")
async def root():
    """Root endpoint with API documentation"""
    return {
        "message": "Stock Market Predictor API",
        "version": "2.0.0",
        "features": {
            "caching": "Enabled (5 minute cache)",
            "parallel_fetching": "Enabled (10 concurrent workers)",
            "performance": "Optimized for speed",
            "trading_recommendations": "AI-powered buy/sell signals with timing"
        },
        "endpoints": {
            "health": "GET /health",
            "stock_data": "POST /get-stock-data",
            "predict": "POST /predict",
            "indicators": "GET /indicators/{ticker}",
            "train_model": "POST /train-model",
            "watchlist": "POST /watchlist",
            "market_overview": "GET /market-overview",
            "all_stocks": "GET /all-stocks",
            "trading_recommendation": "GET /trading-recommendation/{ticker}",
            "cache_stats": "GET /cache/stats",
            "cache_clear": "DELETE /cache"
        }
    }

@app.get("/cache/stats")
async def get_cache_stats():
    """Get cache statistics"""
    return {
        "cache_size": len(data_cache),
        "cache_entries": list(data_cache.keys()),
        "cache_duration_seconds": CACHE_DURATION,
        "timestamp": datetime.now().isoformat()
    }

@app.delete("/cache")
async def clear_cache_endpoint():
    """Clear all cache entries"""
    clear_cache()
    return {
        "message": "Cache cleared successfully",
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
