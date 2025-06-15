// file: src/features/auth/model/useAuth.ts

import { useContext } from 'react';
// Импортируем сам контекст из слоя app, где он был создан
import { AuthContext } from '@/app/providers/AuthProvider';

/**
 * A custom hook to consume the AuthContext.
 * It provides a clean and safe way to access authentication state and methods.
 * This is the public API for our 'auth' feature.
 *
 * @returns The authentication context value.
 * @throws {Error} If the hook is used outside of an AuthProvider tree.
 */
export const useAuth = () => {
  const context = useContext(AuthContext);

  if (!context) {
    throw new Error('useAuth must be used within the AuthProvider tree');
  }

  return context;
};