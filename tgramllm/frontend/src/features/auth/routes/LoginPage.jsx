import React, { useState } from 'react';
import {
  Container,
  Box,
  Typography,
  TextField,
  Button,
  Card,
  CircularProgress,
  Alert,
  CardContent,
} from '@mui/material';
import LockOutlinedIcon from '@mui/icons-material/LockOutlined';
import EmailOutlinedIcon from '@mui/icons-material/EmailOutlined';
import VpnKeyOutlinedIcon from '@mui/icons-material/VpnKeyOutlined';

import apiClient from '../../../services/apiClient';

/**
 * LoginPage component provides a login form for users to authenticate.
 *
 * @param {Function} onLoginSuccess - Callback triggered when login is successful.
 */
const LoginPage = ({ onLoginSuccess }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError('');
    setLoading(true);

    try {
      const formData = new URLSearchParams();
      formData.append('username', email); // Must use 'username' for OAuth2
      formData.append('password', password);

      const response = await apiClient.post('/api/v1/auth/token', formData, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      });

      const accessToken = response.data.access_token;

      if (accessToken) {
        localStorage.setItem('access_token', accessToken);
        onLoginSuccess();
      } else {
        setError('Failed to retrieve token. Please try again.');
      }
    } catch (err) {
      if (err.response) {
        console.error('Login failed:', err.response.data.detail);
        setError(err.response.data.detail || 'Invalid email or password.');
      } else if (err.request) {
        setError('No response from server. Please check your connection or start the backend.');
      } else {
        setError('An unexpected error occurred. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box
      sx={{
        position: 'fixed',
        top: '20px',
        left: '50%',
        transform: 'translateX(-50%)',
        width: '100%',
        maxWidth: 480,
        p: 2,
        boxSizing: 'border-box',
        overflowY: 'auto',
        maxHeight: 'calc(100vh - 40px)',
      }}
    >
      <Container component="main" maxWidth="xs">
        <Card sx={{ p: 4, boxShadow: 3, borderRadius: 2 }}>
          <CardContent
            sx={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
            }}
          >
            <Box sx={{ mb: 2 }}>
              <LockOutlinedIcon color="primary" sx={{ fontSize: 48 }} />
            </Box>
            <Typography component="h1" variant="h5" sx={{ mb: 3 }}>
              Sign In
            </Typography>

            <Box
              component="form"
              onSubmit={handleSubmit}
              noValidate
              sx={{ width: '100%' }}
            >
              {error && (
                <Alert severity="error" sx={{ mb: 2 }}>
                  {error}
                </Alert>
              )}

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
                InputProps={{
                  startAdornment: (
                    <EmailOutlinedIcon sx={{ mr: 1, color: 'action.active' }} />
                  ),
                }}
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
                InputProps={{
                  startAdornment: (
                    <VpnKeyOutlinedIcon sx={{ mr: 1, color: 'action.active' }} />
                  ),
                }}
              />

              <Button
                type="submit"
                fullWidth
                variant="contained"
                sx={{ mt: 3, mb: 2 }}
                disabled={loading}
              >
                {loading ? (
                  <CircularProgress size={24} color="inherit" />
                ) : (
                  'Sign In'
                )}
              </Button>
            </Box>
          </CardContent>
        </Card>

        <Typography
          variant="body2"
          color="text.secondary"
          align="center"
          sx={{ mt: 5 }}
        >
          {'© '}
          {new Date().getFullYear()} My Company. All rights reserved.
        </Typography>
      </Container>
    </Box>
  );
};

export default LoginPage;
