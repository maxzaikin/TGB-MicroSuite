// file: src/widgets/ApiKeysTable/ApiKeysTable.tsx

import React, { useState, useMemo } from 'react';
import {
  useReactTable, getCoreRowModel, getFilteredRowModel, getPaginationRowModel, getSortedRowModel,
  flexRender, createColumnHelper, type Column, type PaginationState, type SortingState, type ColumnFiltersState
} from '@tanstack/react-table';
import {
  Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper,
  Switch, Typography, Box, TextField, IconButton, Menu, MenuItem,
  Tooltip, Dialog, DialogActions, DialogContent, DialogContentText, DialogTitle,
  Button, TablePagination, CircularProgress, LinearProgress, InputAdornment, // Added InputAdornment
} from '@mui/material';
// Icons
import ArrowUpwardIcon from '@mui/icons-material/ArrowUpward';
import ArrowDownwardIcon from '@mui/icons-material/ArrowDownward';
import MoreVertIcon from '@mui/icons-material/MoreVert';
import SaveIcon from '@mui/icons-material/Save';
import CancelIcon from '@mui/icons-material/Cancel';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import VpnKeyIcon from '@mui/icons-material/VpnKey';
import FingerprintIcon from '@mui/icons-material/Fingerprint';
import CommentIcon from '@mui/icons-material/Comment';
import TitleIcon from '@mui/icons-material/Title';
import ToggleOnIcon from '@mui/icons-material/ToggleOn';
import ClearIcon from '@mui/icons-material/Clear'; // The new icon for clearing filters

import { type ApiKey, type ApiKeyUpdate, useUpdateApiKey, useDeleteApiKey } from '@/entities/api-key';
import { TableSkeleton } from './TableSkeleton';

// --- Props Interface ---
interface ApiKeysTableProps {
  data: ApiKey[];
  isLoading: boolean;
  isFetching: boolean;
  pageCount: number;
  pagination: PaginationState;
  setPagination: (updater: React.SetStateAction<PaginationState>) => void;
  sorting: SortingState;
  setSorting: (updater: React.SetStateAction<SortingState>) => void;
  columnFilters: ColumnFiltersState;
  setColumnFilters: (updater: React.SetStateAction<ColumnFiltersState>) => void;
  globalFilter: string;
}

// --- Reusable Filter Component with Clear Button ---
function Filter({ column }: { column: Column<any, unknown> }) {
  const columnFilterValue = column.getFilterValue() as string;

  return (
    <TextField
      fullWidth
      variant="standard"
      size="small"
      placeholder={`Filter...`}
      value={columnFilterValue ?? ''}
      onChange={e => column.setFilterValue(e.target.value)}
      onClick={e => e.stopPropagation()} // Prevent sorting when clicking the filter input
      // Add the clear button as an end adornment
      InputProps={{
        endAdornment: (
          <InputAdornment position="end">
            {/* The button is only visible if there is a value in the filter */}
            {columnFilterValue && (
              <IconButton
                size="small"
                onClick={() => column.setFilterValue('')} // Clear the filter value on click
                aria-label="clear filter"
              >
                <ClearIcon fontSize="inherit" />
              </IconButton>
            )}
          </InputAdornment>
        ),
      }}
    />
  );
}

/**
 * A highly interactive and user-friendly widget for managing API keys.
 */
