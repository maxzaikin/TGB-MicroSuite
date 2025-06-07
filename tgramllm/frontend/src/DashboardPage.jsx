import React from 'react';
import { Box, Typography, Button, Container } from '@mui/material';
import { useAuth } from './auth/useAuth';

/**
 * DashboardPage component displays the main dashboard UI for authenticated users.
 * Users can access protected content and logout from this screen.
 */
const DashboardPage = () => {
  const { logout } = useAuth();

  return (
    <Container
      component="main"
      maxWidth="md"
      sx={{
        mt: 8,
        mb: 4,
        textAlign: 'center',
      }}
    >
      <Box
        sx={{
          p: 4,
          boxShadow: 3,
          borderRadius: 2,
          bgcolor: 'background.paper',
        }}
      >
        <Typography variant="h4" component="h1" gutterBottom>
          Welcome to your dashboard
        </Typography>

        <Typography variant="body1" sx={{ mb: 3 }}>
          This is the main content area for your application.
        </Typography>

        <Button
          variant="contained"
          color="error"
          onClick={logout}
          aria-label="Logout and end session"
        >
          Logout
        </Button>
      </Box>
    </Container>
  );
};

export default DashboardPage;
