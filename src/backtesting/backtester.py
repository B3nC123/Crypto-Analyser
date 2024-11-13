import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
from src.technical_analysis.indicators import TechnicalAnalyzer
from src.sentiment_analysis.analyzer import SentimentAnalyzer
from src.data_collection.market_data import MarketDataCollector
from src.config import RISK_PERCENTAGE, POSITION_SIZE

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Backtester:
    def __init__(self, initial_capital=10000):
        self.initial_capital = initial_capital
        self.capital = initial_capital
        self.position = None
        self.technical_analyzer = TechnicalAnalyzer()
        self.market_data = MarketDataCollector()
        self.trades = []
        self.performance_metrics = {}

    def calculate_position_size(self, price):
        """Calculate position size based on risk parameters."""
        risk_amount = self.capital * (RISK_PERCENTAGE / 100)
        return (self.capital * POSITION_SIZE) / price

    def execute_trade(self, signal, price, timestamp):
        """Execute a trade based on the signal."""
        if signal == 'buy' and self.position is None:
            # Open long position
            size = self.calculate_position_size(price)
            cost = size * price
            if cost <= self.capital:
                self.position = {
                    'type': 'long',
                    'size': size,
                    'entry_price': price,
                    'entry_time': timestamp
                }
                self.capital -= cost
                self.trades.append({
                    'type': 'buy',
                    'price': price,
                    'size': size,
                    'timestamp': timestamp,
                    'remaining_capital': self.capital
                })
                return True

        elif signal == 'sell' and self.position is not None:
            # Close long position
            if self.position['type'] == 'long':
                proceeds = self.position['size'] * price
                profit = proceeds - (self.position['size'] * self.position['entry_price'])
                self.capital += proceeds
                self.trades.append({
                    'type': 'sell',
                    'price': price,
                    'size': self.position['size'],
                    'timestamp': timestamp,
                    'profit': profit,
                    'remaining_capital': self.capital
                })
                self.position = None
                return True

        return False

    def calculate_metrics(self):
        """Calculate performance metrics from backtest results."""
        if not self.trades:
            return {}

        profits = [t['profit'] for t in self.trades if 'profit' in t]
        winning_trades = len([p for p in profits if p > 0])
        losing_trades = len([p for p in profits if p <= 0])
        total_trades = len(profits)

        self.performance_metrics = {
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'win_rate': winning_trades / total_trades if total_trades > 0 else 0,
            'total_profit': sum(profits),
            'max_drawdown': self.calculate_max_drawdown(),
            'profit_factor': self.calculate_profit_factor(profits),
            'final_capital': self.capital,
            'return_pct': ((self.capital - self.initial_capital) / self.initial_capital) * 100
        }

        return self.performance_metrics

    def calculate_max_drawdown(self):
        """Calculate maximum drawdown from trade history."""
        if not self.trades:
            return 0

        peak = self.initial_capital
        max_drawdown = 0

        for trade in self.trades:
            current_capital = trade['remaining_capital']
            if current_capital > peak:
                peak = current_capital
            drawdown = (peak - current_capital) / peak
            max_drawdown = max(max_drawdown, drawdown)

        return max_drawdown * 100

    def calculate_profit_factor(self, profits):
        """Calculate profit factor (gross profits / gross losses)."""
        if not profits:
            return 0

        gross_profits = sum([p for p in profits if p > 0]) or 0
        gross_losses = abs(sum([p for p in profits if p < 0])) or 1
        return gross_profits / gross_losses

    async def run_backtest(self, symbol, timeframe, start_date, end_date):
        """Run backtest for a given symbol and timeframe."""
        try:
            # Reset state
            self.capital = self.initial_capital
            self.position = None
            self.trades = []
            
            # Get historical data
            data = self.market_data.get_historical_klines(
                symbol,
                timeframe,
                (end_date - start_date).days
            )

            if data.empty:
                logger.error("No data available for backtesting")
                return None

            # Filter data for backtest period
            mask = (data.index >= start_date) & (data.index <= end_date)
            data = data[mask]

            # Initialize sentiment analyzer
            sentiment_analyzer = SentimentAnalyzer()

            # Run backtest
            for timestamp, row in data.iterrows():
                # Generate technical signals
                technical_signals = self.technical_analyzer.generate_signals(
                    data.loc[:timestamp]
                )

                # Get sentiment data (if available)
                try:
                    sentiment_data = await sentiment_analyzer.aggregate_sentiment(
                        symbol.replace('USDT', '')
                    )
                    sentiment_signal = 'buy' if sentiment_data['sentiment_score'] > 0.2 else \
                                     'sell' if sentiment_data['sentiment_score'] < -0.2 else \
                                     'neutral'
                except Exception as e:
                    logger.warning(f"Error getting sentiment data: {e}")
                    sentiment_signal = 'neutral'

                # Combine signals (simple strategy - can be enhanced)
                if technical_signals and technical_signals['overall']:
                    overall_signal = technical_signals['overall']['signal']
                    
                    # Execute trade only if technical and sentiment signals align
                    if overall_signal == sentiment_signal and overall_signal != 'neutral':
                        self.execute_trade(overall_signal, row['close'], timestamp)

            # Calculate final metrics
            self.calculate_metrics()

            return {
                'trades': self.trades,
                'metrics': self.performance_metrics
            }

        except Exception as e:
            logger.error(f"Error during backtesting: {e}")
            return None

    def generate_report(self, results):
        """Generate a detailed backtest report."""
        if not results or 'metrics' not in results:
            return "No backtest results available."

        metrics = results['metrics']
        trades = results['trades']

        report = []
        report.append("=== Backtest Results ===")
        report.append(f"Initial Capital: ${self.initial_capital:,.2f}")
        report.append(f"Final Capital: ${metrics['final_capital']:,.2f}")
        report.append(f"Total Return: {metrics['return_pct']:.2f}%")
        report.append(f"Total Trades: {metrics['total_trades']}")
        report.append(f"Win Rate: {metrics['win_rate']*100:.2f}%")
        report.append(f"Profit Factor: {metrics['profit_factor']:.2f}")
        report.append(f"Maximum Drawdown: {metrics['max_drawdown']:.2f}%")
        
        # Add trade list
        report.append("\n=== Trade History ===")
        for trade in trades:
            trade_type = trade['type'].upper()
            price = trade['price']
            size = trade['size']
            timestamp = trade['timestamp']
            
            if 'profit' in trade:
                profit = trade['profit']
                report.append(
                    f"{timestamp}: {trade_type} {size:.4f} @ ${price:.2f} "
                    f"(Profit: ${profit:.2f})"
                )
            else:
                report.append(
                    f"{timestamp}: {trade_type} {size:.4f} @ ${price:.2f}"
                )

        return "\n".join(report)
