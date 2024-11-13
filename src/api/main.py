from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import logging
from datetime import datetime
from typing import Dict, List, Optional

from src.data_collection.market_data import MarketDataCollector
from src.sentiment_analysis.analyzer import SentimentAnalyzer
from src.technical_analysis.indicators import TechnicalAnalyzer
from src.config import CRYPTO_SYMBOLS, TECHNICAL_TIMEFRAMES

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Crypto Sentiment Trader API",
    description="API for cryptocurrency trading based on sentiment and technical analysis",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
market_data = MarketDataCollector()
sentiment_analyzer = SentimentAnalyzer()
technical_analyzer = TechnicalAnalyzer()

@app.get("/")
async def root():
    """Root endpoint returning API status."""
    return {
        "status": "online",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

@app.get("/api/v1/market/prices")
async def get_current_prices():
    """Get current prices for all tracked symbols."""
    try:
        prices = market_data.get_current_prices()
        if not prices:
            raise HTTPException(status_code=500, detail="Failed to fetch current prices")
        return {
            "timestamp": datetime.now().isoformat(),
            "prices": prices
        }
    except Exception as e:
        logger.error(f"Error in get_current_prices: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/market/historical/{symbol}")
async def get_historical_data(symbol: str, interval: str = "1h", days: int = 7):
    """Get historical price data for a specific symbol."""
    try:
        if symbol not in [f"{s}USDT" for s in CRYPTO_SYMBOLS]:
            raise HTTPException(status_code=400, detail="Invalid symbol")
        if interval not in TECHNICAL_TIMEFRAMES:
            raise HTTPException(status_code=400, detail="Invalid interval")
        
        data = market_data.get_historical_klines(symbol, interval, days)
        if data.empty:
            raise HTTPException(status_code=404, detail="No historical data found")
        
        return {
            "symbol": symbol,
            "interval": interval,
            "data": data.reset_index().to_dict(orient='records')
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_historical_data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/analysis/sentiment/{symbol}")
async def get_sentiment_analysis(symbol: str):
    """Get sentiment analysis for a specific symbol."""
    try:
        if symbol not in CRYPTO_SYMBOLS:
            raise HTTPException(status_code=400, detail="Invalid symbol")
        
        sentiment = await sentiment_analyzer.aggregate_sentiment(symbol)
        if not sentiment:
            raise HTTPException(status_code=500, detail="Failed to analyze sentiment")
        
        return sentiment
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_sentiment_analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/analysis/technical/{symbol}")
async def get_technical_analysis(symbol: str, interval: str = "1h"):
    """Get technical analysis for a specific symbol."""
    try:
        if symbol not in [f"{s}USDT" for s in CRYPTO_SYMBOLS]:
            raise HTTPException(status_code=400, detail="Invalid symbol")
        if interval not in TECHNICAL_TIMEFRAMES:
            raise HTTPException(status_code=400, detail="Invalid interval")
        
        # Get historical data for technical analysis
        data = market_data.get_historical_klines(symbol, interval, 30)  # 30 days of data
        if data.empty:
            raise HTTPException(status_code=404, detail="No data available for analysis")
        
        # Generate technical signals
        signals = technical_analyzer.generate_signals(data)
        if not signals:
            raise HTTPException(status_code=500, detail="Failed to generate technical signals")
        
        return {
            "symbol": symbol,
            "interval": interval,
            "timestamp": datetime.now().isoformat(),
            "signals": signals
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_technical_analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/trading/signals/{symbol}")
async def get_trading_signals(symbol: str):
    """Get combined trading signals (technical + sentiment) for a symbol."""
    try:
        if symbol not in CRYPTO_SYMBOLS:
            raise HTTPException(status_code=400, detail="Invalid symbol")
        
        # Get both technical and sentiment analysis
        sentiment = await sentiment_analyzer.aggregate_sentiment(symbol)
        technical = await get_technical_analysis(f"{symbol}USDT", "1h")
        
        if not sentiment or not technical:
            raise HTTPException(status_code=500, detail="Failed to generate trading signals")
        
        # Combine signals
        sentiment_signal = "buy" if sentiment['sentiment_score'] > 0.2 else "sell" if sentiment['sentiment_score'] < -0.2 else "neutral"
        technical_signal = technical['signals']['overall']['signal']
        
        # Calculate combined signal
        signals_map = {"buy": 1, "neutral": 0, "sell": -1}
        combined_score = (signals_map[sentiment_signal] + signals_map[technical_signal]) / 2
        
        combined_signal = "buy" if combined_score > 0.3 else "sell" if combined_score < -0.3 else "neutral"
        
        return {
            "symbol": symbol,
            "timestamp": datetime.now().isoformat(),
            "sentiment": {
                "score": sentiment['sentiment_score'],
                "signal": sentiment_signal
            },
            "technical": {
                "signal": technical_signal,
                "strength": technical['signals']['overall']['strength']
            },
            "combined_signal": combined_signal,
            "confidence": abs(combined_score)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_trading_signals: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
