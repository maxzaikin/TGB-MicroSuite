// file: src/entities/api-key/api/useCreateApiKey.ts

import { useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/shared/api/client';
import type { ApiKeyGenerated, NewApiKey } from '../model/types';
import { API_KEYS_QUERY_KEY } from './useApiKeys';

async function createApiKey(newKey: NewApiKey): Promise<ApiKeyGenerated> {
  const { data } = await apiClient.post<ApiKeyGenerated>('/api/v1/api-keys', newKey);
  return data;
}

export function useCreateApiKey() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: createApiKey,
    onSuccess: () => {
      // This is the key change. We are ensuring all queries starting with API_KEYS_QUERY_KEY are invalidated.
      // invalidateQueries by default only refetches active queries.
      // If we want to guarantee a refetch, we can manually trigger it.
      // However, a simple invalidation should be enough. Let's ensure the key is correct.
      queryClient.invalidateQueries({ queryKey: [API_KEYS_QUERY_KEY] });
    },
  });
}