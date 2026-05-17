import React, { useState, useEffect } from 'react';
import MiniChart from './MiniChart';
import '../styles/StockWatchlist.css';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const DEFAULT_WATCHLIST = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA', 'META', 'NVDA', 'JPM'];

function StockWatchlist({ onStockSelect }) {
  const [watchlistData, setWatchlistData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedStock, setSelectedStock] = useState(null);

  useEffect(() => {
    fetchWatchlistData();
    // Refresh data every 2 minutes instead of 30 seconds for better performance
    const interval = setInterval(fetchWatchlistData, 120000);
    return () => clearInterval(interval);
  }, []);

  const fetchWatchlistData = async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await fetch(`${API_URL}/watchlist`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          tickers: DEFAULT_WATCHLIST,
          period: '1mo'
        })
      });

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }

      const json = await response.json();
      setWatchlistData(json.watchlist || []);
    } catch (err) {
      console.error('Error fetching watchlist:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleStockClick = (stock) => {
    setSelectedStock(stock.ticker);
    if (onStockSelect) {
      onStockSelect(stock.ticker);
    }
  };

  const formatChange = (change, changePercent) => {
    const sign = change >= 0 ? '+' : '';
    return `${sign}${change.toFixed(2)} (${sign}${changePercent.toFixed(2)}%)`;
  };

  const formatVolume = (volume) => {
    if (volume >= 1000000) {
      return `${(volume / 1000000).toFixed(1)}M`;
    } else if (volume >= 1000) {
      return `${(volume / 1000).toFixed(1)}K`;
    }
    return volume.toString();
  };

  if (loading) {
    return (
      <div className="watchlist-container">
        <div className="watchlist-header">
          <h2>📊 Market Watchlist</h2>
          <div className="refresh-indicator">
            <div className="spinner"></div>
            <span>Loading...</span>
          </div>
        </div>
        <div className="watchlist-loading">
          <div className="loading-skeleton"></div>
          <div className="loading-skeleton"></div>
          <div className="loading-skeleton"></div>
          <div className="loading-skeleton"></div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="watchlist-container">
        <div className="watchlist-header">
          <h2>📊 Market Watchlist</h2>
        </div>
        <div className="watchlist-error">
          <span>⚠️</span>
          <p>{error}</p>
          <button onClick={fetchWatchlistData} className="retry-button">
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="watchlist-container">
      <div className="watchlist-header">
        <h2>📊 Market Watchlist</h2>
        <div className="watchlist-actions">
          <button
            onClick={fetchWatchlistData}
            className="refresh-button"
            title="Refresh data"
          >
            🔄 Refresh
          </button>
        </div>
      </div>

      <div className="watchlist-grid">
        {watchlistData.map((stock) => {
          if (stock.error) {
            return (
              <div
                key={stock.ticker}
                className="watchlist-item error"
              >
                <div className="stock-info">
                  <div className="stock-ticker">{stock.ticker}</div>
                  <div className="stock-error">{stock.error}</div>
                </div>
              </div>
            );
          }

          const isPositive = stock.change >= 0;
          const changeClass = isPositive ? 'positive' : 'negative';

          return (
            <div
              key={stock.ticker}
              className={`watchlist-item ${selectedStock === stock.ticker ? 'selected' : ''}`}
              onClick={() => handleStockClick(stock)}
            >
              <div className="stock-header">
                <div className="stock-identity">
                  <div className="stock-ticker">{stock.ticker}</div>
                  <div className="stock-name">{stock.name || stock.ticker}</div>
                </div>
                <div className={`stock-change ${changeClass}`}>
                  {formatChange(stock.change, stock.change_percent)}
                </div>
              </div>

              <div className="stock-price">
                <span className="current-price">${stock.current_price.toFixed(2)}</span>
              </div>

              <div className="stock-chart">
                <MiniChart
                  ticker={stock.ticker}
                  data={stock.data}
                  height={60}
                />
              </div>

              <div className="stock-details">
                <div className="detail-item">
                  <span className="detail-label">Vol</span>
                  <span className="detail-value">{formatVolume(stock.volume)}</span>
                </div>
                <div className="detail-item">
                  <span className="detail-label">High</span>
                  <span className="detail-value">${stock.high.toFixed(2)}</span>
                </div>
                <div className="detail-item">
                  <span className="detail-label">Low</span>
                  <span className="detail-value">${stock.low.toFixed(2)}</span>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

export default StockWatchlist;