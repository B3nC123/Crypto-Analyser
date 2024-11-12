# Crypto Sentiment Trader

A sophisticated cryptocurrency trading assistant that combines technical analysis with sentiment analysis from social media and news sources to generate trading signals.

## Features

- Real-time cryptocurrency price tracking
- Sentiment analysis from multiple sources:
  - Reddit discussions
  - News articles
  - Social media trends
- Technical analysis including:
  - RSI (Relative Strength Index)
  - MACD (Moving Average Convergence Divergence)
  - Bollinger Bands
  - EMA (Exponential Moving Average)
- Interactive dashboard with:
  - Real-time price charts
  - Sentiment indicators
  - Technical analysis visualization
  - Trading signals
- RESTful API for data access

## Prerequisites

- Python 3.8+
- pip (Python package manager)
- Virtual environment (recommended)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/crypto-sentiment-trader.git
cd crypto-sentiment-trader
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install required packages:
```bash
pip install -r requirements.txt
```

4. Create a .env file in the root directory with your API keys:
```env
BINANCE_API_KEY=your_binance_api_key
BINANCE_API_SECRET=your_binance_api_secret
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret
REDDIT_USER_AGENT=crypto_sentiment_bot 1.0
```

## Usage

1. Start the application:
```bash
python src/main.py
```

This will start both the FastAPI backend server and the Streamlit frontend.

- API will be available at: http://localhost:8000
- Dashboard will be available at: http://localhost:8501

2. Access the API documentation:
- Navigate to http://localhost:8000/docs for interactive API documentation

## API Endpoints

- GET `/api/v1/market/prices` - Get current prices for all tracked symbols
- GET `/api/v1/market/historical/{symbol}` - Get historical price data
- GET `/api/v1/analysis/sentiment/{symbol}` - Get sentiment analysis
- GET `/api/v1/analysis/technical/{symbol}` - Get technical analysis
- GET `/api/v1/trading/signals/{symbol}` - Get combined trading signals

## Project Structure

```
crypto-sentiment-trader/
├── src/
│   ├── api/
│   │   └── main.py
│   ├── data_collection/
│   │   └── market_data.py
│   ├── sentiment_analysis/
│   │   └── analyzer.py
│   ├── technical_analysis/
│   │   └── indicators.py
│   ├── frontend/
│   │   └── dashboard.py
│   ├── config.py
│   └── main.py
├── requirements.txt
└── README.md
```

## Configuration

You can modify the following settings in `src/config.py`:

- `CRYPTO_SYMBOLS`: List of cryptocurrencies to track
- `UPDATE_INTERVAL`: Data update frequency
- `SENTIMENT_WINDOW`: Time window for sentiment analysis
- `TECHNICAL_TIMEFRAMES`: Available timeframes for technical analysis
- `RISK_PERCENTAGE`: Maximum risk per trade
- `POSITION_SIZE`: Position size as percentage of available balance

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This software is for educational purposes only. Do not use it to make financial decisions. Always do your own research and consult with financial professionals before trading cryptocurrencies.
