import React, { useState, useEffect } from 'react';
import MiniChart from './MiniChart';
import '../styles/TradingViewGrid.css';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

function TradingViewGrid({ onStockSelect }) {
  const [stocksData, setStocksData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedStock, setSelectedStock] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    fetchAllStocks();
    // Refresh data every 2 minutes instead of 1 minute for better performance
    const interval = setInterval(fetchAllStocks, 120000);
    return () => clearInterval(interval);
  }, []);

  const fetchAllStocks = async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await fetch(`${API_URL}/all-stocks`);

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }

      const json = await response.json();
      setStocksData(json.stocks || []);
    } catch (err) {
      console.error('Error fetching all stocks:', err);
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

  const formatPrice = (price) => {
    if (price >= 1000) {
      return `$${price.toFixed(0)}`;
    } else if (price >= 100) {
      return `$${price.toFixed(1)}`;
    } else {
      return `$${price.toFixed(2)}`;
    }
  };

  const formatVolume = (volume) => {
    if (volume >= 1000000) {
      return `${(volume / 1000000).toFixed(1)}M`;
    } else if (volume >= 1000) {
      return `${(volume / 1000).toFixed(1)}K`;
    }
    return volume.toString();
  };

  const filteredStocks = stocksData.filter(stock =>
    stock.ticker.toLowerCase().includes(searchTerm.toLowerCase()) ||
    (stock.name && stock.name.toLowerCase().includes(searchTerm.toLowerCase()))
  );

  if (loading && stocksData.length === 0) {
    return (
      <div className="tv-grid-container">
        <div className="tv-grid-header">
          <h2>📈 Market Overview</h2>
          <div className="tv-refresh-indicator">
            <div className="tv-spinner"></div>
            <span>Loading market data...</span>
          </div>
        </div>
        <div className="tv-grid-loading">
          {[...Array(8)].map((_, i) => (
            <div key={i} className="tv-stock-card-skeleton">
              <div className="tv-skeleton-header"></div>
              <div className="tv-skeleton-price"></div>
              <div className="tv-skeleton-chart"></div>
              <div className="tv-skeleton-details"></div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (error && stocksData.length === 0) {
    return (
      <div className="tv-grid-container">
        <div className="tv-grid-header">
          <h2>📈 Market Overview</h2>
        </div>
        <div className="tv-grid-error">
          <span>⚠️</span>
          <p>{error}</p>
          <button onClick={fetchAllStocks} className="tv-retry-button">
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="tv-grid-container">
      <div className="tv-grid-header">
        <h2>📈 Market Overview</h2>
        <div className="tv-header-actions">
          <div className="tv-search-box">
            <input
              type="text"
              placeholder="Search stocks..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="tv-search-input"
            />
          </div>
          <button
            onClick={fetchAllStocks}
            className="tv-refresh-button"
            title="Refresh data"
            disabled={loading}
          >
            {loading ? '🔄' : '🔄'} Refresh
          </button>
        </div>
      </div>

      <div className="tv-grid">
        {filteredStocks.map((stock) => {
          if (stock.error) {
            return (
              <div
                key={stock.ticker}
                className="tv-stock-card tv-error-card"
              >
                <div className="tv-stock-info">
                  <div className="tv-stock-ticker">{stock.ticker}</div>
                  <div className="tv-stock-error">{stock.error}</div>
                </div>
              </div>
            );
          }

          const isPositive = stock.change >= 0;
          const changeClass = isPositive ? 'tv-positive' : 'tv-negative';

          return (
            <div
              key={stock.ticker}
              className={`tv-stock-card ${selectedStock === stock.ticker ? 'tv-selected' : ''}`}
              onClick={() => handleStockClick(stock)}
            >
              <div className="tv-stock-header">
                <div className="tv-stock-identity">
                  <div className="tv-stock-ticker">{stock.ticker}</div>
                  <div className="tv-stock-name">{stock.name || stock.ticker}</div>
                </div>
                <div className={`tv-stock-change ${changeClass}`}>
                  {formatChange(stock.change, stock.change_percent)}
                </div>
              </div>

              <div className="tv-stock-price-section">
                <span className="tv-current-price">{formatPrice(stock.current_price)}</span>
                <span className={`tv-price-indicator ${isPositive ? 'tv-up' : 'tv-down'}`}>
                  {isPositive ? '▲' : '▼'}
                </span>
              </div>

              <div className="tv-stock-chart">
                <MiniChart
                  ticker={stock.ticker}
                  data={stock.data}
                  height={80}
                />
              </div>

              <div className="tv-stock-details">
                <div className="tv-detail-item">
                  <span className="tv-detail-label">Vol</span>
                  <span className="tv-detail-value">{formatVolume(stock.volume)}</span>
                </div>
                <div className="tv-detail-item">
                  <span className="tv-detail-label">High</span>
                  <span className="tv-detail-value">{formatPrice(stock.high)}</span>
                </div>
                <div className="tv-detail-item">
                  <span className="tv-detail-label">Low</span>
                  <span className="tv-detail-value">{formatPrice(stock.low)}</span>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {filteredStocks.length === 0 && searchTerm && (
        <div className="tv-no-results">
          <p>No stocks found matching "{searchTerm}"</p>
        </div>
      )}
    </div>
  );
}

export default TradingViewGrid;