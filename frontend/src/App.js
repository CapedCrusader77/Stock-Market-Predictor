import React, { useState } from 'react';
import Home from './components/Home';
import Dashboard from './pages/Dashboard';
import './styles/App.css';

function App() {
  const [ticker, setTicker] = useState('AAPL');
  const [currentPage, setCurrentPage] = useState('home');
  const [selectedStock, setSelectedStock] = useState(null);

  const handleGetStarted = () => {
    setCurrentPage('dashboard');
  };

  const handleStockSelect = (stockTicker) => {
    setSelectedStock(stockTicker);
    setTicker(stockTicker);
    setCurrentPage('prediction');
  };

  const handleBackToDashboard = () => {
    setCurrentPage('dashboard');
  };

  return (
    <div className="App">
      <header className="app-header">
        <div className="header-content">
          <div className="logo-section" onClick={() => setCurrentPage('home')} style={{ cursor: 'pointer' }}>
            <h1>📈 Stock Market Prediction</h1>
            <p>AI-powered trend analysis</p>
          </div>
          <nav className="header-nav">
            <button
              className={`nav-btn ${currentPage === 'home' ? 'active' : ''}`}
              onClick={() => setCurrentPage('home')}
            >
              Home
            </button>
            <button
              className={`nav-btn ${currentPage === 'dashboard' ? 'active' : ''}`}
              onClick={() => setCurrentPage('dashboard')}
            >
              Dashboard
            </button>
            {currentPage === 'prediction' && (
              <button
                className="nav-btn active"
                onClick={handleBackToDashboard}
              >
                ← Analysis: {selectedStock}
              </button>
            )}
          </nav>
        </div>
      </header>
      <main className="app-main">
        {currentPage === 'home' ? (
          <Home onGetStarted={handleGetStarted} />
        ) : currentPage === 'prediction' ? (
          <Dashboard
            key={`prediction-${selectedStock || ticker}`}
            defaultTicker={selectedStock || ticker}
            onTickerChange={setTicker}
            onStockSelect={handleStockSelect}
            isPredictionPage={true}
          />
        ) : (
          <Dashboard
            key="dashboard"
            defaultTicker={ticker}
            onTickerChange={setTicker}
            onStockSelect={handleStockSelect}
          />
        )}
      </main>
    </div>
  );
}

export default App;
