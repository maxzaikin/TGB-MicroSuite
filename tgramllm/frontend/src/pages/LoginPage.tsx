// file: src/pages/LoginPage.tsx

import { Box } from '@mui/material';
import { LoginForm } from '@/features/auth/by-credentials'; // Importing the feature component

/**
 * The login page.
 * Its sole responsibility is to provide the page layout and render the LoginForm feature.
 */
export const LoginPage = () => {
  return (
    <Box
      display="flex"
      justifyContent="center"
      alignItems="center"
      minHeight="100vh"
    >
      <LoginForm />
    </Box>
  );
};