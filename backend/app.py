from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import json
from datetime import datetime
import threading
import time
import schedule
from dotenv import load_dotenv

# Import custom modules
from news_fetcher import fetch_all_news
from sentiment_analyzer import analyze_sentiment
from database import init_db, get_db, save_news, get_all_news, get_news_by_source, get_news_by_sentiment

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize database
init_db()

# News update interval in minutes
UPDATE_INTERVAL = int(os.getenv('UPDATE_INTERVAL', '15'))

def update_news_data():
    """Fetch and update news data periodically"""
    print(f"[{datetime.now()}] Updating news data...")
    try:
        # Fetch news from various sources
        news_articles = fetch_all_news()
        
        # Analyze sentiment for each article
        for article in news_articles:
            if 'content' in article and article['content']:
                sentiment_data = analyze_sentiment(article['content'])
                article['sentiment'] = sentiment_data
            else:
                article['sentiment'] = {'score': 0.0, 'label': 'neutral'}
        
        # Save to database
        for article in news_articles:
            save_news(article)
            
        print(f"[{datetime.now()}] Updated {len(news_articles)} news articles")
    except Exception as e:
        print(f"[{datetime.now()}] Error updating news data: {str(e)}")

def start_scheduler():
    """Start the scheduler for periodic news updates"""
    schedule.every(UPDATE_INTERVAL).minutes.do(update_news_data)
    
    # Run the initial update
    update_news_data()
    
    while True:
        schedule.run_pending()
        time.sleep(1)

# Serve a simple HTML page at the root URL
@app.route('/')
def index():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Financial News Aggregator</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 0;
                display: flex;
                justify-content: center;
                align-items: center;
                min-height: 100vh;
                background-color: #f5f5f5;
                flex-direction: column;
            }
            .container {
                text-align: center;
                padding: 2rem;
                background: white;
                border-radius: 8px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.1);
                max-width: 800px;
                width: 90%;
            }
            h1 {
                color: #1976d2;
                margin-bottom: 1rem;
            }
            p {
                margin-bottom: 1.5rem;
                color: #555;
                line-height: 1.6;
            }
            .endpoints {
                text-align: left;
                background: #f8f8f8;
                padding: 1rem;
                border-radius: 4px;
                margin-bottom: 1.5rem;
            }
            .endpoints h3 {
                margin-top: 0;
                color: #444;
            }
            .endpoints ul {
                padding-left: 20px;
            }
            .endpoints li {
                margin-bottom: 0.5rem;
            }
            .badge {
                display: inline-block;
                padding: 4px 8px;
                border-radius: 4px;
                font-size: 12px;
                font-weight: bold;
                margin-right: 8px;
                color: white;
            }
            .badge.get {
                background-color: #4caf50;
            }
            .status {
                margin-top: 2rem;
                padding: 1rem;
                background: #e8f5e9;
                border-radius: 4px;
                font-weight: bold;
                color: #2e7d32;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Financial News Aggregator API</h1>
            <p>This is the backend server for the Financial News Aggregator application. The server provides real-time financial news with sentiment analysis through REST API endpoints.</p>
            
            <div class="endpoints">
                <h3>Available Endpoints:</h3>
                <ul>
                    <li><span class="badge get">GET</span> <code>/api/news</code> - Get all news articles with optional filtering</li>
                    <li><span class="badge get">GET</span> <code>/api/news/sources</code> - Get list of available news sources</li>
                    <li><span class="badge get">GET</span> <code>/api/news/stats</code> - Get statistics about the news articles</li>
                </ul>
            </div>
            
            <p>For the complete frontend experience, the React frontend needs to be started separately. Check the README.md file for instructions.</p>
            
            <div class="status">Server Status: Running</div>
        </div>
    </body>
    </html>
    """

# API Routes
@app.route('/api/news', methods=['GET'])
def get_news():
    """Get all news articles with optional filtering"""
    source = request.args.get('source', None)
    sentiment = request.args.get('sentiment', None)
    
    if source:
        news = get_news_by_source(source)
    elif sentiment:
        news = get_news_by_sentiment(sentiment)
    else:
        news = get_all_news()
    
    return jsonify({
        'status': 'success',
        'count': len(news),
        'data': news
    })

@app.route('/api/news/sources', methods=['GET'])
def get_sources():
    """Get list of available news sources"""
    news = get_all_news()
    sources = list(set(article['source']['name'] for article in news if 'source' in article and 'name' in article['source']))
    
    return jsonify({
        'status': 'success',
        'count': len(sources),
        'data': sources
    })

@app.route('/api/news/stats', methods=['GET'])
def get_stats():
    """Get statistics about the news articles"""
    news = get_all_news()
    
    # Count articles by sentiment
    sentiment_counts = {
        'positive': 0,
        'neutral': 0,
        'negative': 0
    }
    
    for article in news:
        if 'sentiment' in article and 'label' in article['sentiment']:
            label = article['sentiment']['label']
            if label in sentiment_counts:
                sentiment_counts[label] += 1
    
    # Count articles by source
    source_counts = {}
    for article in news:
        if 'source' in article and 'name' in article['source']:
            source_name = article['source']['name']
            source_counts[source_name] = source_counts.get(source_name, 0) + 1
    
    return jsonify({
        'status': 'success',
        'data': {
            'total_articles': len(news),
            'sentiment_distribution': sentiment_counts,
            'source_distribution': source_counts
        }
    })

if __name__ == '__main__':
    # Start the news update scheduler in a separate thread
    scheduler_thread = threading.Thread(target=start_scheduler)
    scheduler_thread.daemon = True
    scheduler_thread.start()
    
    # Run the Flask app
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
