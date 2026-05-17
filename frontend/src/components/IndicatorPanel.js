import React from 'react';
import '../styles/IndicatorPanel.css';

function IndicatorPanel({ indicators }) {
  if (!indicators) {
    return (
      <div className="indicator-panel">
        <h3>Technical Indicators</h3>
        <p style={{ color: '#94a3b8', textAlign: 'center', padding: '2rem' }}>
          Loading indicators...
        </p>
      </div>
    );
  }

  const formatValue = (val, decimals = 2) => {
    if (val === null || val === undefined) return 'N/A';
    return parseFloat(val).toFixed(decimals);
  };

  return (
    <div className="indicator-panel">
      <h3>Technical Indicators</h3>
      <div className="indicators-grid">
        <div className="indicator-item">
          <span className="label">Price</span>
          <span className="value">${formatValue(indicators.current_price, 2)}</span>
        </div>
        <div className="indicator-item">
          <span className="label">RSI</span>
          <span className="value">{formatValue(indicators.rsi, 1)}</span>
        </div>
        <div className="indicator-item">
          <span className="label">MACD</span>
          <span className="value">{formatValue(indicators.macd, 4)}</span>
        </div>
        <div className="indicator-item">
          <span className="label">Signal</span>
          <span className="value">{formatValue(indicators.signal, 4)}</span>
        </div>
        <div className="indicator-item">
          <span className="label">MA-20</span>
          <span className="value">${formatValue(indicators.sma_20, 2)}</span>
        </div>
        <div className="indicator-item">
          <span className="label">MA-50</span>
          <span className="value">${formatValue(indicators.sma_50, 2)}</span>
        </div>
      </div>
    </div>
  );
}

export default IndicatorPanel;
