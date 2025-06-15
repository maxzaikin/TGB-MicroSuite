// file: src/features/auth/by-credentials/api/useLogin.ts

import { useMutation } from '@tanstack/react-query';
import { useNavigate, useLocation } from 'react-router-dom';
import { apiClient } from '@/shared/api/client';
import { useAuth } from '@/features/auth/model/useAuth';
import type { LoginCredentials } from '@/features/auth/by-credentials/model/types';

interface AuthResponse {
  access_token: string;
  token_type: string;
}

async function loginWithCredentials(credentials: LoginCredentials): Promise<string> {
  const formData = new URLSearchParams();
  formData.append('username', credentials.email);
  formData.append('password', credentials.password);

  const { data } = await apiClient.post<AuthResponse>('/api/v1/auth/token', formData, {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  });

  return data.access_token;
}

export function useLogin() {
  const { login: setAuthToken } = useAuth(); // Получаем метод для сохранения токена из контекста
  const navigate = useNavigate();
  const location = useLocation();
  const from = location.state?.from?.pathname || '/';

  return useMutation({
    mutationFn: loginWithCredentials,
    onSuccess: (accessToken) => {
      // On successful API call, save the token and redirect
      setAuthToken(accessToken);
      navigate(from, { replace: true });
    },
    // onError is handled automatically by useMutation, we can access error state in the component
  });
}