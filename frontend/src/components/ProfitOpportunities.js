import React, { useEffect, useState } from 'react';
import MiniChart from './MiniChart';
import '../styles/ProfitOpportunities.css';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

function ProfitOpportunities({ onStockSelect }) {
  const [opportunities, setOpportunities] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchOpportunities = async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await fetch(`${API_URL}/profit-opportunities`);
      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }

      const json = await response.json();
      setOpportunities(json.opportunities || []);
    } catch (err) {
      console.error('Error fetching profit opportunities:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchOpportunities();
  }, []);

  const formatPrice = (price) => {
    if (price >= 1000) return `$${price.toFixed(0)}`;
    if (price >= 100) return `$${price.toFixed(1)}`;
    return `$${price.toFixed(2)}`;
  };

  const formatPercent = (value) => {
    const sign = value >= 0 ? '+' : '';
    return `${sign}${value.toFixed(2)}%`;
  };

  if (loading) {
    return (
      <section className="profit-opportunities">
        <div className="profit-header">
          <div>
            <h2>Best Trade Setups</h2>
            <p>Finding high-probability technical setups...</p>
          </div>
          <div className="profit-spinner"></div>
        </div>
      </section>
    );
  }

  if (error) {
    return (
      <section className="profit-opportunities">
        <div className="profit-header">
          <div>
            <h2>Best Trade Setups</h2>
            <p>Could not load setup rankings.</p>
          </div>
          <button className="profit-refresh-button" onClick={fetchOpportunities}>
            Retry
          </button>
        </div>
      </section>
    );
  }

  if (opportunities.length === 0) {
    return null;
  }

  return (
    <section className="profit-opportunities">
      <div className="profit-header">
        <div>
          <h2>Best Trade Setups</h2>
          <p>Ranked by trend, RSI, momentum, latest move, and volatility.</p>
        </div>
        <button className="profit-refresh-button" onClick={fetchOpportunities}>
          Refresh
        </button>
      </div>

      <div className="profit-grid">
        {opportunities.map((stock) => (
          <button
            key={stock.ticker}
            className="profit-card"
            onClick={() => onStockSelect && onStockSelect(stock.ticker)}
          >
            <div className="profit-card-top">
              <div>
                <div className="profit-ticker">{stock.ticker}</div>
                <div className="profit-name">{stock.name || stock.ticker}</div>
              </div>
              <div className="profit-score">
                <span>{stock.score.toFixed(1)}</span>
                <small>Score</small>
              </div>
            </div>

            <div className="profit-price-row">
              <span className="profit-price">{formatPrice(stock.current_price)}</span>
              <span className={stock.change_percent >= 0 ? 'profit-change up' : 'profit-change down'}>
                {formatPercent(stock.change_percent)}
              </span>
            </div>

            <div className="profit-chart">
              <MiniChart ticker={stock.ticker} data={stock.data} height={64} />
            </div>

            <div className="profit-metrics">
              <div>
                <span>Target</span>
                <strong>{formatPrice(stock.target_price)}</strong>
              </div>
              <div>
                <span>RSI</span>
                <strong>{stock.rsi.toFixed(1)}</strong>
              </div>
              <div>
                <span>20D</span>
                <strong>{formatPercent(stock.momentum_20d)}</strong>
              </div>
            </div>

            <div className="profit-reasons">
              {stock.reasons.map((reason) => (
                <span key={reason}>{reason}</span>
              ))}
            </div>
          </button>
        ))}
      </div>
    </section>
  );
}

export default ProfitOpportunities;
