import React, { useState, useEffect, useCallback } from 'react';
import StockChart from '../components/StockChart';
import SearchBar from '../components/SearchBar';
import IndicatorPanel from '../components/IndicatorPanel';
import StockWatchlist from '../components/StockWatchlist';
import TradingViewGrid from '../components/TradingViewGrid';
import TradingRecommendation from '../components/TradingRecommendation';
import ProfitOpportunities from '../components/ProfitOpportunities';
import '../styles/Dashboard.css';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
const TIMEFRAMES = [
  { value: '1m', label: '1 Min' },
  { value: '5m', label: '5 Min' },
  { value: '15m', label: '15 Min' },
  { value: '1h', label: '1 Hr' },
  { value: '1d', label: '1 Day' },
  { value: '1mo', label: '1 Month' },
];

function Dashboard({ defaultTicker, onTickerChange, onStockSelect, isPredictionPage = false }) {
  const normalizedDefaultTicker = defaultTicker ? defaultTicker.toUpperCase() : '';
  const [ticker, setTicker] = useState(normalizedDefaultTicker);
  const [selectedTimeframe, setSelectedTimeframe] = useState('1d');
  const [loading, setLoading] = useState(false);
  const [chartData, setChartData] = useState(null);
  const [indicators, setIndicators] = useState(null);
  const [error, setError] = useState(null);

  const handleLoadStock = useCallback(async (newTicker, timeframeOverride) => {
    if (!newTicker) return;
    
    const upperTicker = newTicker.toUpperCase();
    const activeTimeframe = timeframeOverride || selectedTimeframe;
    setTicker(upperTicker);
    setLoading(true);
    setError(null);
    
    // Aggressively clear all data when switching tickers
    setChartData(null);
    setIndicators(null);
    
    try {
      // Fetch chart data
      const dataRes = await fetch(`${API_URL}/get-stock-data`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ticker: upperTicker, period: activeTimeframe })
      });
      
      if (!dataRes.ok) {
        const errText = await dataRes.text();
        throw new Error(`Backend error: ${dataRes.status} - ${errText}`);
      }
      
      const dataJson = await dataRes.json();
      
      // Verify ticker matches
      if (dataJson.ticker.toUpperCase() !== upperTicker) {
        throw new Error(`Ticker mismatch: requested ${upperTicker}, got ${dataJson.ticker}`);
      }
      
      setChartData(dataJson);
      setLoading(false);
      onTickerChange(upperTicker);
      
      // Fetch indicators in background
      Promise.allSettled([
        fetch(`${API_URL}/indicators/${upperTicker}?period=${activeTimeframe}`)
          .then(res => res.ok ? res.json() : null)
          .then(json => json && setIndicators(json))
      ]);
      
    } catch (err) {
      setError(err.message || 'Connection failed. Is backend running?');
      setLoading(false);
    }
  }, [onTickerChange, selectedTimeframe]);

  useEffect(() => {
    if (normalizedDefaultTicker) {
      setTicker(normalizedDefaultTicker);
    }
  }, [normalizedDefaultTicker]);

  // Auto-load selected dashboard stock when entering prediction mode.
  useEffect(() => {
    if (isPredictionPage && normalizedDefaultTicker) {
      handleLoadStock(normalizedDefaultTicker);
    }
  }, [handleLoadStock, isPredictionPage, normalizedDefaultTicker]);

  const handleWatchlistSelect = (selectedTicker) => {
    if (isPredictionPage) {
      handleLoadStock(selectedTicker);
    } else {
      if (onStockSelect) {
        onStockSelect(selectedTicker);
      }
    }
  };

  return (
    <div className="dashboard">
      {isPredictionPage && (
        <div className="prediction-page-header">
          <h2>📊 Detailed Analysis: {ticker}</h2>
          <p>AI-powered prediction and technical indicators</p>
        </div>
      )}

      <SearchBar onSearch={handleLoadStock} currentTicker={ticker} />

      <div className="timeframe-selector" aria-label="Chart timeframe">
        {TIMEFRAMES.map((timeframe) => (
          <button
            key={timeframe.value}
            type="button"
            className={`timeframe-button ${selectedTimeframe === timeframe.value ? 'active' : ''}`}
            onClick={() => {
              setSelectedTimeframe(timeframe.value);
              if (!isPredictionPage && chartData) {
                handleLoadStock(ticker, timeframe.value);
              }
            }}
          >
            {timeframe.label}
          </button>
        ))}
      </div>

      {error && <div className="error-banner">{error}</div>}

      {isPredictionPage ? (
        // Prediction Page - Show detailed view for single stock
        <>
          {loading ? (
            <div className="loader">Loading prediction data...</div>
          ) : (
            <>
              {chartData && (
                <div className="dashboard-grid" key={`pred-${chartData.ticker}`}>
                  <div className="chart-section">
                    <StockChart data={chartData} />
                    {indicators && <IndicatorPanel indicators={indicators} />}
                  </div>

                  <div className="side-panel">
                    <TradingRecommendation ticker={ticker} period={selectedTimeframe} />
                  </div>
                </div>
              )}
              {!chartData && !loading && (
                <div className="loader">
                  Click on a stock to view detailed prediction analysis
                </div>
              )}
            </>
          )}
        </>
      ) : (
        // Dashboard Page - Show TradingView grid and watchlist
        <>
          {loading ? (
            <div className="loader">Loading chart...</div>
          ) : (
            <>
              {chartData && (
                <div className="dashboard-grid" key={`dash-${chartData.ticker}`}>
                  <div className="chart-section">
                    <StockChart data={chartData} />
                    {indicators && <IndicatorPanel indicators={indicators} />}
                  </div>
                </div>
              )}
            </>
          )}

          <ProfitOpportunities onStockSelect={handleWatchlistSelect} />

          {/* TradingView-style Market Overview */}
          <TradingViewGrid onStockSelect={handleWatchlistSelect} />

          {/* Market Watchlist */}
          <StockWatchlist onStockSelect={handleWatchlistSelect} />
        </>
      )}
    </div>
  );
}

export default Dashboard;
