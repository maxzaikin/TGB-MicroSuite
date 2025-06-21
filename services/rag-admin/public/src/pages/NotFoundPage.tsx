// file: src/pages/NotFoundPage.tsx

import React from 'react';
import { Box, Typography, Button, Container } from '@mui/material';
import { Link } from 'react-router-dom';

export const NotFoundPage: React.FC = () => {
  return (
    <Box
      display="flex"
      justifyContent="center"
      alignItems="center"
      minHeight="100vh"
    >
      <Container maxWidth="md" sx={{ textAlign: 'center' }}>
        <Typography variant="h1" component="h1" color="primary" gutterBottom>
          404
        </Typography>
        <Typography variant="h5" component="h2" sx={{ mb: 4 }}>
          Oops! The page you're looking for doesn't exist.
        </Typography>
        <Button variant="contained" component={Link} to="/">
          Go to Homepage
        </Button>
      </Container>
    </Box>
  );
};