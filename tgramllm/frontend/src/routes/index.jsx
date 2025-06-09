// src/routes/index.jsx - НОВАЯ ВЕРСИЯ
import { Routes, Route, Outlet, Navigate } from 'react-router-dom';
import { useAuth } from '../features/auth/hooks/useAuth';

// Импортируем компоненты с правильными путями
import Layout from '../components/layout'; // Обратите внимание на чистый импорт
import LoginPage from '../features/auth/routes/LoginPage';
import DashboardPage from '../features/dashboard/routes/DashboardPage';
import ApiKeysPage from '../features/api-keys/routes/ApiKeysPage';
import PrivateRoute from './PrivateRoute';

/**
 * Этот компонент группирует защищенные роуты.
 * Он сначала проверяет аутентификацию, затем оборачивает
 * дочерние страницы (которые рендерятся через <Outlet />) в Layout.
 */
const ProtectedLayout = () => {
  // Вместо PrivateRoute на каждом роуте, можно использовать одну проверку здесь,
  // но для наглядности оставим ваш PrivateRoute как обертку.
  return (
    <PrivateRoute>
      <Layout>
        <Outlet />
      </Layout>
    </PrivateRoute>
  );
};

export const AppRouter = () => {
  const { isAuthenticated } = useAuth();

  return (
    <Routes>
      {/* Если пользователь НЕ аутентифицирован, все защищенные роуты будут недоступны,
          и он будет перенаправлен на /login при попытке доступа. */}

      {/* Публичные роуты */}
      {!isAuthenticated && (
        <Route path="/login" element={<LoginPage />} />
      )}

      {/* Защищенные роуты */}
      <Route element={<ProtectedLayout />}>
        <Route path="/" element={<DashboardPage />} />
        <Route path="/api-keys" element={<ApiKeysPage />} />
      </Route>

      {/*
        "Catch-all" роут: Перенаправляет на нужную страницу в зависимости от статуса логина.
        Это элегантнее, чем дублировать path="*".
      */}
      <Route
        path="*"
        element={<Navigate to={isAuthenticated ? '/' : '/login'} />}
      />
    </Routes>
  );
};