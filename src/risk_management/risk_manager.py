import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
from src.config import RISK_PERCENTAGE, POSITION_SIZE

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RiskManager:
    def __init__(self, initial_capital):
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.max_capital = initial_capital
        self.positions = {}
        self.daily_loss_limit = initial_capital * 0.02  # 2% daily loss limit
        self.daily_losses = 0
        self.last_reset_date = datetime.now().date()

    def calculate_position_size(self, symbol, entry_price, stop_loss):
        """Calculate safe position size based on risk parameters."""
        try:
            # Reset daily losses if it's a new day
            current_date = datetime.now().date()
            if current_date > self.last_reset_date:
                self.daily_losses = 0
                self.last_reset_date = current_date

            # Check if we've hit daily loss limit
            if self.daily_losses >= self.daily_loss_limit:
                logger.warning("Daily loss limit reached. No new positions allowed.")
                return 0

            # Calculate risk per trade
            risk_amount = self.current_capital * (RISK_PERCENTAGE / 100)
            
            # Ensure risk doesn't exceed remaining daily loss limit
            risk_amount = min(risk_amount, self.daily_loss_limit - self.daily_losses)
            
            # Calculate position size based on stop loss
            if stop_loss:
                risk_per_unit = abs(entry_price - stop_loss)
                if risk_per_unit > 0:
                    position_size = risk_amount / risk_per_unit
                    # Apply position size limit
                    max_position_value = self.current_capital * POSITION_SIZE
                    position_size = min(position_size, max_position_value / entry_price)
                    return position_size
            
            return 0

        except Exception as e:
            logger.error(f"Error calculating position size: {e}")
            return 0

    def validate_trade(self, symbol, trade_type, price, size, stop_loss=None):
        """Validate if a trade meets risk management criteria."""
        try:
            # Basic validation checks
            if not price or price <= 0 or not size or size <= 0:
                return False, "Invalid price or size"

            # Check if we're already in a position
            if trade_type == 'buy' and symbol in self.positions:
                return False, "Position already exists"

            # Calculate trade value
            trade_value = price * size

            # Check if trade value exceeds maximum position size
            max_position_value = self.current_capital * POSITION_SIZE
            if trade_value > max_position_value:
                return False, "Trade value exceeds maximum position size"

            # Validate stop loss
            if stop_loss:
                if trade_type == 'buy' and stop_loss >= price:
                    return False, "Stop loss must be below entry price for long positions"
                elif trade_type == 'sell' and stop_loss <= price:
                    return False, "Stop loss must be above entry price for short positions"

            return True, "Trade validated"

        except Exception as e:
            logger.error(f"Error validating trade: {e}")
            return False, str(e)

    def update_position(self, symbol, trade_type, price, size, pnl=None):
        """Update position tracking with new trade information."""
        try:
            if trade_type == 'buy':
                self.positions[symbol] = {
                    'entry_price': price,
                    'size': size,
                    'entry_time': datetime.now(),
                    'value': price * size
                }
                self.current_capital -= (price * size)
            
            elif trade_type == 'sell' and symbol in self.positions:
                if pnl:
                    self.current_capital += pnl
                    if pnl < 0:
                        self.daily_losses += abs(pnl)
                del self.positions[symbol]
                
                # Update maximum capital
                if self.current_capital > self.max_capital:
                    self.max_capital = self.current_capital

        except Exception as e:
            logger.error(f"Error updating position: {e}")

    def calculate_metrics(self):
        """Calculate current risk metrics."""
        try:
            total_position_value = sum(pos['value'] for pos in self.positions.values())
            
            return {
                'current_capital': self.current_capital,
                'max_capital': self.max_capital,
                'total_position_value': total_position_value,
                'capital_utilization': (total_position_value / self.current_capital) if self.current_capital > 0 else 0,
                'daily_losses': self.daily_losses,
                'daily_loss_limit_remaining': max(0, self.daily_loss_limit - self.daily_losses),
                'drawdown': ((self.max_capital - self.current_capital) / self.max_capital) * 100,
                'active_positions': len(self.positions)
            }

        except Exception as e:
            logger.error(f"Error calculating metrics: {e}")
            return {}

    def check_stop_loss(self, symbol, current_price):
        """Check if current price has hit stop loss levels."""
        try:
            if symbol in self.positions:
                position = self.positions[symbol]
                stop_loss = position.get('stop_loss')
                
                if stop_loss:
                    # For long positions
                    if position['entry_price'] > stop_loss and current_price <= stop_loss:
                        return True, self.calculate_loss(symbol, stop_loss)
                    # For short positions
                    elif position['entry_price'] < stop_loss and current_price >= stop_loss:
                        return True, self.calculate_loss(symbol, stop_loss)
                
            return False, 0

        except Exception as e:
            logger.error(f"Error checking stop loss: {e}")
            return False, 0

    def calculate_loss(self, symbol, exit_price):
        """Calculate loss for a position at given exit price."""
        try:
            if symbol in self.positions:
                position = self.positions[symbol]
                entry_price = position['entry_price']
                size = position['size']
                
                return (exit_price - entry_price) * size
            
            return 0

        except Exception as e:
            logger.error(f"Error calculating loss: {e}")
            return 0

    def get_position_summary(self, symbol):
        """Get summary of current position for a symbol."""
        try:
            if symbol in self.positions:
                position = self.positions[symbol]
                return {
                    'symbol': symbol,
                    'entry_price': position['entry_price'],
                    'current_size': position['size'],
                    'entry_time': position['entry_time'],
                    'value': position['value'],
                    'stop_loss': position.get('stop_loss')
                }
            return None

        except Exception as e:
            logger.error(f"Error getting position summary: {e}")
            return None

    def adjust_position_size(self, symbol, current_price):
        """Dynamically adjust position size based on volatility and performance."""
        try:
            if symbol in self.positions:
                position = self.positions[symbol]
                entry_price = position['entry_price']
                current_value = position['size'] * current_price
                
                # Calculate unrealized P&L
                unrealized_pnl = (current_price - entry_price) * position['size']
                pnl_percentage = unrealized_pnl / position['value']
                
                # Adjust position based on performance
                if pnl_percentage > 0.05:  # 5% profit
                    # Consider increasing position
                    return min(position['size'] * 1.2, self.calculate_position_size(
                        symbol, current_price, position.get('stop_loss')
                    ))
                elif pnl_percentage < -0.02:  # 2% loss
                    # Consider reducing position
                    return position['size'] * 0.8
                
            return None

        except Exception as e:
            logger.error(f"Error adjusting position size: {e}")
            return None
