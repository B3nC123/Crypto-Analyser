from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# API Configuration
BINANCE_API_KEY = os.getenv('BINANCE_API_KEY', '')
BINANCE_API_SECRET = os.getenv('BINANCE_API_SECRET', '')
REDDIT_CLIENT_ID = os.getenv('REDDIT_CLIENT_ID', '')
REDDIT_CLIENT_SECRET = os.getenv('REDDIT_CLIENT_SECRET', '')
REDDIT_USER_AGENT = os.getenv('REDDIT_USER_AGENT', 'crypto_sentiment_bot 1.0')

# Data Collection Settings
CRYPTO_SYMBOLS = ['BTC', 'ETH', 'BNB', 'XRP', 'ADA']
UPDATE_INTERVAL = 300  # 5 minutes in seconds
SENTIMENT_WINDOW = 24  # hours to consider for sentiment analysis

# Technical Analysis Settings
TECHNICAL_TIMEFRAMES = ['1h', '4h', '1d']
TECHNICAL_INDICATORS = [
    'RSI',
    'MACD',
    'BB',  # Bollinger Bands
    'EMA'  # Exponential Moving Average
]

# Trading Settings
RISK_PERCENTAGE = 1.0  # Maximum risk per trade as percentage of portfolio
POSITION_SIZE = 0.1    # Position size as percentage of available balance

# Application Settings
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
