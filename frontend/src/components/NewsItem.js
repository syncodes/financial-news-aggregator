import React from 'react';
import { Card, CardContent, CardActions, Typography, Button, Chip, Box } from '@mui/material';
import { ThumbUp, ThumbDown, Remove } from '@mui/icons-material';

const getSentimentColor = (sentiment) => {
  if (!sentiment || !sentiment.label) return '#757575'; // Default gray
  
  switch (sentiment.label) {
    case 'positive':
      return '#4caf50'; // Green
    case 'negative':
      return '#f44336'; // Red
    default:
      return '#ffb74d'; // Amber for neutral
  }
};

const getSentimentIcon = (sentiment) => {
  if (!sentiment || !sentiment.label) return <Remove />;
  
  switch (sentiment.label) {
    case 'positive':
      return <ThumbUp fontSize="small" />;
    case 'negative':
      return <ThumbDown fontSize="small" />;
    default:
      return <Remove fontSize="small" />;
  }
};

const formatDate = (dateString) => {
  if (!dateString) return 'Unknown date';
  
  const date = new Date(dateString);
  return date.toLocaleString();
};

const NewsItem = ({ article }) => {
  return (
    <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <CardContent sx={{ flexGrow: 1 }}>
        <Typography gutterBottom variant="h6" component="div">
          {article.title}
        </Typography>
        
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Chip 
            size="small" 
            label={article.source?.name || 'Unknown source'} 
            variant="outlined" 
          />
          
          <Chip 
            size="small" 
            icon={getSentimentIcon(article.sentiment)} 
            label={article.sentiment?.label || 'Unknown'} 
            sx={{ 
              backgroundColor: getSentimentColor(article.sentiment),
              color: 'white'
            }}
          />
        </Box>
        
        <Typography variant="body2" color="text.secondary">
          {article.description || 'No description available'}
        </Typography>
        
        <Typography variant="caption" color="text.secondary" sx={{ mt: 2, display: 'block' }}>
          Published: {formatDate(article.publishedAt)}
        </Typography>
      </CardContent>
      
      <CardActions>
        <Button 
          size="small" 
          color="primary" 
          href={article.url} 
          target="_blank" 
          rel="noopener noreferrer"
        >
          Read More
        </Button>
      </CardActions>
    </Card>
  );
};

export default NewsItem;
