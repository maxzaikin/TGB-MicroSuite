// src/routes/index.jsx

import { Routes, Route, Outlet, Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../features/auth/hooks/useAuth';

// Import the real components
import Layout from '../components/layout/Layout';
import LoginPage from '../features/auth/routes/LoginPage';
import DashboardPage from '../features/dashboard/routes/DashboardPage';
import ApiKeysPage from '../features/api-keys/routes/ApiKeysPage';

// Import only the necessary MUI components
import CircularProgress from '@mui/material/CircularProgress';
import Box from '@mui/material/Box';

/**
 * A component to guard routes that require authentication.
 */
const PrivateRoute = () => {
  const { isAuthenticated } = useAuth();
  const location = useLocation();

  if (!isAuthenticated) {
    // Redirect unauthenticated users to the login page, saving their intended destination
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  // If authenticated, render the main app layout with the requested page
  return (
    <Layout>
      <Outlet />
    </Layout>
  );
};

/**
 * The main router for the application.
 */
export const AppRouter = () => {
  const { isAuthenticated, isLoading } = useAuth();

  // Show a global spinner during the initial authentication check
  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="100vh">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Routes>
      {/* 
        This route handles unauthenticated users. 
        If a logged-in user tries to visit /login, they are redirected to the dashboard.
      */}
      <Route
        path="/login"
        element={
          isAuthenticated ? <Navigate to="/" replace /> : <LoginPage />
        }
      />

      {/* 
        This is the main entry for authenticated users.
        The PrivateRoute component handles the protection logic.
      */}
      <Route element={<PrivateRoute />}>
        <Route path="/" element={<DashboardPage />} />
        <Route path="/api-keys" element={<ApiKeysPage />} />
      </Route>

      {/* 
        A catch-all route for any other path.
        It redirects to the main dashboard page.
      */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
};