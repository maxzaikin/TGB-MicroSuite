// file: src/shared/api/token.service.ts

// A single source of truth for the token key in local storage.
const AUTH_TOKEN_KEY = 'accessToken';

/**
 * A service for managing the authentication token in local storage.
 * Abstracting this logic allows for easier testing and future changes
 * (e.g., switching to session storage or a secure cookie).
 */
export const tokenService = {
  get: (): string | null => {
    return localStorage.getItem(AUTH_TOKEN_KEY);
  },

  set: (token: string): void => {
    localStorage.setItem(AUTH_TOKEN_KEY, token);
  },

  remove: (): void => {
    localStorage.removeItem(AUTH_TOKEN_KEY);
  },
};