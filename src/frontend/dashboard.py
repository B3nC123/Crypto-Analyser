import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
import json
from datetime import datetime, timedelta
import time

# Configure the page
st.set_page_config(
    page_title="Crypto Sentiment Trader",
    page_icon="📈",
    layout="wide"
)

# Constants
API_BASE_URL = "http://localhost:8000/api/v1"
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
        ["BTC", "ETH", "BNB", "XRP", "ADA"]
    )
    timeframe = st.sidebar.selectbox(
        "Select Timeframe",
        ["1h", "4h", "1d"]
    )

    # Create columns for key metrics
    col1, col2, col3 = st.columns(3)

    # Current Price
    with col1:
        st.subheader("Current Price")
        prices = fetch_data("market/prices")
        if prices:
            current_price = prices['prices'].get(f"{selected_symbol}USDT")
            st.metric(
                label=f"{selected_symbol}/USDT",
                value=f"${current_price:,.2f}"
            )

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
            st.markdown(f"""
            **Posts Analyzed:** {sentiment['reddit_posts_analyzed']}  
            **News Items:** {sentiment['news_items_analyzed']}
            """)

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
    if historical_data:
        df = pd.DataFrame(historical_data['data'])
        fig = create_candlestick_chart(df, f"{selected_symbol}/USDT")
        st.plotly_chart(fig, use_container_width=True)

    # Technical Analysis
    st.subheader("Technical Analysis")
    technical = fetch_data(f"analysis/technical/{selected_symbol}USDT?interval={timeframe}")
    if technical:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Indicators")
            indicators = technical['signals']
            for indicator, data in indicators.items():
                if indicator != 'overall':
                    st.markdown(f"**{indicator.upper()}:** {data['signal']}")
        
        with col2:
            st.markdown("### Overall Analysis")
            overall = indicators['overall']
            st.markdown(f"""
            **Signal:** {overall['signal']}  
            **Strength:** {overall['strength']:.2%}
            """)

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
