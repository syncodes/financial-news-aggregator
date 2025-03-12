import os
import json
from datetime import datetime
import pymongo
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# MongoDB settings
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
DB_NAME = os.getenv('DB_NAME', 'financial_news_aggregator')
COLLECTION_NAME = 'news_articles'

# Fallback to local JSON storage if MongoDB is not available
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
NEWS_FILE = os.path.join(DATA_DIR, 'news.json')

# Initialize database client
mongo_client = None

def init_db():
    """Initialize the database connection or local storage"""
    global mongo_client
    
    # Create data directory if using local storage
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    
    # Initialize news.json if it doesn't exist
    if not os.path.exists(NEWS_FILE):
        with open(NEWS_FILE, 'w') as f:
            json.dump([], f)
    
    # Try to connect to MongoDB
    try:
        if MONGO_URI != 'mongodb://localhost:27017/':  # Only try if URI is configured
            mongo_client = pymongo.MongoClient(MONGO_URI, serverSelectionTimeoutMS=2000)
            # Validate the connection
            mongo_client.server_info()
            print("Successfully connected to MongoDB")
        else:
            print("MongoDB URI not configured, falling back to local JSON storage")
    except Exception as e:
        print(f"Could not connect to MongoDB: {str(e)}")
        print("Falling back to local JSON storage")
        mongo_client = None

def get_db():
    """Get database connection or local storage reference"""
    if mongo_client:
        return mongo_client[DB_NAME]
    return None

def save_news(article):
    """Save a news article to the database"""
    # Generate a unique ID if not present
    if '_id' not in article:
        # Use URL as a unique identifier
        article['_id'] = article['url']
    
    # Add timestamp if not present
    if 'timestamp' not in article:
        article['timestamp'] = datetime.now().isoformat()
    
    if mongo_client:
        try:
            db = mongo_client[DB_NAME]
            collection = db[COLLECTION_NAME]
            
            # Upsert the document (insert if not exists, update if exists)
            collection.update_one(
                {'_id': article['_id']},
                {'$set': article},
                upsert=True
            )
            return True
        except Exception as e:
            print(f"Error saving to MongoDB: {str(e)}")
            # Fallback to JSON storage
            return _save_to_json(article)
    else:
        # Use JSON storage
        return _save_to_json(article)

def _save_to_json(article):
    """Save a news article to local JSON file"""
    try:
        # Read existing data
        with open(NEWS_FILE, 'r') as f:
            news_data = json.load(f)
        
        # Check if article with same URL exists
        exists = False
        for i, existing_article in enumerate(news_data):
            if existing_article.get('url') == article.get('url'):
                # Update existing article
                news_data[i] = article
                exists = True
                break
        
        # Add new article if not exists
        if not exists:
            news_data.append(article)
        
        # Write back to file
        with open(NEWS_FILE, 'w') as f:
            json.dump(news_data, f, indent=2)
        
        return True
    except Exception as e:
        print(f"Error saving to JSON file: {str(e)}")
        return False

def get_all_news():
    """Get all news articles"""
    if mongo_client:
        try:
            db = mongo_client[DB_NAME]
            collection = db[COLLECTION_NAME]
            
            # Get all articles, sorted by published date (newest first)
            cursor = collection.find({}).sort('publishedAt', pymongo.DESCENDING)
            articles = list(cursor)
            
            # Convert ObjectId to string for JSON serialization
            for article in articles:
                if '_id' in article and isinstance(article['_id'], pymongo.ObjectId):
                    article['_id'] = str(article['_id'])
            
            return articles
        except Exception as e:
            print(f"Error retrieving from MongoDB: {str(e)}")
            # Fallback to JSON storage
            return _get_from_json()
    else:
        # Use JSON storage
        return _get_from_json()

def _get_from_json():
    """Get all news articles from local JSON file"""
    try:
        with open(NEWS_FILE, 'r') as f:
            news_data = json.load(f)
        
        # Sort by published date (newest first)
        news_data.sort(
            key=lambda x: x.get('publishedAt', x.get('timestamp', '')), 
            reverse=True
        )
        
        return news_data
    except Exception as e:
        print(f"Error reading from JSON file: {str(e)}")
        return []

def get_news_by_source(source_name):
    """Get news articles by source name"""
    all_news = get_all_news()
    
    # Filter by source name
    filtered_news = [
        article for article in all_news 
        if article.get('source') and article['source'].get('name') == source_name
    ]
    
    return filtered_news

def get_news_by_sentiment(sentiment_label):
    """Get news articles by sentiment label"""
    all_news = get_all_news()
    
    # Filter by sentiment label
    filtered_news = [
        article for article in all_news 
        if article.get('sentiment') and article['sentiment'].get('label') == sentiment_label
    ]
    
    return filtered_news

def delete_old_news(days=30):
    """Delete news articles older than specified days"""
    # Calculate the cutoff date
    cutoff_date = datetime.now().replace(
        hour=0, minute=0, second=0, microsecond=0
    ).timestamp() - (days * 24 * 60 * 60)
    
    if mongo_client:
        try:
            db = mongo_client[DB_NAME]
            collection = db[COLLECTION_NAME]
            
            # Delete old articles
            result = collection.delete_many({
                'publishedAt': {'$lt': datetime.fromtimestamp(cutoff_date).isoformat()}
            })
            
            print(f"Deleted {result.deleted_count} old articles from MongoDB")
            return result.deleted_count
        except Exception as e:
            print(f"Error deleting from MongoDB: {str(e)}")
            # Fallback to JSON storage
            return _delete_old_from_json(cutoff_date)
    else:
        # Use JSON storage
        return _delete_old_from_json(cutoff_date)

def _delete_old_from_json(cutoff_timestamp):
    """Delete old news articles from local JSON file"""
    try:
        with open(NEWS_FILE, 'r') as f:
            news_data = json.load(f)
        
        # Count initial articles
        initial_count = len(news_data)
        
        # Filter out old articles
        news_data = [
            article for article in news_data
            if article.get('publishedAt', datetime.now().isoformat()) > datetime.fromtimestamp(cutoff_timestamp).isoformat()
        ]
        
        # Write back to file
        with open(NEWS_FILE, 'w') as f:
            json.dump(news_data, f, indent=2)
        
        deleted_count = initial_count - len(news_data)
        print(f"Deleted {deleted_count} old articles from JSON file")
        return deleted_count
    except Exception as e:
        print(f"Error deleting from JSON file: {str(e)}")
        return 0

# For testing
if __name__ == "__main__":
    init_db()
    print("Database initialized")