export const ApiKeysTable: React.FC<ApiKeysTableProps> = ({
  data, isLoading, isFetching, pageCount, pagination, setPagination, sorting, setSorting, columnFilters, setColumnFilters, globalFilter
}) => {
  // --- Local UI State ---
  const [editingRowId, setEditingRowId] = useState<number | null>(null);
  const [editedRowData, setEditedRowData] = useState<ApiKeyUpdate | null>(null);
  const [deleteConfirm, setDeleteConfirm] = useState<{ isOpen: boolean; keyId: number | null }>({ isOpen: false, keyId: null });

  // --- API Hooks ---
  const { mutate: updateKey, isPending: isUpdating } = useUpdateApiKey();
  const { mutate: deleteKey, isPending: isDeleting } = useDeleteApiKey();
  
  // --- Memoized Handlers ---
  const handleEditStart = React.useCallback((row: ApiKey) => { setEditingRowId(row.id); setEditedRowData({ name: row.name, comment: row.comment, is_active: row.is_active }); }, []);
  const handleEditCancel = React.useCallback(() => { setEditingRowId(null); setEditedRowData(null); }, []);
  const handleEditSave = React.useCallback(() => { if (!editingRowId || !editedRowData) return; updateKey({ id: editingRowId, payload: editedRowData }, { onSuccess: handleEditCancel }); }, [editingRowId, editedRowData, updateKey, handleEditCancel]);
  const handleFieldChange = React.useCallback((field: keyof ApiKeyUpdate, value: any) => { setEditedRowData(prev => (prev ? { ...prev, [field]: value } : null)); }, []);
  const openDeleteConfirm = React.useCallback((keyId: number) => setDeleteConfirm({ isOpen: true, keyId }), []);
  const closeDeleteConfirm = React.useCallback(() => setDeleteConfirm({ isOpen: false, keyId: null }), []);
  const handleDeleteConfirm = React.useCallback(() => { if (deleteConfirm.keyId) { deleteKey(deleteConfirm.keyId, { onSuccess: closeDeleteConfirm }); } }, [deleteConfirm.keyId, deleteKey, closeDeleteConfirm]);
  
  const columnHelper = createColumnHelper<ApiKey>();
  
  const columns = useMemo(() => [
    columnHelper.accessor('id', { header: 'ID', size: 60, enableSorting: false, enableColumnFilter: false, meta: { icon: <FingerprintIcon fontSize="small"/> } }),
    columnHelper.accessor('name', { header: 'Name', size: 200, meta: { icon: <TitleIcon fontSize="small"/> }, cell: info => editingRowId === info.row.original.id ? <TextField fullWidth variant="standard" size="small" value={editedRowData?.name ?? ''} onChange={e => handleFieldChange('name', e.target.value)} /> : info.getValue() }),
    columnHelper.accessor('comment', { header: 'Comment', size: 300, enableSorting: false, meta: { icon: <CommentIcon fontSize="small"/> }, cell: info => editingRowId === info.row.original.id ? <TextField fullWidth variant="standard" size="small" value={editedRowData?.comment ?? ''} onChange={e => handleFieldChange('comment', e.target.value)} /> : (info.getValue() ?? <Typography color="text.secondary" component="em">N/A</Typography>) }),
    columnHelper.accessor('is_active', { header: 'Active', size: 100, enableSorting: false, enableColumnFilter: false, meta: { icon: <ToggleOnIcon fontSize="small"/> }, cell: info => <Switch checked={editingRowId === info.row.original.id ? !!editedRowData?.is_active : info.getValue()} onChange={e => handleFieldChange('is_active', e.target.checked)} readOnly={editingRowId !== info.row.original.id} /> }),
    columnHelper.accessor('key_hash', { header: 'Key Hash', size: 250, enableSorting: false, enableColumnFilter: false, meta: { icon: <VpnKeyIcon fontSize="small"/> }, cell: info => <Typography fontFamily="monospace" sx={{ wordBreak: 'break-all' }}>{info.getValue()}</Typography> }),
    columnHelper.display({ id: 'actions', header: 'Actions', size: 120, enableColumnFilter: false, cell: info => {
      const isEditingThisRow = info.row.original.id === editingRowId;
      const [anchorEl, setAnchorEl] = React.useState<null | HTMLElement>(null);
      if (isEditingThisRow) {
        return <Box display="flex" gap={1}>
          <Tooltip title="Save">
            {/* The span wrapper allows the tooltip to show even when the button is disabled */}
            <span>
              <IconButton size="small" onClick={handleEditSave} disabled={isUpdating}>
                {isUpdating ? <CircularProgress size={20}/> : <SaveIcon />}
              </IconButton>
            </span>
          </Tooltip>
          <Tooltip title="Cancel">
            <IconButton size="small" onClick={handleEditCancel}>
              <CancelIcon />
            </IconButton>
          </Tooltip>
        </Box>;
      }
      return (
        <><Tooltip title="Actions"><IconButton onClick={e => setAnchorEl(e.currentTarget)}><MoreVertIcon /></IconButton></Tooltip><Menu anchorEl={anchorEl} open={Boolean(anchorEl)} onClose={() => setAnchorEl(null)}><MenuItem onClick={() => { handleEditStart(info.row.original); setAnchorEl(null); }}><EditIcon fontSize="small" sx={{ mr: 1 }}/>Edit</MenuItem><MenuItem onClick={() => { openDeleteConfirm(info.row.original.id); setAnchorEl(null); }} sx={{ color: 'error.main' }}><DeleteIcon fontSize="small" sx={{ mr: 1 }}/>Delete</MenuItem></Menu></>
      );
    }}),
  ], [handleEditStart, handleFieldChange, editingRowId, editedRowData, isUpdating, handleDeleteConfirm, openDeleteConfirm]);

  const table = useReactTable({
    data: data ?? [], columns, pageCount,
    state: { pagination, sorting, columnFilters, globalFilter },
    onPaginationChange: setPagination, onSortingChange: setSorting, onColumnFiltersChange: setColumnFilters,
    getCoreRowModel: getCoreRowModel(), getFilteredRowModel: getFilteredRowModel(), getSortedRowModel: getSortedRowModel(),
    manualPagination: true, manualSorting: true,
  });

  if (isLoading) {
    return <TableSkeleton />;
  }
  
  return (
    <>
      <Paper sx={{ width: '100%', overflow: 'hidden', position: 'relative' }}>
        {isFetching && <LinearProgress sx={{ position: 'absolute', top: 0, width: '100%' }} />}
        <TableContainer sx={{ maxHeight: 650 }}>
          <Table stickyHeader sx={{ tableLayout: 'fixed', minWidth: 900 }}>
            <TableHead>
              {table.getHeaderGroups().map((headerGroup) => (
                <React.Fragment key={headerGroup.id}>
                  <TableRow sx={{ '& .MuiTableCell-root': { py: 1, bgcolor: (theme) => theme.palette.action.hover } }}>
                    {headerGroup.headers.map((header) => (
                      <TableCell key={header.id} sx={{ width: header.getSize(), fontWeight: 'bold', textTransform: 'uppercase', fontSize: '0.75rem', textAlign: 'center', bgcolor: header.column.getIsSorted() ? 'action.selected' : 'inherit' }}>
                        <Box onClick={header.column.getToggleSortingHandler()} sx={{ cursor: header.column.getCanSort() ? 'pointer' : 'default', userSelect: 'none', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 0.5 }}>
                          {(header.column.columnDef.meta as any)?.icon}
                          {flexRender(header.column.columnDef.header, header.getContext())}
                          {{ asc: <ArrowUpwardIcon fontSize="inherit" />, desc: <ArrowDownwardIcon fontSize="inherit" />,}[header.column.getIsSorted() as string] ?? null}
                        </Box>
                      </TableCell>
                    ))}
                  </TableRow>
                  <TableRow sx={{ '& .MuiTableCell-root': { py: 0.5, px: 1, bgcolor: (theme) => theme.palette.background.default }}}>
                    {headerGroup.headers.map((header) => (
                      <TableCell key={`${header.id}-filter`}>
                        {header.column.getCanFilter() ? <Filter column={header.column} /> : null}
                      </TableCell>
                    ))}
                  </TableRow>
                </React.Fragment>
              ))}
            </TableHead>
            <TableBody>
              {table.getRowModel().rows.map((row) => (
                <TableRow key={row.id} hover>
                  {row.getVisibleCells().map((cell) => (
                    <TableCell key={cell.id} sx={{ fontSize: '0.875rem', py: 1, wordBreak: 'break-word' }}>
                      {flexRender(cell.column.columnDef.cell, cell.getContext())}
                    </TableCell>
                  ))}
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
        <TablePagination
          rowsPerPageOptions={[10, 25, 50, 100]}
          component="div"
          count={pageCount > 0 ? pageCount * pagination.pageSize : data.length}
          rowsPerPage={pagination.pageSize ?? 10}
          page={pagination.pageIndex ?? 0}
          onPageChange={(_, newPage) => table.setPageIndex(newPage)}
          onRowsPerPageChange={e => table.setPageSize(Number(e.target.value))}
          showFirstButton showLastButton
        />
      </Paper>
      <Dialog open={deleteConfirm.isOpen} onClose={closeDeleteConfirm}>
        <DialogTitle>Confirm Deletion</DialogTitle>
        <DialogContent><DialogContentText>Are you sure you want to permanently delete this API key? This action cannot be undone.</DialogContentText></DialogContent>
        <DialogActions>
          <Button onClick={closeDeleteConfirm} disabled={isDeleting}>Cancel</Button>
          <Button onClick={handleDeleteConfirm} color="error" disabled={isDeleting}>
            {isDeleting ? <CircularProgress size={24} /> : 'Delete'}
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
};