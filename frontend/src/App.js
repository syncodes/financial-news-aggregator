import React, { useState, useEffect } from 'react';
import { Container, CssBaseline, Box, Typography, CircularProgress } from '@mui/material';
import { createTheme, ThemeProvider } from '@mui/material/styles';
import Header from './components/Header';
import NewsGrid from './components/NewsGrid';
import FilterPanel from './components/FilterPanel';
import SentimentChart from './components/SentimentChart';
import ErrorState from './components/ErrorState';
import api from './services/api';

const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
    background: {
      default: '#f5f5f5',
    },
  },
  typography: {
    fontFamily: [
      '-apple-system',
      'BlinkMacSystemFont',
      '"Segoe UI"',
      'Roboto',
      '"Helvetica Neue"',
      'Arial',
      'sans-serif',
    ].join(','),
  },
});

function App() {
  const [news, setNews] = useState([]);
  const [filteredNews, setFilteredNews] = useState([]);
  const [sources, setSources] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filters, setFilters] = useState({
    source: '',
    sentiment: '',
    search: ''
  });

  // Fetch all data when component mounts
  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        
        // Fetch news articles
        const newsResponse = await api.getNews();
        setNews(newsResponse.data);
        setFilteredNews(newsResponse.data);
        
        // Fetch available sources
        const sourcesResponse = await api.getSources();
        setSources(sourcesResponse.data);
        
        // Fetch statistics
        const statsResponse = await api.getStats();
        setStats(statsResponse.data);
        
        setLoading(false);
      } catch (err) {
        console.error('Error fetching data:', err);
        setError('Failed to fetch data. Please try again later.');
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  // Apply filters when filters state changes
  useEffect(() => {
    let result = [...news];
    
    // Apply source filter
    if (filters.source) {
      result = result.filter(article => 
        article.source && article.source.name === filters.source
      );
    }
    
    // Apply sentiment filter
    if (filters.sentiment) {
      result = result.filter(article => 
        article.sentiment && article.sentiment.label === filters.sentiment
      );
    }
    
    // Apply search filter
    if (filters.search) {
      const searchTerm = filters.search.toLowerCase();
      result = result.filter(article => 
        (article.title && article.title.toLowerCase().includes(searchTerm)) || 
        (article.description && article.description.toLowerCase().includes(searchTerm))
      );
    }
    
    setFilteredNews(result);
  }, [filters, news]);

  const handleFilterChange = (name, value) => {
    setFilters(prev => ({ ...prev, [name]: value }));
  };

  if (error) {
    return <ErrorState message={error} />;
  }

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Header />
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        {loading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '70vh' }}>
            <CircularProgress />
          </Box>
        ) : (
          <>
            <Box sx={{ mb: 4 }}>
              <FilterPanel 
                sources={sources} 
                filters={filters} 
                onFilterChange={handleFilterChange} 
              />
            </Box>
            
            {stats && (
              <Box sx={{ mb: 4 }}>
                <Typography variant="h5" gutterBottom>
                  Sentiment Distribution
                </Typography>
                <SentimentChart data={stats.sentiment_distribution} />
              </Box>
            )}
            
            <NewsGrid news={filteredNews} />
          </>
        )}
      </Container>
    </ThemeProvider>
  );
}

export default App;
