// file: src/app/providers/index.tsx

import React from 'react';
import { BrowserRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { CssBaseline, ThemeProvider } from '@mui/material';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { theme } from '@/app/styles/theme';
import { AuthProvider } from './AuthProvider'; // AuthProvider будет жить здесь же

/**
 * Creates a QueryClient instance with default options.
 * - staleTime: Data is considered fresh for 5 minutes, preventing unnecessary refetches.
 * - cacheTime: Data is kept in the cache for 15 minutes after a component unmounts.
 */
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5,
      refetchOnWindowFocus: false,
    },
  },
});

/**
 * A Higher-Order Component (HOC) that composes all application-wide providers.
 * This approach avoids the "Pyramid of Doom" in the main App component and centralizes provider configuration.
 *
 * @param component The root component of the application to be wrapped.
 * @returns A new component wrapped with all necessary providers.
 */
export const withProviders = (component: () => React.ReactNode) => () => (
  // BrowserRouter should be at the top level to provide routing context.
  <BrowserRouter>
    <QueryClientProvider client={queryClient}>
      <ThemeProvider theme={theme}>
        {/* CssBaseline provides a consistent baseline of styles across browsers. */}
        <CssBaseline />
        <AuthProvider>
          {component()}
        </AuthProvider>
      </ThemeProvider>
      {/* ReactQueryDevtools are invaluable for debugging server state and only included in development builds.. */}
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  </BrowserRouter>
);