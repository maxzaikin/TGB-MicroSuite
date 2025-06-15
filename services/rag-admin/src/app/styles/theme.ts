// file: src/app/styles/theme.ts

import { createTheme } from '@mui/material/styles';

/**
 * MUI Theme configuration.
 * This is the central place to define the application's color palette,
 * typography, component overrides, etc.
 * @see https://mui.com/material-ui/customization/theming/
 */
export const theme = createTheme({
  palette: {
    mode: 'dark', // Starting with a dark mode theme as a baseline
    primary: {
      main: '#90caf9', // A nice light blue for dark mode
    },
    secondary: {
      main: '#f48fb1', // A soft pink
    },
    background: {
      default: '#121212',
      paper: '#1e1e1e',
    },
    text: {
      primary: '#ffffff',
      secondary: '#b0bec5',
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
    h4: {
      fontWeight: 700,
    },
    h5: {
      fontWeight: 700,
    },
  },
});