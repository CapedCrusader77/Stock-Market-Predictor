"""
Backtester - Backtest trading strategies
"""

import numpy as np
import pandas as pd
from typing import Dict, Tuple

class Backtester:
    def __init__(self, initial_capital: float = 10000):
        self.initial_capital = initial_capital
        self.capital = initial_capital
        self.shares = 0
        self.trades = []
        self.equity_curve = []
    
    def run_backtest(self, prices: np.ndarray, signals: np.ndarray) -> Dict:
        """Run backtest on price data with trading signals"""
        try:
            self.capital = self.initial_capital
            self.shares = 0
            self.trades = []
            self.equity_curve = []
            
            for i, (price, signal) in enumerate(zip(prices, signals)):
                # Buy signal
                if signal == 1 and self.capital > 0:
                    shares_to_buy = self.capital / price
                    self.shares += shares_to_buy
                    self.capital = 0
                    self.trades.append({
                        "day": i,
                        "type": "BUY",
                        "price": price,
                        "shares": shares_to_buy
                    })
                
                # Sell signal
                elif signal == -1 and self.shares > 0:
                    self.capital = self.shares * price
                    self.trades.append({
                        "day": i,
                        "type": "SELL",
                        "price": price,
                        "shares": self.shares
                    })
                    self.shares = 0
                
                # Record equity
                current_equity = self.capital + (self.shares * price)
                self.equity_curve.append(current_equity)
            
            return self.calculate_stats()
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def calculate_stats(self) -> Dict:
        """Calculate backtest statistics"""
        try:
            equity_array = np.array(self.equity_curve)
            
            if len(equity_array) == 0:
                return {"status": "error", "message": "No equity data"}
            
            # Calculate returns
            total_return = (equity_array[-1] - self.initial_capital) / self.initial_capital
            returns = np.diff(equity_array) / equity_array[:-1]
            
            # Calculate metrics
            max_equity = np.max(equity_array)
            min_equity = np.min(equity_array)
            max_drawdown = (max_equity - min_equity) / max_equity if max_equity > 0 else 0
            
            annual_return = (1 + total_return) ** (252 / len(equity_array)) - 1 if len(equity_array) > 0 else 0
            annual_volatility = np.std(returns) * np.sqrt(252) if len(returns) > 0 else 0
            
            sharpe_ratio = annual_return / annual_volatility if annual_volatility > 0 else 0
            
            return {
                "status": "success",
                "initial_capital": self.initial_capital,
                "final_equity": float(equity_array[-1]),
                "total_return": float(total_return),
                "annual_return": float(annual_return),
                "annual_volatility": float(annual_volatility),
                "sharpe_ratio": float(sharpe_ratio),
                "max_drawdown": float(max_drawdown),
                "num_trades": len(self.trades),
                "trades": self.trades[:10]  # Return first 10 trades
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def calculate_returns(self, prices: np.ndarray) -> Dict:
        """Calculate return statistics"""
        try:
            returns = np.diff(prices) / prices[:-1]
            
            return {
                "total_return": float((prices[-1] - prices[0]) / prices[0]),
                "avg_daily_return": float(np.mean(returns)),
                "daily_volatility": float(np.std(returns)),
                "max_price": float(np.max(prices)),
                "min_price": float(np.min(prices))
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def generate_report(self) -> Dict:
        """Generate backtest report"""
        stats = self.calculate_stats()
        
        return {
            "summary": stats,
            "trades": self.trades,
            "equity_curve_length": len(self.equity_curve)
        }
