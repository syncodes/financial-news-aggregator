# Financial News Aggregator

A real-time financial news aggregator that collects news from various sources and provides sentiment analysis for each news article.

## Features

- Real-time news collection from various financial news outlets
- Sentiment analysis for each news article
- Filtering by category, source, and sentiment
- User-friendly web interface with responsive design
- API endpoints for programmatic access

## Project Structure

- `backend/`: Flask backend with news fetching and sentiment analysis
- `frontend/`: React frontend for displaying news and sentiment

## Setup Instructions

### Backend Setup

1. Navigate to the backend directory:
   ```
   cd backend
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   ```

3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - Linux/Mac: `source venv/bin/activate`

4. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

5. Set up environment variables:
   - Copy `.env.example` to `.env`
   - Add your API keys for news services

6. Run the Flask application:
   ```
   python app.py
   ```

### Frontend Setup

1. Navigate to the frontend directory:
   ```
   cd frontend
   ```

2. Install dependencies:
   ```
   npm install
   ```

3. Run the development server:
   ```
   npm start
   ```

## Technologies Used

- Backend: Python, Flask, NLTK/TextBlob (sentiment analysis)
- Frontend: React, Material-UI
- News Sources: Various financial news APIs (NewsAPI, Alpha Vantage, etc.)
- Database: SQLite (development), PostgreSQL (production)
