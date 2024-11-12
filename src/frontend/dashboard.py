import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
import json
from datetime import datetime, timedelta
import time
import sys
import os
from pathlib import Path

# Add parent directory to Python path
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.config import CRYPTO_SYMBOLS, TECHNICAL_TIMEFRAMES

# Configure the page
st.set_page_config(
    page_title="Crypto Sentiment Trader",
    page_icon="📈",
    layout="wide"
)

# Constants
API_PORT = os.environ.get('API_PORT', '8080')  # Get port from environment or default to 8080
API_BASE_URL = f"http://localhost:{API_PORT}/api/v1"
REFRESH_INTERVAL = 300  # 5 minutes in seconds

def fetch_data(endpoint):
    """Fetch data from API endpoint."""
    try:
        response = requests.get(f"{API_BASE_URL}/{endpoint}")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error fetching data from {endpoint}: {str(e)}")
        return None

def create_candlestick_chart(data, symbol):
    """Create a candlestick chart with volume."""
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                       vertical_spacing=0.03, subplot_titles=(f'{symbol} Price', 'Volume'),
                       row_width=[0.7, 0.3])

    # Candlestick chart
    fig.add_trace(go.Candlestick(x=data['timestamp'],
                                open=data['open'],
                                high=data['high'],
                                low=data['low'],
                                close=data['close'],
                                name='OHLC'),
                  row=1, col=1)

    # Volume bar chart
    fig.add_trace(go.Bar(x=data['timestamp'],
                        y=data['volume'],
                        name='Volume'),
                  row=2, col=1)

    fig.update_layout(
        xaxis_rangeslider_visible=False,
        height=800
    )

    return fig

def main():
    # Title and description
    st.title("🚀 Crypto Sentiment Trader")
    st.markdown("""
    Real-time cryptocurrency trading dashboard combining technical analysis and sentiment data.
    """)

    # Sidebar
    st.sidebar.title("Settings")
    selected_symbol = st.sidebar.selectbox(
        "Select Cryptocurrency",
        CRYPTO_SYMBOLS
    )
    timeframe = st.sidebar.selectbox(
        "Select Timeframe",
        TECHNICAL_TIMEFRAMES
    )

    # Create columns for key metrics
    col1, col2, col3 = st.columns(3)

    # Current Price
    with col1:
        st.subheader("Current Price")
        prices = fetch_data("market/prices")
        if prices:
            current_price = prices['prices'].get(f"{selected_symbol}USDT")
            if current_price:
                st.metric(
                    label=f"{selected_symbol}/USDT",
                    value=f"${current_price:,.2f}"
                )
            else:
                st.error(f"No price data available for {selected_symbol}")

    # Sentiment Analysis
    with col2:
        st.subheader("Sentiment Analysis")
        sentiment = fetch_data(f"analysis/sentiment/{selected_symbol}")
        if sentiment:
            sentiment_score = sentiment['sentiment_score']
            sentiment_color = 'green' if sentiment_score > 0 else 'red'
            st.markdown(f"""
            **Score:** <span style='color:{sentiment_color}'>{sentiment_score:.2f}</span>
            """, unsafe_allow_html=True)
            
            # Display data source information
            st.markdown("### Data Sources")
            if sentiment.get('reddit_available', False):
                st.markdown(f"**Reddit Posts:** {sentiment['reddit_posts_analyzed']}")
            else:
                st.warning("⚠️ Reddit data unavailable")
            
            st.markdown(f"**News Items:** {sentiment['news_items_analyzed']}")

    # Trading Signals
    with col3:
        st.subheader("Trading Signals")
        signals = fetch_data(f"trading/signals/{selected_symbol}")
        if signals:
            combined_signal = signals['combined_signal']
            signal_color = {
                'buy': 'green',
                'sell': 'red',
                'neutral': 'gray'
            }[combined_signal]
            st.markdown(f"""
            **Signal:** <span style='color:{signal_color}'>{combined_signal.upper()}</span>  
            **Confidence:** {signals['confidence']:.2%}
            """, unsafe_allow_html=True)

    # Price Chart
    st.subheader("Price Chart")
    historical_data = fetch_data(f"market/historical/{selected_symbol}USDT?interval={timeframe}")
    if historical_data and historical_data.get('data'):
        df = pd.DataFrame(historical_data['data'])
        fig = create_candlestick_chart(df, f"{selected_symbol}/USDT")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.error("No historical data available")

    # Technical Analysis
    st.subheader("Technical Analysis")
    technical = fetch_data(f"analysis/technical/{selected_symbol}USDT?interval={timeframe}")
    if technical and technical.get('signals'):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Indicators")
            indicators = technical['signals']
            for indicator, data in indicators.items():
                if indicator != 'overall':
                    signal_color = {
                        'buy': 'green',
                        'sell': 'red',
                        'neutral': 'gray'
                    }[data['signal']]
                    st.markdown(f"**{indicator.upper()}:** <span style='color:{signal_color}'>{data['signal'].upper()}</span>", unsafe_allow_html=True)
        
        with col2:
            st.markdown("### Overall Analysis")
            overall = indicators['overall']
            signal_color = {
                'buy': 'green',
                'sell': 'red',
                'neutral': 'gray'
            }[overall['signal']]
            st.markdown(f"""
            **Signal:** <span style='color:{signal_color}'>{overall['signal'].upper()}</span>  
            **Strength:** {overall['strength']:.2%}
            """, unsafe_allow_html=True)
    else:
        st.error("No technical analysis data available")

    # Refresh button
    if st.button("Refresh Data"):
        st.experimental_rerun()

    # Auto-refresh disclaimer
    st.markdown("""
    ---
    *Data refreshes automatically every 5 minutes. Last update: {}*
    """.format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

if __name__ == "__main__":
    main()
