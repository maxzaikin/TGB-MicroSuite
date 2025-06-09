// src/features/auth/routes/LoginPage.jsx

import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth'; // Use our global auth hook
import apiClient from '../../../services/apiClient'; // Correct path to apiClient

// Material-UI imports
import {
  Container, Box, Typography, TextField, Button,
  Card, CircularProgress, Alert, CardContent
} from '@mui/material';
import LockOutlinedIcon from '@mui/icons-material/LockOutlined';

/**
 * LoginPage component provides a login form for users to authenticate.
 * It uses the global AuthContext to manage login state.
 */
const LoginPage = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // Get the login function from our AuthContext
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  // Determine where to redirect after login
  const from = location.state?.from?.pathname || '/';

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError('');
    setLoading(true);

    try {
      const formData = new URLSearchParams();
      formData.append('username', email); // Must use 'username' for OAuth2
      formData.append('password', password);

      const response = await apiClient.post('/api/v1/auth/token', formData, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      });

      const accessToken = response.data.access_token;

      if (accessToken) {
        // Call the login function from context, which will handle localStorage
        login(accessToken);
        // Redirect the user to their intended page or the dashboard
        navigate(from, { replace: true });
      } else {
        setError('Failed to retrieve token. Please try again.');
      }
    } catch (err) {
      if (err.response) {
        console.error('Login failed:', err.response.data.detail);
        setError(err.response.data.detail || 'Invalid email or password.');
      } else if (err.request) {
        setError('No response from server. Check your connection or if the backend is running.');
      } else {
        setError('An unexpected error occurred. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    // Use Flexbox to center the login card on the page
    <Box
      display="flex"
      flexDirection="column"
      justifyContent="center"
      alignItems="center"
      minHeight="100vh"
      sx={{ bgcolor: 'grey.100' }}
    >
      <Container component="main" maxWidth="xs">
        <Card sx={{ p: 4, boxShadow: 5, borderRadius: 2 }}>
          <CardContent sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
            <Box sx={{ mb: 2 }}>
              <LockOutlinedIcon color="primary" sx={{ fontSize: 48 }} />
            </Box>
            <Typography component="h1" variant="h5" sx={{ mb: 3 }}>
              Sign In
            </Typography>

            {error && (
              <Alert severity="error" sx={{ mb: 2, width: '100%' }}>
                {error}
              </Alert>
            )}

            <Box component="form" onSubmit={handleSubmit} noValidate sx={{ width: '100%' }}>
              <TextField
                margin="normal"
                required
                fullWidth
                id="email"
                label="Email Address"
                name="email"
                autoComplete="email"
                autoFocus
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />

              <TextField
                margin="normal"
                required
                fullWidth
                name="password"
                label="Password"
                type="password"
                id="password"
                autoComplete="current-password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />

              <Button
                type="submit"
                fullWidth
                variant="contained"
                sx={{ mt: 3, mb: 2 }}
                disabled={loading}
              >
                {loading ? <CircularProgress size={24} color="inherit" /> : 'Sign In'}
              </Button>
            </Box>
          </CardContent>
        </Card>
      </Container>
    </Box>
  );
};

export default LoginPage;
