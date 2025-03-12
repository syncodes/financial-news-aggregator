import React from 'react';
import { Grid, Typography, Box } from '@mui/material';
import NewsItem from './NewsItem';

const NewsGrid = ({ news }) => {
  if (!news || news.length === 0) {
    return (
      <Box sx={{ textAlign: 'center', py: 5 }}>
        <Typography variant="h5" color="text.secondary">
          No news articles found. Try adjusting your filters.
        </Typography>
      </Box>
    );
  }

  return (
    <Box>
      <Typography variant="h5" gutterBottom>
        News Articles ({news.length})
      </Typography>
      <Grid container spacing={3}>
        {news.map((article, index) => (
          <Grid item xs={12} sm={6} md={4} key={article.id || index}>
            <NewsItem article={article} />
          </Grid>
        ))}
      </Grid>
    </Box>
  );
};

export default NewsGrid;
