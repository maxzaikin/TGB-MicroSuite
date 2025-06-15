// file: frontend/vite.config.ts

import { defineConfig } from 'vitest/config'; // Import from 'vitest/config' for test config typing
import react from '@vitejs/plugin-react';
import svgr from 'vite-plugin-svgr';
import path from 'path';

export default defineConfig({
  plugins: [
    react(),
    // Allows importing SVGs as React components
    // e.g. import { ReactComponent as MyIcon } from './icon.svg'
    svgr(),
  ],
  resolve: {
    alias: {
      // Sets up the '@' alias to point to the 'src' directory.
      // This is crucial for clean, absolute imports across the project.
      '@': path.resolve(__dirname, './src'),
    },
  },
  // Vitest configuration
  test: {
    globals: true,
    environment: 'jsdom',
    // Path to the setup file for tests.
    // It runs before each test file.
    setupFiles: './setupTests.ts', // Points to the file in the root
    // Optional: add coverage configuration
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
    },
  },
});