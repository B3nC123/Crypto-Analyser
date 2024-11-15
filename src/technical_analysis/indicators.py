import pandas as pd
import numpy as np
import ta
import logging
from src.config import TECHNICAL_INDICATORS, TECHNICAL_TIMEFRAMES

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TechnicalAnalyzer:
    def __init__(self):
        self.indicators = TECHNICAL_INDICATORS
        self.timeframes = TECHNICAL_TIMEFRAMES

    def _series_to_dict(self, series):
        """Convert pandas Series to dictionary, handling NaN values."""
        if isinstance(series, pd.Series):
            return {str(k): float(v) if not pd.isna(v) else 0.0 for k, v in series.items()}
        return series

    def _handle_missing_values(self, series):
        """Handle missing values in a series using forward and backward fill."""
        return series.ffill().bfill()

    def calculate_rsi(self, data, period=14):
        """Calculate Relative Strength Index."""
        try:
            rsi = ta.momentum.RSIIndicator(data['close'], window=period)
            return rsi.rsi().fillna(50)  # Fill NaN with neutral RSI value
        except Exception as e:
            logger.error(f"Error calculating RSI: {e}")
            return None

    def calculate_macd(self, data, fast_period=12, slow_period=26, signal_period=9):
        """Calculate MACD (Moving Average Convergence Divergence)."""
        try:
            macd = ta.trend.MACD(
                data['close'],
                window_slow=slow_period,
                window_fast=fast_period,
                window_sign=signal_period
            )
            return {
                'macd': self._series_to_dict(macd.macd().fillna(0)),
                'signal': self._series_to_dict(macd.macd_signal().fillna(0)),
                'histogram': self._series_to_dict(macd.macd_diff().fillna(0))
            }
        except Exception as e:
            logger.error(f"Error calculating MACD: {e}")
            return None

    def calculate_bollinger_bands(self, data, window=20, window_dev=2):
        """Calculate Bollinger Bands."""
        try:
            bollinger = ta.volatility.BollingerBands(
                data['close'],
                window=window,
                window_dev=window_dev
            )
            return {
                'upper': self._series_to_dict(self._handle_missing_values(bollinger.bollinger_hband())),
                'middle': self._series_to_dict(self._handle_missing_values(bollinger.bollinger_mavg())),
                'lower': self._series_to_dict(self._handle_missing_values(bollinger.bollinger_lband()))
            }
        except Exception as e:
            logger.error(f"Error calculating Bollinger Bands: {e}")
            return None

    def calculate_ema(self, data, periods=[9, 21, 50, 200]):
        """Calculate Exponential Moving Averages for multiple periods."""
        try:
            emas = {}
            for period in periods:
                ema = ta.trend.EMAIndicator(data['close'], window=period)
                emas[f'EMA_{period}'] = self._series_to_dict(self._handle_missing_values(ema.ema_indicator()))
            return emas
        except Exception as e:
            logger.error(f"Error calculating EMAs: {e}")
            return None

    def calculate_support_resistance(self, data, window=20):
        """Calculate support and resistance levels using pivot points."""
        try:
            pivot = ta.trend.PSARIndicator(
                high=data['high'],
                low=data['low'],
                close=data['close']
            )
            return {
                'support': self._series_to_dict(self._handle_missing_values(pivot.psar())),
                'resistance': self._series_to_dict(pivot.psar_up_indicator().fillna(0))
            }
        except Exception as e:
            logger.error(f"Error calculating support/resistance: {e}")
            return None

    def calculate_volume_profile(self, data, bins=10):
        """Calculate Volume Profile."""
        try:
            price_range = data['high'].max() - data['low'].min()
            bin_size = price_range / bins
            
            volume_profile = []
            current_price = data['low'].min()
            
            for i in range(bins):
                price_level = current_price + (bin_size * i)
                mask = (data['low'] >= price_level) & (data['low'] < price_level + bin_size)
                volume = data.loc[mask, 'volume'].sum()
                volume_profile.append({
                    'price_level': float(price_level),
                    'volume': float(volume)
                })
            
            return volume_profile
        except Exception as e:
            logger.error(f"Error calculating volume profile: {e}")
            return None

    def generate_signals(self, data):
        """Generate trading signals based on technical indicators."""
        try:
            signals = {
                'rsi': None,
                'macd': None,
                'bb': None,
                'ema': None,
                'overall': None
            }

            # RSI Signals
            rsi = self.calculate_rsi(data)
            if rsi is not None:
                latest_rsi = float(rsi.iloc[-1])
                signals['rsi'] = {
                    'value': latest_rsi,
                    'signal': 'buy' if latest_rsi < 30 else 'sell' if latest_rsi > 70 else 'neutral'
                }

            # MACD Signals
            macd = self.calculate_macd(data)
            if macd is not None:
                latest_macd = float(list(macd['macd'].values())[-1])
                latest_signal = float(list(macd['signal'].values())[-1])
                signals['macd'] = {
                    'value': latest_macd,
                    'signal': 'buy' if latest_macd > latest_signal else 'sell'
                }

            # Bollinger Bands Signals
            bb = self.calculate_bollinger_bands(data)
            if bb is not None:
                latest_price = float(data['close'].iloc[-1])
                latest_lower = float(list(bb['lower'].values())[-1])
                latest_upper = float(list(bb['upper'].values())[-1])
                signals['bb'] = {
                    'value': {
                        'price': latest_price,
                        'lower': latest_lower,
                        'upper': latest_upper
                    },
                    'signal': 'buy' if latest_price < latest_lower else 'sell' if latest_price > latest_upper else 'neutral'
                }

            # EMA Signals
            ema = self.calculate_ema(data)
            if ema is not None:
                latest_price = float(data['close'].iloc[-1])
                latest_ema_50 = float(list(ema['EMA_50'].values())[-1])
                latest_ema_200 = float(list(ema['EMA_200'].values())[-1])
                signals['ema'] = {
                    'value': {
                        'ema_50': latest_ema_50,
                        'ema_200': latest_ema_200
                    },
                    'signal': 'buy' if latest_ema_50 > latest_ema_200 else 'sell'
                }

            # Calculate Overall Signal
            signal_counts = {
                'buy': 0,
                'sell': 0,
                'neutral': 0
            }

            for indicator in signals:
                if indicator != 'overall' and signals[indicator] is not None:
                    signal_counts[signals[indicator]['signal']] += 1

            # Determine overall signal
            if signal_counts['buy'] > signal_counts['sell']:
                overall_signal = 'buy'
            elif signal_counts['sell'] > signal_counts['buy']:
                overall_signal = 'sell'
            else:
                overall_signal = 'neutral'

            total_signals = sum(signal_counts.values())
            strength = float(max(signal_counts.values()) / total_signals) if total_signals > 0 else 0.0

            signals['overall'] = {
                'signal': overall_signal,
                'strength': strength
            }

            return signals

        except Exception as e:
            logger.error(f"Error generating signals: {e}")
            return None
