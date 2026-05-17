# Frontend Structure & Organization

## Current Structure

```
frontend/
├── node_modules/           # Dependencies (ignore)
├── public/                 # Static assets
│   └── index.html         # Main HTML file
├── src/
│   ├── App.js             # Main app component
│   ├── index.js           # React entry point
│   ├── styles/            # Global styles
│   │   ├── App.css
│   │   └── styles.css
│   ├── pages/             # Page components
│   │   └── Dashboard.js   # Dashboard page
│   ├── components/        # Reusable components
│   │   ├── Home.js
│   │   ├── SearchBar.js
│   │   ├── StockChart.js
│   │   ├── PredictionCard.js
│   │   ├── IndicatorPanel.js
│   │   ├── StockWatchlist.js
│   │   ├── TradingViewGrid.js
│   │   ├── TradingRecommendation.js
│   │   └── [other components]
│   └── services/          # API services
│       └── (empty - in progress)
├── package.json           # Dependencies & scripts
└── package-lock.json      # Lock file
```

## Component Breakdown

### Pages
- **Dashboard.js** - Main dashboard with stock search, charts, indicators, and trading recommendations

### Components
- **Home.js** - Landing/home page
- **SearchBar.js** - Stock symbol search
- **StockChart.js** - Candlestick chart display (Plotly)
- **IndicatorPanel.js** - Technical indicators display
- **PredictionCard.js** - Price prediction display
- **StockWatchlist.js** - Watchlist of multiple stocks
- **TradingViewGrid.js** - TradingView-style mini charts
- **TradingRecommendation.js** - Buy/sell/hold recommendations

### Services
- Currently empty - can add API client here
- Can organize API calls into dedicated service files

## Styling Strategy
- Global styles in `styles/styles.css`
- Component-specific CSS in `styles/App.css`
- CSS Grid/Flexbox for responsive layout
- Dark theme with green/red accents

## Recommended Improvements

### Add API Service Layer
```
src/services/api.js
- Centralized API calls
- Error handling
- Request/response formatting
```

### Add Constants
```
src/constants/
- API_URL
- Chart colors
- Stock symbols
- Period options
```

### Add Utils
```
src/utils/
- formatPrice()
- formatDate()
- calculateChange()
```

### Add Hooks (Optional)
```
src/hooks/
- useStockData()
- useFetchIndicators()
- usePrediction()
```

## Current Status
✅ Components organized by function
✅ Styles centralized
✅ Responsive design implemented
⏳ API service layer - can be added if needed
⏳ Tests - not yet implemented
⏳ Error boundary - can be added for better UX

## Quick Commands

```bash
# Start development server
npm start

# Build for production
npm run build

# Run tests
npm test

# Format code
npm run format

# Lint code
npm run lint
```
