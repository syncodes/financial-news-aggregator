import nltk
import os
from textblob import TextBlob
import re
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

# Ensure NLTK resources are downloaded
def download_nltk_resources():
    """Download required NLTK resources"""
    resources = ['punkt', 'stopwords', 'wordnet']
    for resource in resources:
        try:
            nltk.data.find(f'tokenizers/{resource}' if resource == 'punkt' else f'corpora/{resource}')
        except LookupError:
            print(f"Downloading NLTK resource: {resource}")
            nltk.download(resource, quiet=True)

# Download resources if needed
download_nltk_resources()

# Initialize lemmatizer and stopwords
lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words('english'))

# Financial-specific sentiment lexicon
# These are words that might have special significance in financial news
FINANCIAL_POSITIVE_WORDS = {
    'growth', 'profit', 'profitable', 'gain', 'surge', 'uptrend', 'bullish', 'rally',
    'outperform', 'recovery', 'rebound', 'robust', 'strong', 'strengthen', 'upgrade',
    'beat', 'exceeded', 'exceed', 'higher', 'record', 'opportunity', 'breakthrough'
}

FINANCIAL_NEGATIVE_WORDS = {
    'recession', 'crisis', 'debt', 'deficit', 'loss', 'decline', 'downturn', 'bearish',
    'downgrade', 'underperform', 'weak', 'weaken', 'plunge', 'plummet', 'crash', 'bankruptcy',
    'default', 'risk', 'volatile', 'miss', 'missed', 'disappointment', 'concern', 'threat',
    'inflation', 'layoff', 'downsize', 'cut', 'shutdown', 'liability'
}

def preprocess_text(text):
    """Preprocess text for sentiment analysis"""
    if not text:
        return ""
    
    # Convert to lowercase
    text = text.lower()
    
    # Remove URLs
    text = re.sub(r'https?://\S+|www\.\S+', '', text)
    
    # Remove HTML tags
    text = re.sub(r'<.*?>', '', text)
    
    # Remove special characters and numbers
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    
    # Tokenize
    tokens = word_tokenize(text)
    
    # Remove stopwords and lemmatize
    cleaned_tokens = [lemmatizer.lemmatize(word) for word in tokens if word not in stop_words]
    
    # Join back to string
    cleaned_text = ' '.join(cleaned_tokens)
    
    return cleaned_text

def adjust_sentiment_for_financial_context(text, base_score):
    """Adjust sentiment score based on financial context"""
    adjustment = 0
    
    # Count financial-specific positive and negative words
    words = set(word.lower() for word in word_tokenize(text))
    
    positive_matches = words.intersection(FINANCIAL_POSITIVE_WORDS)
    negative_matches = words.intersection(FINANCIAL_NEGATIVE_WORDS)
    
    # Apply adjustment based on financial terms
    adjustment += len(positive_matches) * 0.05
    adjustment -= len(negative_matches) * 0.05
    
    # Cap adjustment to prevent extreme values
    adjustment = max(-0.3, min(0.3, adjustment))
    
    # Apply adjustment and ensure score stays in [-1, 1] range
    adjusted_score = base_score + adjustment
    adjusted_score = max(-1.0, min(1.0, adjusted_score))
    
    return adjusted_score

def analyze_sentiment(text):
    """Analyze sentiment of text and return score and label"""
    if not text:
        return {'score': 0.0, 'label': 'neutral'}
    
    # Preprocess the text
    cleaned_text = preprocess_text(text)
    
    # Skip empty text after preprocessing
    if not cleaned_text:
        return {'score': 0.0, 'label': 'neutral'}
    
    # Get base sentiment using TextBlob
    blob = TextBlob(cleaned_text)
    base_sentiment_score = blob.sentiment.polarity
    
    # Adjust sentiment for financial context
    adjusted_score = adjust_sentiment_for_financial_context(text, base_sentiment_score)
    
    # Determine sentiment label
    if adjusted_score > 0.05:
        label = 'positive'
    elif adjusted_score < -0.05:
        label = 'negative'
    else:
        label = 'neutral'
    
    return {
        'score': round(adjusted_score, 4),
        'label': label
    }

# For testing
if __name__ == "__main__":
    test_texts = [
        "Company XYZ reported a 20% increase in quarterly profits, exceeding analyst expectations.",
        "Markets plummeted today as fears of recession grow amid rising inflation.",
        "The central bank kept interest rates unchanged, in line with expectations.",
        "Company ABC announced layoffs affecting 15% of its workforce due to restructuring.",
        "Investors remain cautious as geopolitical tensions rise."
    ]
    
    for text in test_texts:
        sentiment = analyze_sentiment(text)
        print(f"Text: {text}")
        print(f"Sentiment: {sentiment['label']} (Score: {sentiment['score']})")
        print()
