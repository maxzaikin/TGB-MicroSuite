// file: src/entities/api-key/api/useApiKeys.ts

import { useQuery } from '@tanstack/react-query';
import { type SortingState, type PaginationState, type ColumnFiltersState } from '@tanstack/react-table';
import { apiClient } from '@/shared/api/client';
import type { PaginatedApiResponse } from '../model/types';

interface UseApiKeysProps {
  pagination: PaginationState;
  sorting: SortingState;
  columnFilters: ColumnFiltersState;
}

export const API_KEYS_QUERY_KEY = 'apiKeys';

async function fetchApiKeys({ pagination, sorting, columnFilters }: UseApiKeysProps): Promise<PaginatedApiResponse> {
  const params = new URLSearchParams();
  params.append('page', `${pagination.pageIndex + 1}`);
  params.append('size', `${pagination.pageSize}`);

  if (sorting.length > 0) {
    params.append('sort_by', sorting[0].id);
    params.append('sort_order', sorting[0].desc ? 'desc' : 'asc');
  }
  
  // Add per-column filters to the request
  columnFilters.forEach(filter => {
    if (filter.value) {
      params.append(filter.id, String(filter.value));
    }
  });

  const { data } = await apiClient.get<PaginatedApiResponse>('/api/v1/api-keys', { params });
  return data;
}

export function useApiKeys(tableState: UseApiKeysProps) {
  return useQuery({
    queryKey: [API_KEYS_QUERY_KEY, tableState],
    queryFn: () => fetchApiKeys(tableState),
    keepPreviousData: true,
  });
}