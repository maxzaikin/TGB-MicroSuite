import React from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  Button,
  Box,
  Container,
  CssBaseline,
} from '@mui/material';
import { Link } from 'react-router-dom';

/**
 * Layout component provides a consistent page structure
 * including a navigation bar, content area, and footer.
 */
const Layout = ({ children, onLogout }) => {
  return (
    <Box display="flex" flexDirection="column" minHeight="100vh">
      <CssBaseline />

      <AppBar position="static" elevation={2}>
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            Admin Dashboard
          </Typography>

          <Button
            color="inherit"
            component={Link}
            to="/"
            aria-label="Go to dashboard home"
          >
            Home
          </Button>
          <Button
            color="inherit"
            component={Link}
            to="/api-keys"
            aria-label="Manage API keys"
          >
            API Keys
          </Button>
          <Button
            color="inherit"
            onClick={onLogout}
            aria-label="Log out of your account"
          >
            Logout
          </Button>
        </Toolbar>
      </AppBar>

      <Container component="main" sx={{ mt: 4, flexGrow: 1 }}>
        {children}
      </Container>

      <Box
        component="footer"
        sx={{
          p: 2,
          mt: 'auto',
          bgcolor: 'grey.100',
          textAlign: 'center',
        }}
      >
        <Typography variant="body2" color="text.secondary">
          © {new Date().getFullYear()} TGramBuddy OpenSource (c)All rights belongs to all.
        </Typography>
      </Box>
    </Box>
  );
};

export default Layout;
