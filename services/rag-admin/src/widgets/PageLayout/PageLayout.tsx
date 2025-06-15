// file: src/widgets/PageLayout/PageLayout.tsx

import React from 'react';
import { NavLink, Outlet } from 'react-router-dom';
import {
  AppBar,
  Toolbar,
  Typography,
  Button,
  Box,
  Container,
} from '@mui/material';
import { useAuth } from '@/features/auth/model/useAuth'; // We will create this hook soon

// Configuration for navigation links to keep them manageable.
const navItems = [
  { label: 'Home', path: '/' },
  { label: 'API Keys', path: '/api-keys' },
];

/**
 * A primary layout widget for authenticated pages.
 * It provides a consistent structure including a header, main content area, and a footer.
 * It consumes the AuthContext via the `useAuth` hook to handle the logout action.
 */
export const PageLayout = () => {
  // The layout component now fetches the logout function itself,
  // making it more decoupled and reusable without prop drilling.
  const { logout } = useAuth();

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      <AppBar position="static" elevation={1}>
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            TgramBuddy
          </Typography>

          {/* Navigation items are mapped from a config array for easy maintenance */}
          {navItems.map((item) => (
            <Button
              key={item.label}
              component={NavLink}
              to={item.path}
              // NavLink automatically handles the 'active' class,
              // but we can also style it based on the `isActive` prop.
              sx={(theme) => ({
                '&.active': {
                  backgroundColor: theme.palette.action.selected,
                  fontWeight: 'bold',
                },
                color: 'inherit',
                textTransform: 'none',
                fontSize: '1rem',
              })}
            >
              {item.label}
            </Button>
          ))}

          <Button
            color="inherit"
            onClick={logout}
            aria-label="Log out of your account"
          >
            Logout
          </Button>
        </Toolbar>
      </AppBar>

      <Container component="main" sx={{ py: 4, flexGrow: 1 }}>
        {/* Outlet renders the matched child route component */}
        <Outlet />
      </Container>

      <Box
        component="footer"
        sx={{
          py: 2,
          px: 2,
          mt: 'auto',
          backgroundColor: (theme) =>
            theme.palette.mode === 'light'
              ? theme.palette.grey[200]
              : theme.palette.grey[800],
        }}
      >
        <Typography variant="body2" color="text.secondary" align="center">
          © {new Date().getFullYear()} TgramBuddy
        </Typography>
      </Box>
    </Box>
  );
};

// No children prop needed, as we use <Outlet /> from react-router-dom v6+.