import React, { useState } from 'react';
import '../styles/SearchBar.css';

function SearchBar({ onSearch, currentTicker }) {
  const [input, setInput] = useState(currentTicker);
  const [isFocused, setIsFocused] = useState(false);

  const handleSearch = () => {
    if (input.trim()) {
      onSearch(input.toUpperCase());
      setInput('');
    }
  };

  const popularStocks = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA', 'META', 'NVDA', 'JPM'];

  return (
    <div className="search-container">
      <div className={`search-bar ${isFocused ? 'focused' : ''}`}>
        <div className="search-icon">🔍</div>
        <input
          type="text"
          placeholder="Enter ticker (e.g., AAPL, GOOGL, MSFT)"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
          onFocus={() => setIsFocused(true)}
          onBlur={() => setIsFocused(false)}
        />
        <button onClick={handleSearch} className="search-button">
          <span className="button-text">Search</span>
          <span className="button-arrow">→</span>
        </button>
      </div>

      <div className="popular-stocks">
        <span className="popular-label">Popular:</span>
        {popularStocks.map((stock) => (
          <button
            key={stock}
            className="stock-tag"
            onClick={() => {
              onSearch(stock);
              setInput('');
            }}
          >
            {stock}
          </button>
        ))}
      </div>
    </div>
  );
}

export default SearchBar;
