// src/routes/index.jsx

import { Routes, Route, Outlet, Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../features/auth/hooks/useAuth';

// Import the real components
import Layout from '../components/layout';
import LoginPage from '../features/auth/routes/LoginPage'; // The real login page
import DashboardPage from '../features/dashboard/routes/DashboardPage';
import ApiKeysPage from '../features/api-keys/routes/ApiKeysPage';

// Import only the necessary MUI components
import CircularProgress from '@mui/material/CircularProgress';
import Box from '@mui/material/Box';

/**
 * A component to guard routes that require authentication.
 * It renders the main Layout with nested pages if the user is authenticated.
 */
const PrivateRoute = () => {
  const { isAuthenticated } = useAuth();
  const location = useLocation();

  if (!isAuthenticated) {
    // Redirect unauthenticated users to the login page
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  // If authenticated, render the Layout which will contain the page via <Outlet />
  return (
    <Layout>
      <Outlet />
    </Layout>
  );
};

/**
 * The main router for the application.
 * It handles the loading state and directs users based on authentication status.
 */
export const AppRouter = () => {
  const { isLoading } = useAuth();

  // Show a global spinner while the initial authentication check is in progress
  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="100vh">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Routes>
      {/* ==================================================================== */}
      {/* THIS IS THE PUBLIC ROUTE FOR THE LOGIN PAGE, IT MUST BE PRESENT */}
      <Route path="/login" element={<LoginPage />} />
      {/* ==================================================================== */}

      {/* Group of protected routes */}
      <Route element={<PrivateRoute />}>
        <Route path="/" element={<DashboardPage />} />
        <Route path="/api-keys" element={<ApiKeysPage />} />
      </Route>

      {/* 
        A catch-all route.
        If a user navigates to a non-existent path, redirect them to the dashboard.
      */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
};