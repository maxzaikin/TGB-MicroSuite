// file: src/shared/api/client.ts

import axios, { type AxiosInstance } from 'axios';
import { tokenService } from './token.service';

/**
 * The base URL for the API. It's sourced from environment variables.
 * Vite exposes env variables on the `import.meta.env` object.
 * A fallback to a local development URL is provided.
 * @see https://vitejs.dev/guide/env-and-mode.html
 */
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// --- Interceptors ---

// 1. Request Interceptor: Injects the auth token into requests.
apiClient.interceptors.request.use(
  (config) => {
    const token = tokenService.get();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error),
);

// 2. Response Interceptor: Handles global errors, like 401 Unauthorized.
apiClient.interceptors.response.use(
  (response) => response, // Pass through successful responses
  (error) => {
    // Check if the error is a 401 Unauthorized response
    if (error.response?.status === 401) {
      // The token is invalid or expired.
      // 1. Remove the invalid token from storage.
      tokenService.remove();
      // 2. Redirect the user to the login page.
      // Using `window.location.assign` forces a full page reload,
      // which clears all component state and is the safest way to handle a full logout.
      window.location.assign('/login');
    }

    // For all other errors, just pass them along.
    return Promise.reject(error);
  },
);