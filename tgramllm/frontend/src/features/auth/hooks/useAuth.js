// src/features/auth/hooks/useAuth.js

import { useContext } from 'react';
// 👈 ПРАВИЛЬНЫЙ ПУТЬ к вашему контексту
import { AuthContext } from '../context/AuthContext';

export const useAuth = () => {
  const context = useContext(AuthContext);

  if (context === undefined) { // Лучше проверять на undefined
    throw new Error('useAuth must be used within an AuthProvider');
  }

  return {
    ...context,
    // Вычисляемое свойство для удобства
    isAuthenticated: !!context.user, // true, если user не null
  };
};