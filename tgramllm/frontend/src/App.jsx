// src/App.jsx
import * as React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import LoginPage from './LoginPage';
import DashboardPage from './DashboardPage';
import ApiKeysPage from './ApiKeysPage';
import Layout from './Layout';
import { AuthProvider } from './AuthContext';
import PrivateRoute from './PrivateRoute';
import { useAuth } from './useAuth' ;

const AppRoutes = () => {
  const { isAuthenticated, login } = useAuth();

  console.log("Auth?", isAuthenticated);

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
      <Route path="/" element={<LoginPage onLoginSuccess={login} />} />
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
