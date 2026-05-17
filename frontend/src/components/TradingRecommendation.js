import React, { useState, useEffect, useCallback } from 'react';
import '../styles/TradingRecommendation.css';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

function TradingRecommendation({ ticker, period = '3mo' }) {
  const [recommendation, setRecommendation] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchRecommendation = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await fetch(`${API_URL}/trading-recommendation/${ticker}?period=${period}`);

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }

      const json = await response.json();
      setRecommendation(json.recommendation);
    } catch (err) {
      console.error('Error fetching trading recommendation:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [ticker, period]);

  useEffect(() => {
    if (ticker) {
      fetchRecommendation();
    }
  }, [fetchRecommendation, ticker]);

  const getActionColor = (action) => {
    switch (action) {
      case 'BUY':
        return '#26a69a';
      case 'SELL':
        return '#ef5350';
      default:
        return '#666666';
    }
  };

  const getRiskColor = (risk) => {
    switch (risk) {
      case 'Low':
        return '#26a69a';
      case 'Medium':
        return '#ffa726';
      case 'High':
        return '#ef5350';
      default:
        return '#666666';
    }
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

  if (loading) {
    return (
      <div className="trading-recommendation">
        <div className="tr-loading">
          <div className="tr-spinner"></div>
          <span>Analyzing market conditions...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="trading-recommendation">
        <div className="tr-error">
          <span>⚠️</span>
          <p>{error}</p>
          <button onClick={fetchRecommendation} className="tr-retry-button">
            Retry
          </button>
        </div>
      </div>
    );
  }

  if (!recommendation) {
    return null;
  }

  const { action, confidence, entry_price, target_price, stop_loss,
         time_horizon, risk_level, reasoning, technical_signals,
         optimal_entry_time, suggested_hold_duration } = recommendation;

  return (
    <div className="trading-recommendation">
      <div className="tr-header">
        <h3>🎯 Trading Recommendation</h3>
        <div className="tr-ticker">{ticker}</div>
      </div>

      <div className="tr-action-section">
        <div
          className="tr-action-badge"
          style={{ backgroundColor: getActionColor(action) }}
        >
          {action}
        </div>
        <div className="tr-confidence">
          <span className="tr-confidence-label">Confidence:</span>
          <span className="tr-confidence-value">{confidence}%</span>
        </div>
      </div>

      <div className="tr-price-targets">
        <div className="tr-price-item">
          <span className="tr-price-label">Entry Price</span>
          <span className="tr-price-value">{formatPrice(entry_price)}</span>
        </div>
        <div className="tr-price-item tr-target">
          <span className="tr-price-label">Target Price</span>
          <span className="tr-price-value tr-positive">{formatPrice(target_price)}</span>
        </div>
        <div className="tr-price-item tr-stop">
          <span className="tr-price-label">Stop Loss</span>
          <span className="tr-price-value tr-negative">{formatPrice(stop_loss)}</span>
        </div>
      </div>

      <div className="tr-timing-section">
        <div className="tr-timing-item">
          <span className="tr-timing-label">⏰ Optimal Entry</span>
          <span className="tr-timing-value">{optimal_entry_time}</span>
        </div>
        <div className="tr-timing-item">
          <span className="tr-timing-label">📅 Hold Duration</span>
          <span className="tr-timing-value">{suggested_hold_duration}</span>
        </div>
        <div className="tr-timing-item">
          <span className="tr-timing-label">⏱️ Time Horizon</span>
          <span className="tr-timing-value">{time_horizon}</span>
        </div>
      </div>

      <div className="tr-risk-section">
        <div className="tr-risk-item">
          <span className="tr-risk-label">Risk Level</span>
          <span
            className="tr-risk-value"
            style={{ color: getRiskColor(risk_level) }}
          >
            {risk_level}
          </span>
        </div>
      </div>

      <div className="tr-reasoning">
        <h4>📊 Analysis</h4>
        <p>{reasoning}</p>
      </div>

      <div className="tr-signals">
        <h4>📈 Technical Signals</h4>
        <div className="tr-signals-grid">
          {Object.entries(technical_signals).map(([key, signal]) => (
            <div key={key} className="tr-signal-item">
              <span className="tr-signal-key">{key.toUpperCase()}</span>
              <span className="tr-signal-value">{signal}</span>
            </div>
          ))}
        </div>
      </div>

      <button onClick={fetchRecommendation} className="tr-refresh-button">
        🔄 Refresh Analysis
      </button>
    </div>
  );
}

export default TradingRecommendation;
