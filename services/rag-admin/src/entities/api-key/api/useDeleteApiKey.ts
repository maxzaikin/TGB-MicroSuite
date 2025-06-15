// file: src/entities/api-key/api/useDeleteApiKey.ts

import { useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/shared/api/client';
import { API_KEYS_QUERY_KEY } from './useApiKeys';

// The mutation function that sends the DELETE request.
async function deleteApiKey(id: number): Promise<void> {
  await apiClient.delete(`/api/v1/api-keys/${id}`);
}

/**
 * A hook for deleting an API key.
 * It handles the API mutation and invalidates the cache on success.
 */
export function useDeleteApiKey() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: deleteApiKey,
    // Use onSettled here as well for consistency and robustness.
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: [API_KEYS_QUERY_KEY] });
    },
  });
}