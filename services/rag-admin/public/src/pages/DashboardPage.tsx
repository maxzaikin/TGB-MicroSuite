// file: src/pages/DashboardPage.tsx

import React from 'react';
import { Box, Typography, Container, Paper } from '@mui/material';

/**
 * The main dashboard page, serving as the home screen for authenticated users.
 * Its primary role is to display high-level information and widgets.
 */
export const DashboardPage: React.FC = () => {
  return (
    <Container component="main" maxWidth="lg">
      <Paper
        sx={{
          p: 4,
          mt: 4,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          gap: 2, // Use gap for spacing between elements
        }}
        elevation={2}
      >
        <Typography variant="h4" component="h1">
          Welcome to TGramBuddy Dashboard
        </Typography>

        <Typography variant="body1" color="text.secondary">
          High-level widgets and application statistics will be displayed here soon.
        </Typography>

        {/* 
          The logout functionality has been moved to the main PageLayout widget
          for global access, making this button redundant.
          If a page-specific action is needed, it can be added here.
        */}
      </Paper>
    </Container>
  );
};