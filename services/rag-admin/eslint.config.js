// file: frontend/eslint.config.js

import globals from 'globals';
import tseslint from 'typescript-eslint';
import pluginReact from 'eslint-plugin-react';
import pluginReactHooks from 'eslint-plugin-react-hooks';
import pluginReactRefresh from 'eslint-plugin-react-refresh';
import eslintConfigPrettier from 'eslint-config-prettier';

/**
 * Modern ESLint configuration using the "flat config" format.
 * @see https://eslint.org/docs/latest/use/configure/configuration-files-new
 */
export default tseslint.config(
  // Global ignores
  {
    ignores: ['dist/'],
  },

  // Base configuration for all files
  tseslint.configs.base,

  // Recommended rules for JS/TS
  tseslint.configs.recommended,

  // Configuration for React files
  {
    files: ['**/*.{ts,tsx}'],
    ...pluginReact.configs.recommended,
    languageOptions: {
      ...pluginReact.configs.recommended.languageOptions,
      globals: {
        ...globals.browser,
      },
    },
    settings: {
      react: {
        version: 'detect', // Automatically detect React version
      },
    },
    plugins: {
      'react-hooks': pluginReactHooks,
      'react-refresh': pluginReactRefresh,
    },
    rules: {
      ...pluginReactHooks.configs.recommended.rules,
      'react-refresh/only-export-components': [
        'warn',
        { allowConstantExport: true },
      ],
      'react/react-in-jsx-scope': 'off', // Not needed with modern React/Vite
      '@typescript-eslint/no-explicit-any': 'warn',
    },
  },

  // Prettier config must be last to override styling rules
  eslintConfigPrettier,
);
