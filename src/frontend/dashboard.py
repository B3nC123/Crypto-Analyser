import streamlit as st
import plotly.graph_objects as go
from datetime import datetime, timedelta
import pandas as pd
import asyncio
from ..data_collection.market_data import MarketDataCollector
from ..technical_analysis.indicators import TechnicalAnalyzer
from ..sentiment_analysis.analyzer import SentimentAnalyzer
from ..config import CRYPTO_SYMBOLS, TECHNICAL_TIMEFRAMES

class Dashboard:
    def __init__(self):
        self.market_data = MarketDataCollector()
        self.technical_analyzer = TechnicalAnalyzer()
        self.sentiment_analyzer = SentimentAnalyzer()

    def plot_price_chart(self, symbol, timeframe, data):
        """Create an interactive price chart with indicators."""
        fig = go.Figure()

        # Candlestick chart
        fig.add_trace(go.Candlestick(
            x=data.index,
            open=data['open'],
            high=data['high'],
            low=data['low'],
            close=data['close'],
            name='Price'
        ))

        # Add Bollinger Bands
        bb = self.technical_analyzer.calculate_bollinger_bands(data)
        if bb:
            for band, color in [('upper', 'rgba(250, 0, 0, 0.2)'), 
                              ('lower', 'rgba(0, 250, 0, 0.2)')]:
                fig.add_trace(go.Scatter(
                    x=data.index,
                    y=pd.Series(bb[band]),
                    name=f'BB {band}',
                    line=dict(color=color),
                    opacity=0.7
                ))

        # Layout
        fig.update_layout(
            title=f'{symbol} Price Chart ({timeframe})',
            yaxis_title='Price (USDT)',
            xaxis_title='Date',
            template='plotly_dark'
        )

        return fig

    def display_technical_indicators(self, data):
        """Display technical indicators in a formatted way."""
        signals = self.technical_analyzer.generate_signals(data)
        
        if signals:
            cols = st.columns(4)
            
            # RSI
            if signals['rsi']:
                with cols[0]:
                    st.metric(
                        "RSI",
                        f"{signals['rsi']['value']:.2f}",
                        delta=signals['rsi']['signal']
                    )
            
            # MACD
            if signals['macd']:
                with cols[1]:
                    st.metric(
                        "MACD",
                        f"{signals['macd']['value']:.2f}",
                        delta=signals['macd']['signal']
                    )
            
            # Bollinger Bands
            if signals['bb']:
                with cols[2]:
                    st.metric(
                        "BB Position",
                        f"{signals['bb']['value']['price']:.2f}",
                        delta=signals['bb']['signal']
                    )
            
            # Overall Signal
            if signals['overall']:
                with cols[3]:
                    st.metric(
                        "Signal Strength",
                        signals['overall']['signal'].upper(),
                        f"{signals['overall']['strength']:.2%}"
                    )

    async def display_sentiment_analysis(self, symbol):
        """Display sentiment analysis results."""
        sentiment_data = await self.sentiment_analyzer.aggregate_sentiment(symbol)
        
        if sentiment_data:
            st.subheader("Sentiment Analysis")
            
            # Display sentiment score with color coding
            score = sentiment_data['sentiment_score']
            color = 'green' if score > 0 else 'red' if score < 0 else 'gray'
            st.markdown(f"**Sentiment Score:** <span style='color:{color}'>{score:.2f}</span>", 
                       unsafe_allow_html=True)
            
            # Display analysis metrics
            cols = st.columns(2)
            with cols[0]:
                st.metric("Reddit Posts Analyzed", sentiment_data['reddit_posts_analyzed'])
            with cols[1]:
                st.metric("News Items Analyzed", sentiment_data['news_items_analyzed'])

    def run(self):
        """Main dashboard interface."""
        st.set_page_config(page_title="Crypto Trader Dashboard", layout="wide")
        st.title("Crypto Trading Dashboard")

        # Sidebar controls
        st.sidebar.header("Settings")
        selected_symbol = st.sidebar.selectbox("Select Cryptocurrency", CRYPTO_SYMBOLS)
        selected_timeframe = st.sidebar.selectbox("Select Timeframe", TECHNICAL_TIMEFRAMES)
        
        symbol = f"{selected_symbol}USDT"
        
        try:
            # Fetch market data
            data = self.market_data.get_historical_klines(
                symbol, 
                selected_timeframe, 
                lookback_days=30
            )
            
            if not data.empty:
                # Main price chart
                st.plotly_chart(self.plot_price_chart(symbol, selected_timeframe, data), 
                              use_container_width=True)
                
                # Technical indicators
                st.subheader("Technical Analysis")
                self.display_technical_indicators(data)
                
                # Sentiment analysis
                asyncio.run(self.display_sentiment_analysis(selected_symbol))
                
                # Current market stats
                st.subheader("Market Statistics")
                stats = self.market_data.get_24h_stats(symbol)
                if stats:
                    cols = st.columns(4)
                    cols[0].metric("24h Change", f"{stats['price_change_percent']}%")
                    cols[1].metric("Volume", f"{stats['volume']:.2f}")
                    cols[2].metric("Last Price", f"{stats['last_price']:.2f}")
                    cols[3].metric("Weighted Avg", f"{stats['weighted_avg_price']:.2f}")
                
            else:
                st.error("No data available for the selected symbol and timeframe.")
                
        except Exception as e:
            st.error(f"Error loading dashboard: {str(e)}")

if __name__ == "__main__":
    dashboard = Dashboard()
    dashboard.run()
