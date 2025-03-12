import React from 'react';
import { 
  Paper, 
  Typography, 
  Box, 
  FormControl, 
  InputLabel, 
  Select, 
  MenuItem, 
  TextField,
  Grid
} from '@mui/material';

const FilterPanel = ({ sources, filters, onFilterChange }) => {
  const handleChange = (event) => {
    const { name, value } = event.target;
    onFilterChange(name, value);
  };

  const handleSearchChange = (event) => {
    onFilterChange('search', event.target.value);
  };

  return (
    <Paper sx={{ p: 3, mb: 3 }}>
      <Typography variant="h6" gutterBottom>
        Filter News
      </Typography>
      
      <Grid container spacing={3}>
        <Grid item xs={12} sm={4}>
          <FormControl fullWidth>
            <InputLabel id="source-select-label">News Source</InputLabel>
            <Select
              labelId="source-select-label"
              id="source-select"
              name="source"
              value={filters.source}
              label="News Source"
              onChange={handleChange}
            >
              <MenuItem value="">All Sources</MenuItem>
              {sources.map((source) => (
                <MenuItem key={source} value={source}>
                  {source}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </Grid>
        
        <Grid item xs={12} sm={4}>
          <FormControl fullWidth>
            <InputLabel id="sentiment-select-label">Sentiment</InputLabel>
            <Select
              labelId="sentiment-select-label"
              id="sentiment-select"
              name="sentiment"
              value={filters.sentiment}
              label="Sentiment"
              onChange={handleChange}
            >
              <MenuItem value="">All Sentiments</MenuItem>
              <MenuItem value="positive">Positive</MenuItem>
              <MenuItem value="neutral">Neutral</MenuItem>
              <MenuItem value="negative">Negative</MenuItem>
            </Select>
          </FormControl>
        </Grid>
        
        <Grid item xs={12} sm={4}>
          <TextField
            fullWidth
            id="search-input"
            label="Search Keywords"
            variant="outlined"
            value={filters.search}
            onChange={handleSearchChange}
            placeholder="Enter keywords..."
          />
        </Grid>
      </Grid>
    </Paper>
  );
};

export default FilterPanel;
