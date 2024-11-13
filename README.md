# Crypto Sentiment Trading Assistant

A comprehensive cryptocurrency trading assistant that combines technical analysis, sentiment analysis, and risk management to provide trading signals and portfolio management.

## Features

### Core Components
- **Market Data Collection**: Real-time and historical data from Binance
- **Sentiment Analysis**: Multi-source sentiment analysis including:
  - Reddit sentiment tracking
  - Crypto news RSS feeds
  - Custom crypto-specific lexicon
- **Technical Analysis**: Comprehensive technical indicators including:
  - RSI (Relative Strength Index)
  - MACD (Moving Average Convergence Divergence)
  - Bollinger Bands
  - EMA (Exponential Moving Average)
  - Support/Resistance levels
  - Volume Profile analysis

### Advanced Features
- **Interactive Dashboard**
  - Real-time price charts with technical indicators
  - Sentiment analysis visualization
  - Market statistics and metrics
  - Trading signals display

- **Backtesting System**
  - Historical strategy testing
  - Performance metrics calculation
  - Trade history analysis
  - Risk/reward optimization

- **Risk Management**
  - Position size optimization
  - Dynamic stop-loss calculation
  - Portfolio exposure control
  - Daily loss limits
  - Capital utilization tracking

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/crypto-trader.git
cd crypto-trader
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

3. Create a .env file with your API keys:
```bash
cp .env.example .env
# Edit .env with your API keys
```

## Usage

### Running the Dashboard
```bash
streamlit run run_dashboard.py
```

### Backtesting a Strategy
```python
from src.backtesting.backtester import Backtester
from datetime import datetime, timedelta

# Initialize backtester
backtester = Backtester(initial_capital=10000)

# Run backtest
start_date = datetime.now() - timedelta(days=30)
end_date = datetime.now()
results = await backtester.run_backtest(
    symbol='BTCUSDT',
    timeframe='1h',
    start_date=start_date,
    end_date=end_date
)

# Generate and print report
print(backtester.generate_report(results))
```

### Using Risk Management
```python
from src.risk_management.risk_manager import RiskManager

# Initialize risk manager
risk_manager = RiskManager(initial_capital=10000)

# Calculate safe position size
position_size = risk_manager.calculate_position_size(
    symbol='BTCUSDT',
    entry_price=50000,
    stop_loss=49000
)

# Validate trade
is_valid, message = risk_manager.validate_trade(
    symbol='BTCUSDT',
    trade_type='buy',
    price=50000,
    size=position_size,
    stop_loss=49000
)
```

## Configuration

Key settings can be configured in `src/config.py`:

- `CRYPTO_SYMBOLS`: List of cryptocurrencies to track
- `UPDATE_INTERVAL`: Data update frequency
- `SENTIMENT_WINDOW`: Time window for sentiment analysis
- `TECHNICAL_TIMEFRAMES`: Available timeframes for analysis
- `RISK_PERCENTAGE`: Maximum risk per trade
- `POSITION_SIZE`: Maximum position size as percentage of capital

## Project Structure

```
crypto-trader/
├── src/
│   ├── api/                 # API endpoints
│   ├── data_collection/     # Market data collection
│   ├── sentiment_analysis/  # Sentiment analysis
│   ├── technical_analysis/  # Technical indicators
│   ├── backtesting/        # Strategy testing
│   ├── risk_management/    # Risk control
│   ├── frontend/           # Web dashboard
│   └── config.py           # Configuration
├── run_dashboard.py        # Dashboard entry point
├── requirements.txt
└── README.md
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This software is for educational purposes only. Do not risk money which you are afraid to lose. USE THE SOFTWARE AT YOUR OWN RISK. THE AUTHORS AND ALL AFFILIATES ASSUME NO RESPONSIBILITY FOR YOUR TRADING RESULTS.
