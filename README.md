# AI Stock Market Analysis & Prediction System

A production-quality system that predicts stock trends (UP/DOWN) using technical indicators and machine learning.

## 📋 Tech Stack

### Backend
- **Framework**: FastAPI (Python 3.9+)
- **ML**: scikit-learn
- **Data**: pandas, numpy, yfinance
- **Sentiment**: VADER (NLTK)

### Frontend
- **Framework**: React.js
- **Charts**: Chart.js, Plotly.js
- **Styling**: CSS3 (responsive)

### Data Source
- Yahoo Finance API (via yfinance)

## 📁 Project Structure

```
Stock Market Predictor/
├── backend/                    # Python FastAPI backend
│   ├── api_complete.py        # Main API server
│   ├── stock_predictor.py     # ML prediction models
│   ├── data_pipeline.py       # Data fetching & processing
│   ├── sentiment_analyzer.py  # News sentiment analysis
│   ├── backtester.py          # Backtesting module
│   ├── test_api.py            # API tests
│   ├── requirements.txt        # Python dependencies
│   ├── app/                    # FastAPI app structure
│   ├── models/                 # Trained ML models
│   └── data/                   # Stock data cache
│
├── frontend/                   # React frontend app
│   ├── public/                 # Static assets
│   ├── src/
│   │   ├── components/         # React components
│   │   │   ├── Home.js        # Landing page
│   │   │   ├── SearchBar.js   # Stock search
│   │   │   ├── StockChart.js  # Price chart display
│   │   │   ├── PredictionCard.js  # Prediction display
│   │   │   └── IndicatorPanel.js  # Technical indicators
│   │   ├── pages/              # Page components
│   │   │   └── Dashboard.js    # Main dashboard
│   │   ├── services/           # API client services
│   │   ├── styles/             # CSS files
│   │   ├── App.js              # Main app component
│   │   └── index.js            # React entry point
│   ├── package.json            # Node.js dependencies
│   └── node_modules/           # Installed packages
│
├── README.md                   # This file
└── .gitignore                 # Git ignore rules
```

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Node.js 16+
- pip & npm

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/Scripts/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run server
python api_complete.py
```

Server runs on `http://localhost:8000`
API docs: `http://localhost:8000/docs`

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

App runs on `http://localhost:3000`

## 🎯 Features

- ✅ Stock data fetching via Yahoo Finance
- ✅ Technical indicators (MA-50/200, RSI, MACD)
- ✅ Binary trend prediction (UP/DOWN)
- ✅ RESTful API with FastAPI
- ✅ Modern React dashboard with home page
- ✅ Interactive stock charts
- ✅ Sentiment analysis from news
- ✅ Backtesting module
- ✅ Responsive UI design

## 🔑 Key Features

### Home Page
- Professional hero section with key statistics
- Feature highlights showcasing capabilities
- Quick start guide for new users
- Newsletter subscription
- Easy navigation to dashboard

### Dashboard
- Real-time stock search
- Technical indicator analysis (RSI, MACD, Moving Averages)
- AI-powered trend predictions
- Interactive price charts
- Responsive grid layout

### Backend API
- Health check endpoints
- Stock data fetching with indicators
- Trend predictions
- Sentiment analysis
- Backtesting capabilities

## 📚 API Endpoints

```
GET  /health              - Health check
POST /get-stock-data      - Fetch stock data + indicators
POST /train-model         - Train prediction model
POST /predict             - Get trend prediction
GET  /indicators/:ticker  - Get technical indicators
```

## 📖 Development Guidelines

- **Code Style**: PEP 8 (Python), ESLint (JavaScript)
- **Components**: React hooks with functional components
- **Styling**: CSS3 with responsive design
- **Error Handling**: Comprehensive try-catch with meaningful messages

## ⚠️ Important Notes

- This system predicts **trend (UP/DOWN)**, not exact prices
- Model uses historical data; past performance ≠ future results
- For production: Add authentication, rate limiting, database
- Backtesting results may differ from live trading

## 📝 License

MIT License - See LICENSE file

---

**Status**: 🟢 Production Ready - Home page and dashboard complete
