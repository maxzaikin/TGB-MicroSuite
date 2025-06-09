// src/features/auth/hooks/useAuth.js

import { useContext } from 'react';
import { AuthContext } from '../context/auth-context'; // Import the same context "wire"

/**
 * Custom hook to consume the AuthContext.
 * It provides a simple way to access auth state and functions.
 */
export const useAuth = () => {
  const context = useContext(AuthContext);

  // This check ensures the hook is used within the <AuthProvider> tree.
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }

  return context;
};