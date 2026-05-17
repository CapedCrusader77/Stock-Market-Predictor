"""
Data Pipeline - Fetch, process, and cache stock data
"""

import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Tuple

class DataPipeline:
    def __init__(self, cache_dir: str = "data"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
    
    def fetch_stock_data(self, ticker: str, period: str = "1y") -> pd.DataFrame:
        """Fetch historical stock data from yfinance"""
        try:
            # Add user agent to avoid being blocked by yfinance servers
            yf.pdr_read.get_data_yahoo.defaults['user_agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            
            stock = yf.Ticker(ticker, session=None)
            data = stock.history(period=period)
            
            if data.empty:
                raise ValueError(f"No data found for ticker {ticker}")
            
            # Cache the data
            cache_file = self.cache_dir / f"{ticker}_{period}.csv"
            data.to_csv(cache_file)
            
            return data
        except Exception as e:
            raise Exception(f"Error fetching data for {ticker}: {str(e)}")
    
    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate technical indicators"""
        try:
            df = data.copy()
            prices = df['Close'].values
            
            # Simple Moving Averages
            df['SMA_20'] = pd.Series(prices).rolling(window=20).mean()
            df['SMA_50'] = pd.Series(prices).rolling(window=50).mean()
            df['SMA_200'] = pd.Series(prices).rolling(window=200).mean()
            
            # Exponential Moving Average
            df['EMA_12'] = pd.Series(prices).ewm(span=12).mean()
            df['EMA_26'] = pd.Series(prices).ewm(span=26).mean()
            
            # MACD
            df['MACD'] = df['EMA_12'] - df['EMA_26']
            df['Signal'] = df['MACD'].ewm(span=9).mean()
            df['MACD_Hist'] = df['MACD'] - df['Signal']
            
            # RSI
            df['RSI'] = self.calculate_rsi(prices)
            
            # Bollinger Bands
            df['BB_Middle'] = df['SMA_20']
            std = pd.Series(prices).rolling(window=20).std()
            df['BB_Upper'] = df['BB_Middle'] + (std * 2)
            df['BB_Lower'] = df['BB_Middle'] - (std * 2)
            
            return df
        except Exception as e:
            raise Exception(f"Error calculating indicators: {str(e)}")
    
    def calculate_rsi(self, prices: np.ndarray, period: int = 14) -> np.ndarray:
        """Calculate RSI"""
        deltas = np.diff(prices)
        seed = deltas[:period+1]
        up = seed[seed >= 0].sum() / period
        down = -seed[seed < 0].sum() / period
        rs = up / down if down != 0 else 0
        rsi = np.zeros_like(prices, dtype=float)
        rsi[:period] = 100. - 100. / (1. + rs)
        
        for i in range(period, len(prices)):
            delta = deltas[i-1]
            upval = delta if delta > 0 else 0.
            downval = -delta if delta < 0 else 0.
            
            up = (up * (period - 1) + upval) / period
            down = (down * (period - 1) + downval) / period
            rs = up / down if down != 0 else 0
            rsi[i] = 100. - 100. / (1. + rs)
        
        return rsi
    
    def prepare_features(self, data: pd.DataFrame, lookback: int = 20) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare features for ML model"""
        try:
            X, y = [], []
            prices = data['Close'].values
            
            for i in range(len(prices) - lookback):
                X.append(prices[i:i+lookback])
                y.append(prices[i+lookback])
            
            return np.array(X), np.array(y)
        except Exception as e:
            raise Exception(f"Error preparing features: {str(e)}")
    
    def load_cached_data(self, ticker: str, period: str = "1y") -> pd.DataFrame:
        """Load cached stock data if available"""
        cache_file = self.cache_dir / f"{ticker}_{period}.csv"
        
        if cache_file.exists():
            return pd.read_csv(cache_file, index_col=0, parse_dates=True)
        
        return None
