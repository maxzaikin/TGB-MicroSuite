// file: src/pages/ApiKeysPage.tsx

import React, { useState } from 'react';
import { Box, Typography, Alert, TextField, InputAdornment } from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import { type SortingState, type PaginationState, type ColumnFiltersState } from '@tanstack/react-table';

import { useApiKeys } from '@/entities/api-key';
import { ApiKeysTable } from '@/widgets/ApiKeysTable';
import { CreateApiKeyButton } from '@/features/api-key-management/create-key';
import { useDebounce } from '@/shared/hooks';

export const ApiKeysPage: React.FC = () => {
  // --- State for Server-Side Operations ---
  const [sorting, setSorting] = useState<SortingState>([]);
  const [pagination, setPagination] = useState<PaginationState>({ pageIndex: 0, pageSize: 10 });
  const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>([]);
  
  // Debounce the column filters to avoid excessive API calls
  const debouncedColumnFilters = useDebounce(columnFilters, 500);

  // --- State for Client-Side Filtering ---
  const [globalFilter, setGlobalFilter] = useState('');

  const { data, isLoading, isError, error, isFetching } = useApiKeys({
    pagination,
    sorting,
    columnFilters: debouncedColumnFilters,
  });

  return (
    <Box sx={{ p: 3, display: 'flex', flexDirection: 'column', gap: 2 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="h5">API Key Management</Typography>
        <CreateApiKeyButton />
      </Box>

      {/* This is the INSTANT, CLIENT-SIDE search bar */}
      <TextField
        value={globalFilter}
        onChange={(e) => setGlobalFilter(e.target.value)}
        placeholder="Instant search on current page..."
        variant="outlined"
        size="small"
        InputProps={{
          startAdornment: <InputAdornment position="start"><SearchIcon /></InputAdornment>,
        }}
      />

      {isError && (
        <Alert severity="error">{(error as any)?.message || 'Failed to load API keys.'}</Alert>
      )}

      <ApiKeysTable
        data={data?.items || []}
        // Show loading indicator on initial load OR when refetching in the background
        isLoading={isLoading || isFetching}
        pageCount={data?.total ? Math.ceil(data.total / data.size) : 0}
        pagination={pagination}
        setPagination={setPagination}
        sorting={sorting}
        setSorting={setSorting}
        columnFilters={columnFilters}
        setColumnFilters={setColumnFilters}
        globalFilter={globalFilter}
      />
    </Box>
  );
};