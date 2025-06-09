// src/features/auth/context/AuthProvider.jsx

import React, { useState, useEffect, useCallback } from 'react';
import { jwtDecode } from 'jwt-decode';
import { AuthContext } from './auth-context'; // Import the context "wire"

export const AuthProvider = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  // Memoize logout function for stability
  const logout = useCallback(() => {
    localStorage.removeItem('access_token');
    setIsAuthenticated(false);
  }, []);

  // Memoize the core authentication logic to prevent re-creation on every render
  const checkAuthStatus = useCallback(() => {
    const token = localStorage.getItem('access_token');
    if (!token) {
      setIsAuthenticated(false);
      return; // Exit if no token is found
    }

    try {
      const { exp } = jwtDecode(token);
      const timeLeft = exp * 1000 - Date.now();

      if (timeLeft > 0) {
        setIsAuthenticated(true);
        console.log(`⏳ Auto-logout in ${Math.floor(timeLeft / 1000)} seconds`);
        const timer = setTimeout(logout, timeLeft);
        // Return a cleanup function for the timer
        return () => clearTimeout(timer);
      } else {
        // Token has expired, log out
        logout();
      }
    } catch (error) {
      console.error('❌ JWT parse error:', error);
      logout(); // Log out if token is invalid
    }
  }, [logout]); // This function only depends on the stable `logout` function

  // Login handler
  const login = (token) => {
    localStorage.setItem('access_token', token);
    checkAuthStatus(); // Run the auth check to set timers and state
  };

  // Effect to check authentication status on initial app load
  useEffect(() => {
    const cleanup = checkAuthStatus();
    setIsLoading(false); // Initial check is complete

    // This will be called if the AuthProvider is ever unmounted
    return cleanup;
  }, [checkAuthStatus]); // Run only when the stable checkAuthStatus function is created

  // The value provided to all consuming components
  const value = { isAuthenticated, isLoading, login, logout };

  return (
    <AuthContext.Provider value={value}>
      {/* Don't render children until the initial auth check is done */}
      {!isLoading && children}
    </AuthContext.Provider>
  );
};