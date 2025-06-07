// src/App.jsx
import * as React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import LoginPage from './LoginPage';
import DashboardPage from './DashboardPage';
import ApiKeysPage from './ApiKeysPage';
import Layout from './Layout';
import { AuthProvider } from './auth/AuthContext';
import PrivateRoute from './auth/PrivateRoute';
import { useAuth } from './auth/useAuth';

const AppRoutes = () => {
  const { isAuthenticated, login } = useAuth();

  return isAuthenticated ? (
    <Layout>
      <Routes>
        <Route path="/" element={<PrivateRoute element={<DashboardPage />} />} />
        <Route path="/api-keys" element={<PrivateRoute element={<ApiKeysPage />} />} />
        <Route path="*" element={<PrivateRoute element={<DashboardPage />} />} />
      </Routes>
    </Layout>
  ) : (
    <Routes>
      <Route path="*" element={<LoginPage onLoginSuccess={login} />} />
    </Routes>
  );
};

const App = () => (
  <AuthProvider>
    <Router>
      <AppRoutes />
    </Router>
  </AuthProvider>
);

export default App;
