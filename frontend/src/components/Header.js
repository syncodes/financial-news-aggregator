import React from 'react';
import { AppBar, Toolbar, Typography, Container } from '@mui/material';

const Header = () => {
  return (
    <AppBar position="static" sx={{ mb: 4 }}>
      <Toolbar>
        <Container>
          <Typography variant="h4" component="div" sx={{ flexGrow: 1 }}>
            Financial News Aggregator
          </Typography>
          <Typography variant="subtitle1" sx={{ mt: 1 }}>
            Real-time financial news with sentiment analysis
          </Typography>
        </Container>
      </Toolbar>
    </AppBar>
  );
};

export default Header;
