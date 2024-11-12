from binance.client import Client
from binance.exceptions import BinanceAPIException
import pandas as pd
from datetime import datetime, timedelta
import logging
from src.config import BINANCE_API_KEY, BINANCE_API_SECRET, CRYPTO_SYMBOLS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MarketDataCollector:
    def __init__(self):
        self.client = Client(BINANCE_API_KEY, BINANCE_API_SECRET)
        self.symbols = [f"{symbol}USDT" for symbol in CRYPTO_SYMBOLS]

    def get_current_prices(self):
        """Get current prices for all tracked symbols."""
        try:
            tickers = self.client.get_all_tickers()
            prices = {}
            for ticker in tickers:
                if ticker['symbol'] in self.symbols:
                    prices[ticker['symbol']] = float(ticker['price'])
            return prices
        except BinanceAPIException as e:
            logger.error(f"Error fetching current prices: {e}")
            return {}

    def get_historical_klines(self, symbol, interval, lookback_days):
        """
        Get historical kline/candlestick data.
        
        Args:
            symbol (str): Trading pair symbol (e.g., 'BTCUSDT')
            interval (str): Kline interval (e.g., '1h', '4h', '1d')
            lookback_days (int): Number of days to look back
        
        Returns:
            pandas.DataFrame: Historical price data
        """
        try:
            start_time = datetime.now() - timedelta(days=lookback_days)
            klines = self.client.get_historical_klines(
                symbol,
                interval,
                start_time.strftime("%d %b %Y %H:%M:%S"),
                limit=1000
            )
            
            if not klines:
                return pd.DataFrame()
            
            df = pd.DataFrame(klines, columns=[
                'timestamp', 'open', 'high', 'low', 'close',
                'volume', 'close_time', 'quote_asset_volume',
                'number_of_trades', 'taker_buy_base_asset_volume',
                'taker_buy_quote_asset_volume', 'ignore'
            ])
            
            # Convert timestamp to datetime
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            
            # Convert string values to float
            for col in ['open', 'high', 'low', 'close', 'volume']:
                df[col] = df[col].astype(float)
            
            return df.set_index('timestamp')
        
        except BinanceAPIException as e:
            logger.error(f"Error fetching historical data for {symbol}: {e}")
            return pd.DataFrame()

    def get_market_depth(self, symbol):
        """Get order book depth for a symbol."""
        try:
            depth = self.client.get_order_book(symbol=symbol, limit=10)
            return {
                'bids': depth['bids'][:5],  # Top 5 bids
                'asks': depth['asks'][:5]    # Top 5 asks
            }
        except BinanceAPIException as e:
            logger.error(f"Error fetching market depth for {symbol}: {e}")
            return {'bids': [], 'asks': []}

    def get_24h_stats(self, symbol):
        """Get 24-hour price statistics."""
        try:
            stats = self.client.get_ticker(symbol=symbol)
            return {
                'price_change': float(stats['priceChange']),
                'price_change_percent': float(stats['priceChangePercent']),
                'weighted_avg_price': float(stats['weightedAvgPrice']),
                'prev_close_price': float(stats['prevClosePrice']),
                'last_price': float(stats['lastPrice']),
                'volume': float(stats['volume'])
            }
        except BinanceAPIException as e:
            logger.error(f"Error fetching 24h stats for {symbol}: {e}")
            return {}
