# Crypto Sentiment Trader

A sophisticated cryptocurrency trading assistant that combines technical analysis with sentiment analysis from social media and news sources to generate trading signals.

## Features

- Real-time cryptocurrency price tracking via Binance API
- Multi-source sentiment analysis:
  - Reddit discussions (using public API)
  - News articles from major crypto news outlets (CoinTelegraph, CoinDesk)
  - Weighted sentiment scoring based on post engagement
- Comprehensive technical analysis:
  - RSI (Relative Strength Index)
  - MACD (Moving Average Convergence Divergence)
  - Bollinger Bands
  - EMA (Exponential Moving Average)
- Interactive dashboard featuring:
  - Real-time price charts with volume data
  - Sentiment indicators and trends
  - Technical analysis visualization
  - Combined trading signals
- RESTful API for data access and integration

## Prerequisites

- Python 3.8+
- Git
- Binance API credentials (for market data)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/B3nC123/Crypto-Analyser.git
cd Crypto-Analyser
```

2. Create and activate a virtual environment:
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

3. Install required packages:
```bash
pip install -r requirements.txt
```

4. Create a .env file in the root directory:
```bash
# Windows
copy .env.example .env

# Linux/Mac
cp .env.example .env
```

5. Update the .env file with your API credentials:
```env
# Binance API Configuration
BINANCE_API_KEY=your_binance_api_key
BINANCE_API_SECRET=your_binance_api_secret

# Application Settings
DEBUG=False
LOG_LEVEL=INFO
```

## Usage

1. Start the application:
```bash
python -m src.main
```

This command starts both:
- FastAPI backend server on http://localhost:8080
- Streamlit dashboard on http://localhost:8501

2. Access the dashboard:
- Open your web browser and navigate to http://localhost:8501
- Select a cryptocurrency from the dropdown menu
- Choose your preferred timeframe
- View real-time price data, sentiment analysis, and trading signals

3. API Documentation:
- Interactive API docs: http://localhost:8080/docs
- OpenAPI specification: http://localhost:8080/openapi.json

## API Endpoints

### Market Data
- GET `/api/v1/market/prices` - Get current prices for all tracked symbols
- GET `/api/v1/market/historical/{symbol}` - Get historical price data

### Analysis
- GET `/api/v1/analysis/sentiment/{symbol}` - Get sentiment analysis
- GET `/api/v1/analysis/technical/{symbol}` - Get technical analysis
- GET `/api/v1/trading/signals/{symbol}` - Get combined trading signals

## Sentiment Analysis

The system performs sentiment analysis using multiple data sources:

1. Reddit Data:
   - Fetches posts from cryptocurrency-related subreddits
   - Uses Reddit's public JSON API
   - Analyzes post titles and content
   - Weights sentiment based on post scores and comment counts

2. News Data:
   - Aggregates news from major crypto news outlets
   - Filters articles by relevance to specific cryptocurrencies
   - Analyzes article titles and summaries
   - Considers publication timing and source reliability

3. Sentiment Scoring:
   - Uses VADER sentiment analysis
   - Enhanced with crypto-specific lexicon
   - Weighted scoring based on source reliability and engagement
   - Separate tracking for each cryptocurrency

## Project Structure

```
crypto-sentiment-trader/
├── src/
│   ├── api/                 # FastAPI backend
│   ├── data_collection/     # Market data retrieval
│   ├── sentiment_analysis/  # Sentiment processing
│   ├── technical_analysis/  # Trading indicators
│   ├── frontend/           # Streamlit dashboard
│   ├── config.py          # Configuration settings
│   └── main.py            # Application entry point
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
└── README.md            # Project documentation
```

## Configuration

Edit `src/config.py` to modify:
- `CRYPTO_SYMBOLS`: List of tracked cryptocurrencies
- `UPDATE_INTERVAL`: Data refresh frequency
- `SENTIMENT_WINDOW`: Time window for sentiment analysis
- `TECHNICAL_TIMEFRAMES`: Available chart timeframes
- `TECHNICAL_INDICATORS`: Enabled technical indicators

## Development

1. Install development dependencies:
```bash
pip install -r requirements.txt
```

2. Run tests:
```bash
python -m pytest tests/
```

3. Start the application in debug mode:
```bash
DEBUG=True python -m src.main
```

## Troubleshooting

1. Sentiment Analysis:
   - If sentiment scores seem incorrect, check the news feed URLs in the configuration
   - Verify the cryptocurrency symbol matches exactly (e.g., "BTC" not "Bitcoin")
   - Check if the sentiment window duration is appropriate for your needs

2. Binance API issues:
   - Confirm your API keys are valid
   - Check if you have the necessary API permissions
   - Verify your IP is not restricted

3. Dashboard not loading:
   - Ensure both backend and frontend are running
   - Check if ports 8080 and 8501 are available
   - Look for errors in the application logs

## Contributing

1. Fork the repository
2. Create a feature branch:
```bash
git checkout -b feature/your-feature-name
```
3. Commit your changes:
```bash
git commit -am 'Add some feature'
```
4. Push to the branch:
```bash
git push origin feature/your-feature-name
```
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This software is for educational purposes only. Do not use it to make financial decisions. Always do your own research and consult with financial professionals before trading cryptocurrencies.
