// src/features/auth/context/auth-context.js

import { createContext } from 'react';

/**
 * This context object is the "wire" that connects the provider (which supplies the value)
 * and the consumer hooks (which use the value).
 * The initial value is `null` as it will be immediately replaced by the provider's value.
 */
export const AuthContext = createContext(null);