// file: src/features/auth/by-credentials/ui/LoginForm.tsx

import React, { useState } from 'react';
import {
  Box, Typography, TextField, Button,
  Card, CircularProgress, Alert, CardContent
} from '@mui/material';
import LockOutlinedIcon from '@mui/icons-material/LockOutlined';
import { useLogin } from '../api/useLogin';

export const LoginForm = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const { mutate: performLogin, isPending, isError, error } = useLogin();

  const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    performLogin({ email, password });
  };

  return (
    <Card sx={{ p: 4, boxShadow: 5, borderRadius: 2, maxWidth: 400, width: '100%' }}>
      <CardContent sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
        <LockOutlinedIcon color="primary" sx={{ fontSize: 48, mb: 2 }} />
        <Typography component="h1" variant="h5" sx={{ mb: 3 }}>
          Sign In
        </Typography>

        {isError && (
          <Alert severity="error" sx={{ mb: 2, width: '100%' }}>
            {/* Display a more specific error message from the mutation hook */}
            {(error as any)?.response?.data?.detail || 'Invalid email or password.'}
          </Alert>
        )}

        <Box component="form" onSubmit={handleSubmit} noValidate sx={{ width: '100%' }}>
          <TextField
            margin="normal" required fullWidth id="email"
            label="Email Address" name="email" autoComplete="email"
            autoFocus value={email} onChange={(e) => setEmail(e.target.value)}
          />

          <TextField
            margin="normal" required fullWidth name="password"
            label="Password" type="password" id="password"
            autoComplete="current-password" value={password} onChange={(e) => setPassword(e.target.value)}
          />

          <Button type="submit" fullWidth variant="contained" sx={{ mt: 3, mb: 2 }} disabled={isPending}>
            {isPending ? <CircularProgress size={24} color="inherit" /> : 'Sign In'}
          </Button>
        </Box>
      </CardContent>
    </Card>
  );
};