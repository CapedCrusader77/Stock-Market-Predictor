import React from 'react';
import '../styles/PredictionCard.css';

function PredictionCard({ prediction }) {
  if (!prediction) {
    return <div className="prediction-card">Loading prediction...</div>;
  }

  const isBullish = prediction.trend === 'BULLISH';
  const isNeutral = prediction.trend === 'NEUTRAL';
  const confidence = prediction.confidence || 0;
  const currentPrice = prediction.current_price || 0;
  const recommendation = prediction.recommendation || 'HOLD';
  
  return (
    <div className={`prediction-card ${isBullish ? 'up' : isNeutral ? 'neutral' : 'down'}`}>
      <h3>AI Prediction</h3>
      
      <div className="trend-display">
        <div className="trend-arrow">
          {isBullish ? '📈' : isNeutral ? '➡️' : '📉'}
        </div>
        <div className="trend-text">
          <span className="trend-label">Predicted Trend</span>
          <span className={`trend-value ${isBullish ? 'up-trend' : isNeutral ? 'neutral-trend' : 'down-trend'}`}>
            {prediction.trend}
          </span>
        </div>
      </div>

      <div className="recommendation-box">
        <span className="rec-label">Recommendation:</span>
        <span className={`rec-value ${recommendation.toLowerCase()}`}>
          {recommendation}
        </span>
      </div>
      
      <div className="confidence-bar">
        <div className="confidence-label">Confidence</div>
        <div className="bar-container">
          <div 
            className="bar-fill"
            style={{ width: `${Math.min(confidence, 100)}%` }}
          ></div>
        </div>
        <span className="confidence-value">{confidence.toFixed(1)}%</span>
      </div>
      
      <div className="prediction-footer">
        <span>Current Price: ${currentPrice.toFixed(2)}</span>
      </div>
    </div>
  );
}

export default PredictionCard;
