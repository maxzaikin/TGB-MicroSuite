// file: src/app/router/index.tsx

import { Routes, Route, Navigate } from 'react-router-dom';
import { AuthGuard, GuestGuard } from './route-guards';
import { LoginPage } from '@/pages/LoginPage';
import { DashboardPage } from '@/pages/DashboardPage';
import { ApiKeysPage } from '@/pages/ApiKeysPage';
import { NotFoundPage } from '@/pages/NotFoundPage'; // A dedicated 404 page is good practice

/**
 * The main router configuration for the application.
 * It defines all routes and applies the necessary guards.
 */
export const AppRouter = () => {
  return (
    <Routes>
      {/* Routes for unauthenticated users */}
      <Route element={<GuestGuard />}>
        <Route path="/login" element={<LoginPage />} />
      </Route>

      {/* Protected routes for authenticated users */}
      <Route element={<AuthGuard />}>
        <Route path="/" element={<DashboardPage />} />
        <Route path="/api-keys" element={<ApiKeysPage />} />
      </Route>

      {/* Fallback routes */}
      <Route path="/404" element={<NotFoundPage />} />
      <Route path="*" element={<Navigate to="/404" replace />} />
    </Routes>
  );
};