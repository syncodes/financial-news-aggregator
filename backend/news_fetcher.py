import os
import requests
import json
import feedparser
from datetime import datetime
import time
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Keys
NEWS_API_KEY = os.getenv('NEWS_API_KEY')
ALPHA_VANTAGE_API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY')

# News Sources
RSS_FEEDS = {
    'Yahoo Finance': 'https://finance.yahoo.com/news/rssindex',
    'MarketWatch': 'http://feeds.marketwatch.com/marketwatch/topstories/',
    'CNBC': 'https://www.cnbc.com/id/100003114/device/rss/rss.html',
    'Financial Times': 'https://www.ft.com/?format=rss',
    'Bloomberg': 'https://feeds.bloomberg.com/markets/news.rss',
    'Reuters Business': 'https://www.reutersagency.com/feed/?taxonomy=best-topics&post_type=best',
    'WSJ Markets': 'https://feeds.a.dj.com/rss/RSSMarketsMain.xml'
}

def fetch_from_news_api():
    """Fetch financial news from NewsAPI"""
    if not NEWS_API_KEY:
        print("NewsAPI key not found. Skipping NewsAPI source.")
        return []
    
    url = 'https://newsapi.org/v2/top-headlines'
    params = {
        'apiKey': NEWS_API_KEY,
        'category': 'business',
        'language': 'en',
        'pageSize': 100
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        articles = response.json().get('articles', [])
        
        # Process and standardize article format
        processed_articles = []
        for article in articles:
            if article.get('title') and article.get('url'):
                processed_article = {
                    'title': article.get('title'),
                    'source': {
                        'id': article.get('source', {}).get('id'),
                        'name': article.get('source', {}).get('name', 'NewsAPI')
                    },
                    'author': article.get('author'),
                    'url': article.get('url'),
                    'urlToImage': article.get('urlToImage'),
                    'publishedAt': article.get('publishedAt'),
                    'content': article.get('content') or article.get('description', ''),
                    'description': article.get('description', ''),
                    'fetched_at': datetime.now().isoformat(),
                    'category': 'business'
                }
                processed_articles.append(processed_article)
        
        return processed_articles
    except Exception as e:
        print(f"Error fetching from NewsAPI: {str(e)}")
        return []

def fetch_from_alpha_vantage():
    """Fetch financial news from Alpha Vantage"""
    if not ALPHA_VANTAGE_API_KEY:
        print("Alpha Vantage API key not found. Skipping Alpha Vantage source.")
        return []
    
    url = 'https://www.alphavantage.co/query'
    params = {
        'function': 'NEWS_SENTIMENT',
        'apikey': ALPHA_VANTAGE_API_KEY,
        'topics': 'financial_markets,economy_fiscal,economy_monetary',
        'time_from': '20230101T0000',
        'sort': 'LATEST',
        'limit': 50
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        data = response.json()
        feed = data.get('feed', [])
        
        # Process and standardize article format
        processed_articles = []
        for item in feed:
            if item.get('title') and item.get('url'):
                # Extract sentiment data if available
                sentiment_data = {}
                if 'overall_sentiment_score' in item:
                    score = float(item.get('overall_sentiment_score', 0))
                    label = 'positive' if score > 0.25 else 'negative' if score < -0.25 else 'neutral'
                    sentiment_data = {
                        'score': score,
                        'label': label
                    }
                
                processed_article = {
                    'title': item.get('title'),
                    'source': {
                        'id': 'alphavantage',
                        'name': item.get('source') or 'Alpha Vantage'
                    },
                    'author': item.get('authors', []),
                    'url': item.get('url'),
                    'urlToImage': item.get('banner_image'),
                    'publishedAt': item.get('time_published'),
                    'content': item.get('summary', ''),
                    'description': item.get('summary', ''),
                    'fetched_at': datetime.now().isoformat(),
                    'category': 'business',
                    'sentiment': sentiment_data if sentiment_data else None
                }
                processed_articles.append(processed_article)
        
        return processed_articles
    except Exception as e:
        print(f"Error fetching from Alpha Vantage: {str(e)}")
        return []

def fetch_from_rss_feeds():
    """Fetch financial news from RSS feeds"""
    all_articles = []
    
    for source_name, feed_url in RSS_FEEDS.items():
        try:
            feed = feedparser.parse(feed_url)
            
            for entry in feed.entries[:20]:  # Limit to 20 entries per feed
                if hasattr(entry, 'title') and hasattr(entry, 'link'):
                    # Extract content and clean it
                    content = ''
                    if hasattr(entry, 'content'):
                        content = entry.content[0].value
                    elif hasattr(entry, 'summary'):
                        content = entry.summary
                    elif hasattr(entry, 'description'):
                        content = entry.description
                    
                    # Clean HTML if present
                    if content:
                        soup = BeautifulSoup(content, 'lxml')
                        content = soup.get_text()
                    
                    # Get published date
                    published_at = None
                    if hasattr(entry, 'published'):
                        published_at = entry.published
                    elif hasattr(entry, 'pubDate'):
                        published_at = entry.pubDate
                    elif hasattr(entry, 'updated'):
                        published_at = entry.updated
                    
                    article = {
                        'title': entry.title,
                        'source': {
                            'id': source_name.lower().replace(' ', '_'),
                            'name': source_name
                        },
                        'author': getattr(entry, 'author', None),
                        'url': entry.link,
                        'urlToImage': None,  # RSS often doesn't include images
                        'publishedAt': published_at,
                        'content': content,
                        'description': getattr(entry, 'summary', content[:200] + '...') if content else None,
                        'fetched_at': datetime.now().isoformat(),
                        'category': 'business'
                    }
                    
                    # Try to find an image in the content if available
                    if content:
                        soup = BeautifulSoup(content, 'lxml')
                        img_tag = soup.find('img')
                        if img_tag and img_tag.has_attr('src'):
                            article['urlToImage'] = img_tag['src']
                    
                    all_articles.append(article)
            
            print(f"Fetched {len(feed.entries[:20])} articles from {source_name}")
        except Exception as e:
            print(f"Error fetching from {source_name}: {str(e)}")
    
    return all_articles

def fetch_all_news():
    """Fetch news from all available sources"""
    all_news = []
    
    # Fetch from NewsAPI
    news_api_articles = fetch_from_news_api()
    all_news.extend(news_api_articles)
    
    # Fetch from Alpha Vantage
    alpha_vantage_articles = fetch_from_alpha_vantage()
    all_news.extend(alpha_vantage_articles)
    
    # Fetch from RSS feeds
    rss_articles = fetch_from_rss_feeds()
    all_news.extend(rss_articles)
    
    # Deduplicate articles by URL
    unique_urls = set()
    unique_articles = []
    
    for article in all_news:
        if article['url'] not in unique_urls:
            unique_urls.add(article['url'])
            unique_articles.append(article)
    
    print(f"Fetched a total of {len(unique_articles)} unique articles")
    return unique_articles

# For testing
if __name__ == "__main__":
    articles = fetch_all_news()
    print(f"Total articles: {len(articles)}")
    for i, article in enumerate(articles[:5]):  # Print first 5 for testing
        print(f"\nArticle {i+1}:")
        print(f"Title: {article['title']}")
        print(f"Source: {article['source']['name']}")
        print(f"URL: {article['url']}")
        print(f"Published: {article['publishedAt']}")
        print(f"Content preview: {article['content'][:100]}..." if article['content'] else "No content")
