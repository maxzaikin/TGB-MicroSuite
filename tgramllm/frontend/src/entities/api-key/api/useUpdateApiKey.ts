// file: src/entities/api-key/api/useUpdateApiKey.ts

import { useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/shared/api/client';
import type { ApiKey, ApiKeyUpdate, PaginatedApiResponse } from '../model/types';
import { API_KEYS_QUERY_KEY } from './useApiKeys';

async function updateApiKey({ id, payload }: { id: number; payload: ApiKeyUpdate }): Promise<ApiKey> {
  const { data } = await apiClient.patch<ApiKey>(`/api/v1/api-keys/${id}`, payload);
  return data;
}

export function useUpdateApiKey() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: updateApiKey,
    // --- Optimistic Update Logic ---
    onMutate: async (updatedKey) => {
      // 1. Cancel any outgoing refetches so they don't overwrite our optimistic update
      await queryClient.cancelQueries({ queryKey: [API_KEYS_QUERY_KEY] });

      // 2. Snapshot the previous value
      const previousApiKeys = queryClient.getQueryData<PaginatedApiResponse>([API_KEYS_QUERY_KEY]);

      // 3. Optimistically update to the new value
      if (previousApiKeys) {
        queryClient.setQueryData<PaginatedApiResponse>([API_KEYS_QUERY_KEY], {
          ...previousApiKeys,
          items: previousApiKeys.items.map(key => 
            key.id === updatedKey.id ? { ...key, ...updatedKey.payload } : key
          ),
        });
      }
      
      // 4. Return a context object with the snapshotted value
      return { previousApiKeys };
    },
    // If the mutation fails, use the context returned from onMutate to roll back
    onError: (err, newTodo, context) => {
      if (context?.previousApiKeys) {
        queryClient.setQueryData([API_KEYS_QUERY_KEY], context.previousApiKeys);
      }
    },
    // Always refetch after error or success, to ensure data consistency
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: [API_KEYS_QUERY_KEY] });
    },
  });
}