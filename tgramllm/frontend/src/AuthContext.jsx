// src/auth/AuthContext.jsx
import React, { createContext, useContext, useState, useEffect } from 'react';
import { jwtDecode } from 'jwt-decode';

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  const logout = () => {
    localStorage.removeItem('access_token');
    setIsAuthenticated(false);
  };

  const setupAutoLogout = () => {
    const token = localStorage.getItem('access_token');
    if (!token) return;

    try {
      const { exp } = jwtDecode(token);
      const timeLeft = exp * 1000 - Date.now();

      if (timeLeft <= 0) {
        logout();
      } else {
        console.log(`⏳ Auto-logout in ${Math.floor(timeLeft / 1000)} seconds`);
        setTimeout(logout, timeLeft);
      }
    } catch (error) {
      console.error('❌ JWT parse error:', error);
      logout();
    }
  };

  const login = () => {
    setIsAuthenticated(true);
    setupAutoLogout();
  };

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (token) {
      setIsAuthenticated(true);
      setupAutoLogout();
    }
  }, []);

  return (
    <AuthContext.Provider value={{ isAuthenticated, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};
