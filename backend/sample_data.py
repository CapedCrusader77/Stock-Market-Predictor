"""
Sample stock data generator for testing when yfinance fails
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_sample_data(ticker="AAPL", days=252):
    """Generate sample historical stock data"""
    # Generate random prices that look realistic
    seed = hash(ticker) % 2**32
    np.random.seed(seed)
    
    dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
    
    # Start with a base price
    base_prices = {
        'AAPL': 180,
        'GOOGL': 140,
        'MSFT': 420,
        'AMZN': 180,
        'TSLA': 240,
        'META': 320,
        'NVDA': 900,
        'JPM': 190
    }
    
    base_price = base_prices.get(ticker, 100)
    
    # Generate realistic price movement
    returns = np.random.normal(0.0005, 0.02, days)
    prices = base_price * np.exp(np.cumsum(returns))
    
    data = pd.DataFrame({
        'Date': dates,
        'Open': prices * (1 + np.random.uniform(-0.01, 0.01, days)),
        'High': prices * (1 + np.random.uniform(0, 0.03, days)),
        'Low': prices * (1 - np.random.uniform(0, 0.03, days)),
        'Close': prices,
        'Volume': np.random.randint(50000000, 150000000, days)
    })
    
    data.set_index('Date', inplace=True)
    return data

if __name__ == "__main__":
    # Test
    data = generate_sample_data('AAPL')
    print(data.head())
    print(f"\nGenerated {len(data)} rows")
    print(f"Price range: ${data['Close'].min():.2f} - ${data['Close'].max():.2f}")
