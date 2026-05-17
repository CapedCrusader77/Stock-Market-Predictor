"""
Sentiment Analyzer - News sentiment analysis for stocks
"""

import requests
import feedparser
from typing import Dict, List
from datetime import datetime, timedelta
import os

class SentimentAnalyzer:
    def __init__(self):
        self.news_sources = {
            "bloomberg": "https://feeds.bloomberg.com/markets/news.rss",
            "cnbc": "https://feeds.cnbc.com/cnbc/latest",
            "reuters": "https://feeds.reuters.com/reuters/businessNews"
        }
    
    def analyze_sentiment(self, text: str) -> Dict:
        """Analyze sentiment of text"""
        try:
            # Simple sentiment analysis based on keywords
            positive_words = ["gain", "surge", "bull", "up", "rally", "strong", "growth", "profit"]
            negative_words = ["loss", "decline", "bear", "down", "crash", "weak", "fall", "loss"]
            
            text_lower = text.lower()
            
            positive_count = sum(1 for word in positive_words if word in text_lower)
            negative_count = sum(1 for word in negative_words if word in text_lower)
            
            if positive_count + negative_count == 0:
                sentiment_score = 0.5
            else:
                sentiment_score = positive_count / (positive_count + negative_count)
            
            if sentiment_score > 0.6:
                sentiment = "POSITIVE"
            elif sentiment_score < 0.4:
                sentiment = "NEGATIVE"
            else:
                sentiment = "NEUTRAL"
            
            return {
                "sentiment": sentiment,
                "score": float(sentiment_score),
                "positive_count": positive_count,
                "negative_count": negative_count
            }
        except Exception as e:
            return {"sentiment": "NEUTRAL", "score": 0.5, "error": str(e)}
    
    def fetch_news(self, ticker: str, limit: int = 10) -> List[Dict]:
        """Fetch news for a ticker"""
        try:
            news_items = []
            
            # Add timeout and headers to requests
            import requests
            session = requests.Session()
            session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            
            for source_name, feed_url in self.news_sources.items():
                try:
                    # Add timeout to prevent hanging
                    response = session.get(feed_url, timeout=10)
                    feed = feedparser.parse(response.content)
                    
                    for entry in feed.entries[:limit]:
                        if ticker in entry.get("title", "").upper() or ticker in entry.get("summary", "").upper():
                            sentiment = self.analyze_sentiment(
                                entry.get("summary", "") + " " + entry.get("title", "")
                            )
                            
                            news_items.append({
                                "source": source_name,
                                "title": entry.get("title", ""),
                                "link": entry.get("link", ""),
                                "published": entry.get("published", ""),
                                "summary": entry.get("summary", "")[:200],
                                "sentiment": sentiment["sentiment"],
                                "sentiment_score": sentiment["score"]
                            })
                except Exception as e:
                    print(f"Error fetching from {source_name}: {e}")
                    continue
            
            return sorted(news_items, key=lambda x: x["sentiment_score"], reverse=True)[:limit]
        except Exception as e:
            print(f"Error in fetch_news: {e}")
            return []
    
    def get_sentiment_summary(self, ticker: str) -> Dict:
        """Get overall sentiment for a ticker"""
        try:
            news = self.fetch_news(ticker, limit=20)
            
            if not news:
                return {
                    "ticker": ticker,
                    "overall_sentiment": "NEUTRAL",
                    "average_score": 0.5,
                    "positive_count": 0,
                    "negative_count": 0,
                    "neutral_count": 0
                }
            
            positive = sum(1 for n in news if n["sentiment"] == "POSITIVE")
            negative = sum(1 for n in news if n["sentiment"] == "NEGATIVE")
            neutral = len(news) - positive - negative
            
            avg_score = sum(n["sentiment_score"] for n in news) / len(news)
            
            if avg_score > 0.6:
                overall = "POSITIVE"
            elif avg_score < 0.4:
                overall = "NEGATIVE"
            else:
                overall = "NEUTRAL"
            
            return {
                "ticker": ticker,
                "overall_sentiment": overall,
                "average_score": float(avg_score),
                "positive_count": positive,
                "negative_count": negative,
                "neutral_count": neutral,
                "total_articles": len(news)
            }
        except Exception as e:
            return {"error": str(e)}
