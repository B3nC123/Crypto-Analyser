from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import asyncpraw
import feedparser
import logging
import asyncio
import aiohttp
from datetime import datetime, timedelta
from src.config import (
    REDDIT_CLIENT_ID,
    REDDIT_CLIENT_SECRET,
    REDDIT_USER_AGENT,
    CRYPTO_SYMBOLS,
    SENTIMENT_WINDOW
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SentimentAnalyzer:
    def __init__(self):
        self.analyzer = SentimentIntensityAnalyzer()
        self.session = None
        self.reddit_available = False
        
        # Custom crypto-specific lexicon additions
        self.crypto_lexicon = {
            'hodl': 2.0,
            'moon': 2.0,
            'dump': -2.0,
            'fud': -1.5,
            'shill': -1.0,
            'bullish': 2.0,
            'bearish': -2.0,
            'pump': 1.0,
            'dip': -0.5,
            'correction': -1.0,
            'accumulate': 1.0,
            'buy': 1.0,
            'sell': -1.0,
            'long': 1.0,
            'short': -1.0
        }
        self._update_lexicon()

    def _update_lexicon(self):
        """Update the sentiment analyzer's lexicon with crypto-specific terms."""
        self.analyzer.lexicon.update(self.crypto_lexicon)

    async def _init_session(self):
        """Initialize aiohttp session if not already initialized."""
        if self.session is None:
            self.session = aiohttp.ClientSession()

    def analyze_text(self, text):
        """Analyze sentiment of a single text."""
        try:
            scores = self.analyzer.polarity_scores(text)
            return {
                'compound': scores['compound'],
                'pos': scores['pos'],
                'neu': scores['neu'],
                'neg': scores['neg']
            }
        except Exception as e:
            logger.error(f"Error analyzing text: {e}")
            return None

    async def get_reddit_sentiment(self, subreddit_name, symbol, limit=100):
        """Get sentiment from Reddit posts using public JSON API."""
        await self._init_session()
        posts = []
        
        try:
            url = f"https://www.reddit.com/r/{subreddit_name}/search.json"
            params = {
                'q': symbol,
                't': 'day',
                'limit': limit,
                'restrict_sr': 'on'
            }
            headers = {'User-Agent': REDDIT_USER_AGENT}
            
            async with self.session.get(url, params=params, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if 'data' in data and 'children' in data['data']:
                        for post in data['data']['children']:
                            post_data = post['data']
                            
                            # Check if post mentions the symbol
                            if symbol in post_data.get('title', '') or symbol in post_data.get('selftext', ''):
                                text = post_data['title']
                                if 'selftext' in post_data:
                                    text += " " + post_data['selftext']
                                    
                                sentiment = self.analyze_text(text)
                                if sentiment:
                                    posts.append({
                                        'timestamp': datetime.fromtimestamp(post_data['created_utc']),
                                        'title': post_data['title'],
                                        'sentiment': sentiment['compound'],
                                        'score': post_data['score'],
                                        'num_comments': post_data['num_comments']
                                    })
                else:
                    logger.warning(f"Failed to fetch Reddit data: {response.status}")
            
            return posts
        except Exception as e:
            logger.error(f"Error fetching Reddit data: {e}")
            return []

    def get_news_sentiment(self, rss_feeds, symbol):
        """Analyze sentiment from crypto news RSS feeds."""
        try:
            news_items = []
            for feed_url in rss_feeds:
                try:
                    feed = feedparser.parse(feed_url)
                    for entry in feed.entries:
                        # Check if entry is within sentiment window
                        if 'published_parsed' in entry:
                            pub_date = datetime(*entry.published_parsed[:6])
                            if pub_date < datetime.now() - timedelta(hours=SENTIMENT_WINDOW):
                                continue
                        
                        # Only analyze entries that mention the specific symbol
                        title_and_summary = (entry.title + " " + entry.summary).upper()
                        if symbol not in title_and_summary:
                            continue

                        sentiment = self.analyze_text(entry.title + " " + entry.summary)
                        if sentiment:
                            news_items.append({
                                'timestamp': pub_date if 'published_parsed' in entry else datetime.now(),
                                'title': entry.title,
                                'sentiment': sentiment['compound'],
                                'source': feed.feed.title
                            })
                except Exception as e:
                    logger.error(f"Error processing feed {feed_url}: {e}")
                    continue
            
            return news_items
        except Exception as e:
            logger.error(f"Error fetching news data: {e}")
            return []

    async def aggregate_sentiment(self, symbol):
        """Aggregate sentiment from all sources for a specific symbol."""
        try:
            # Get Reddit sentiment from relevant subreddits
            reddit_data = []
            subreddits = ['cryptocurrency', f'{symbol.lower()}', 'cryptomarkets']
            for subreddit in subreddits:
                reddit_posts = await self.get_reddit_sentiment(subreddit, symbol)
                reddit_data.extend(reddit_posts)

            # Get news sentiment
            crypto_news_feeds = [
                'https://cointelegraph.com/rss',
                'https://coindesk.com/arc/outboundfeeds/rss/'
            ]
            news_data = self.get_news_sentiment(crypto_news_feeds, symbol)

            # Calculate weighted sentiment
            total_weight = 0
            weighted_sentiment = 0

            # Weight Reddit posts by score and number of comments
            for post in reddit_data:
                weight = (post['score'] + post['num_comments']) / 100
                weighted_sentiment += post['sentiment'] * weight
                total_weight += weight

            # Weight news items (could be enhanced with source reliability scores)
            for item in news_data:
                weight = 1  # Base weight for news items
                weighted_sentiment += item['sentiment'] * weight
                total_weight += weight

            if total_weight > 0:
                final_sentiment = weighted_sentiment / total_weight
            else:
                final_sentiment = 0

            # Close the session if it exists
            if self.session:
                await self.session.close()
                self.session = None

            return {
                'symbol': symbol,
                'sentiment_score': final_sentiment,
                'reddit_posts_analyzed': len(reddit_data),
                'news_items_analyzed': len(news_data),
                'timestamp': datetime.now()
            }

        except Exception as e:
            logger.error(f"Error aggregating sentiment for {symbol}: {e}")
            if self.session:
                await self.session.close()
                self.session = None
            return {
                'symbol': symbol,
                'sentiment_score': 0,
                'reddit_posts_analyzed': 0,
                'news_items_analyzed': 0,
                'timestamp': datetime.now(),
                'error': str(e)
            }
