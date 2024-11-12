from vaderSentiment.vaderSentiment import SentimentIntensifier, SentimentAnalyzer
import praw
import feedparser
import logging
from datetime import datetime, timedelta
from ..config import (
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
        self.analyzer = SentimentAnalyzer()
        self.reddit = praw.Reddit(
            client_id=REDDIT_CLIENT_ID,
            client_secret=REDDIT_CLIENT_SECRET,
            user_agent=REDDIT_USER_AGENT
        )
        # Custom crypto-specific lexicon additions
        self.crypto_lexicon = {
            'hodl': 2.0,
            'moon': 2.0,
            'dump': -2.0,
            'fud': -1.5,
            'shill': -1.0,
            'bullish': 2.0,
            'bearish': -2.0,
            'pump': 1.0,  # Neutral as it can be both positive and negative
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

    def get_reddit_sentiment(self, subreddit_name, symbol, limit=100):
        """Get sentiment from Reddit posts and comments."""
        try:
            subreddit = self.reddit.subreddit(subreddit_name)
            posts = []
            
            # Get posts from last 24 hours
            for post in subreddit.search(symbol, time_filter='day', limit=limit):
                sentiment = self.analyze_text(post.title + " " + post.selftext)
                if sentiment:
                    posts.append({
                        'timestamp': datetime.fromtimestamp(post.created_utc),
                        'title': post.title,
                        'sentiment': sentiment['compound'],
                        'score': post.score,
                        'num_comments': post.num_comments
                    })
            
            return posts
        except Exception as e:
            logger.error(f"Error fetching Reddit data: {e}")
            return []

    def get_news_sentiment(self, rss_feeds):
        """Analyze sentiment from crypto news RSS feeds."""
        try:
            news_items = []
            for feed_url in rss_feeds:
                feed = feedparser.parse(feed_url)
                for entry in feed.entries:
                    # Check if entry is within sentiment window
                    if 'published_parsed' in entry:
                        pub_date = datetime(*entry.published_parsed[:6])
                        if pub_date < datetime.now() - timedelta(hours=SENTIMENT_WINDOW):
                            continue
                    
                    sentiment = self.analyze_text(entry.title + " " + entry.summary)
                    if sentiment:
                        news_items.append({
                            'timestamp': pub_date if 'published_parsed' in entry else datetime.now(),
                            'title': entry.title,
                            'sentiment': sentiment['compound'],
                            'source': feed.feed.title
                        })
            
            return news_items
        except Exception as e:
            logger.error(f"Error fetching news data: {e}")
            return []

    def aggregate_sentiment(self, symbol):
        """Aggregate sentiment from all sources for a specific symbol."""
        try:
            # Get Reddit sentiment from relevant subreddits
            reddit_data = []
            for subreddit in ['cryptocurrency', f'{symbol.lower()}', 'cryptomarkets']:
                reddit_data.extend(self.get_reddit_sentiment(subreddit, symbol))

            # Get news sentiment
            crypto_news_feeds = [
                'https://cointelegraph.com/rss',
                'https://coindesk.com/arc/outboundfeeds/rss/'
            ]
            news_data = self.get_news_sentiment(crypto_news_feeds)

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

            return {
                'symbol': symbol,
                'sentiment_score': final_sentiment,
                'reddit_posts_analyzed': len(reddit_data),
                'news_items_analyzed': len(news_data),
                'timestamp': datetime.now()
            }

        except Exception as e:
            logger.error(f"Error aggregating sentiment for {symbol}: {e}")
            return None
