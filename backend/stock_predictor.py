"""
Stock Predictor - ML models for stock price prediction
"""

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
import joblib
from pathlib import Path
from typing import Tuple, Dict

class StockPredictor:
    def __init__(self, model_dir: str = "models"):
        self.model_dir = Path(model_dir)
        self.model_dir.mkdir(exist_ok=True)
        self.scaler = StandardScaler()
        self.model = None
    
    def prepare_features(self, data: pd.DataFrame, lookback: int = 20) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare features from historical data"""
        X, y = [], []
        prices = data['Close'].values
        
        for i in range(len(prices) - lookback):
            X.append(prices[i:i+lookback])
            y.append(prices[i+lookback])
        
        return np.array(X), np.array(y)
    
    def train_model(self, ticker: str, data: pd.DataFrame, lookback: int = 20) -> Dict:
        """Train prediction model"""
        try:
            X, y = self.prepare_features(data, lookback)
            
            if len(X) < 10:
                return {"status": "error", "message": "Insufficient data"}
            
            # Scale features
            X_scaled = self.scaler.fit_transform(X)
            
            # Train model
            self.model = RandomForestRegressor(n_estimators=100, random_state=42)
            self.model.fit(X_scaled, y)
            
            # Save model
            model_path = self.model_dir / f"{ticker}_model.joblib"
            scaler_path = self.model_dir / f"{ticker}_scaler.joblib"
            joblib.dump(self.model, model_path)
            joblib.dump(self.scaler, scaler_path)
            
            # Calculate R² score
            train_score = self.model.score(X_scaled, y)
            
            return {
                "status": "success",
                "ticker": ticker,
                "model_score": float(train_score),
                "samples_used": len(X)
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def predict_trend(self, ticker: str, recent_prices: np.ndarray, days: int = 5) -> Dict:
        """Predict future trend"""
        try:
            # Load model if exists
            model_path = self.model_dir / f"{ticker}_model.joblib"
            scaler_path = self.model_dir / f"{ticker}_scaler.joblib"
            
            if model_path.exists() and scaler_path.exists():
                self.model = joblib.load(model_path)
                self.scaler = joblib.load(scaler_path)
            
            predictions = []
            current_sequence = recent_prices[-20:] if len(recent_prices) >= 20 else recent_prices
            
            for _ in range(days):
                if len(current_sequence) >= 20:
                    X = current_sequence[-20:].reshape(1, -1)
                    X_scaled = self.scaler.transform(X)
                    next_price = self.model.predict(X_scaled)[0] if self.model else current_sequence[-1]
                else:
                    next_price = current_sequence[-1]
                
                predictions.append(float(next_price))
                current_sequence = np.append(current_sequence, next_price)[-20:]
            
            return {
                "status": "success",
                "ticker": ticker,
                "current_price": float(recent_prices[-1]),
                "predictions": predictions
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def evaluate_model(self, ticker: str, test_data: np.ndarray) -> Dict:
        """Evaluate model performance"""
        try:
            if self.model is None:
                return {"status": "error", "message": "Model not loaded"}
            
            X, y = self.prepare_features(pd.DataFrame({"Close": test_data}))
            X_scaled = self.scaler.transform(X)
            score = self.model.score(X_scaled, y)
            
            return {
                "status": "success",
                "ticker": ticker,
                "test_score": float(score)
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
