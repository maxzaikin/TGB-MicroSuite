// file: src/app/router/route-guards.tsx

import React from 'react';
import { Navigate, useLocation, Outlet } from 'react-router-dom';
import { Box, CircularProgress } from '@mui/material';
import { useAuth } from '@/features/auth/model/useAuth';
import { PageLayout } from '@/widgets/PageLayout/PageLayout';

/**
 * Guards routes that require authentication.
 * While loading, it displays a spinner.
 * If the user is not authenticated, it redirects to the /login page.
 * If authenticated, it renders the main PageLayout, which contains the <Outlet /> for the child routes.
 */
export const AuthGuard: React.FC = () => {
  const { isAuthenticated, isLoading } = useAuth();
  const location = useLocation();

  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="100vh">
        <CircularProgress />
      </Box>
    );
  }

  if (!isAuthenticated) {
    // Redirect unauthenticated users, preserving the intended destination.
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  // User is authenticated, render the standard page layout.
  return <PageLayout />;
};

/**
 * Guards the /login route.
 * If the user is already authenticated, they are redirected to the main dashboard.
 * Otherwise, it renders the child component (the login page).
 */
export const GuestGuard: React.FC = () => {
    const { isAuthenticated, isLoading } = useAuth();

    if (isLoading) {
        // Render nothing or a spinner during the initial check
        return null;
    }

    if (isAuthenticated) {
        return <Navigate to="/" replace />;
    }

    // Render the login page
    return <Outlet />;
};