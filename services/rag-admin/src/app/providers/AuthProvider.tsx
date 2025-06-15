// file: src/app/providers/AuthProvider.tsx

import React, {
  createContext,
  useState,
  useEffect,
  useCallback,
  useMemo,
} from 'react';
import { jwtDecode, JwtPayload } from 'jwt-decode';

// --- Constants ---
const AUTH_TOKEN_KEY = 'accessToken';

// --- Type Definitions ---
interface AuthContextType {
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (token: string) => void;
  logout: () => void;
}

// Custom JWT payload type if you have additional fields
interface CustomJwtPayload extends JwtPayload {
  // Add any custom claims from your token, e.g., roles
  // roles: string[];
}

// --- Context Definition ---
// Context is created and exported from the same file, avoiding a separate `auth-context.ts`.
// The initial context value is null and will be checked by the consumer hook.
export const AuthContext = createContext<AuthContextType | null>(null);

// --- Token Service (Abstraction) ---
// A simple abstraction over localStorage for better testability and maintainability.
const tokenService = {
  getToken: (): string | null => localStorage.getItem(AUTH_TOKEN_KEY),
  setToken: (token: string): void => localStorage.setItem(AUTH_TOKEN_KEY, token),
  removeToken: (): void => localStorage.removeItem(AUTH_TOKEN_KEY),
};

// --- AuthProvider Component ---
export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  const [token, setToken] = useState<string | null>(tokenService.getToken());
  const [isLoading, setIsLoading] = useState<boolean>(true);

  // Memoized logout function. It's stable and can be used in dependencies without causing re-renders.
  const logout = useCallback(() => {
    tokenService.removeToken();
    setToken(null);
  }, []);

  // Login handler
  const login = useCallback((newToken: string) => {
    tokenService.setToken(newToken);
    setToken(newToken);
  }, []);

  // Effect to handle token expiration and initial loading state
  useEffect(() => {
    setIsLoading(true);

    const currentToken = tokenService.getToken();
    if (!currentToken) {
      setToken(null);
      setIsLoading(false);
      return;
    }

    try {
      const { exp } = jwtDecode<CustomJwtPayload>(currentToken);
      const expirationTime = (exp ?? 0) * 1000;
      const timeLeft = expirationTime - Date.now();

      if (timeLeft > 0) {
        setToken(currentToken);
        // Set a timer to automatically log out when the token expires.
        const timerId = setTimeout(logout, timeLeft);
        // Cleanup function to clear the timer if the component unmounts or token changes.
        return () => clearTimeout(timerId);
      } else {
        // Token has already expired
        logout();
      }
    } catch (error) {
      console.error('Invalid token found:', error);
      logout();
    } finally {
      setIsLoading(false);
    }
  }, [token, logout]); // This effect re-runs if the token changes or the stable logout function is referenced.


  // The context value is memoized to prevent re-renders in consumers
  // when the provider itself re-renders for other reasons.
  const contextValue = useMemo(
    () => ({
      isAuthenticated: !!token,
      isLoading,
      login,
      logout,
    }),
    [token, isLoading, login, logout],
  );

  return (
    <AuthContext.Provider value={contextValue}>{children}</AuthContext.Provider>
  );
};
