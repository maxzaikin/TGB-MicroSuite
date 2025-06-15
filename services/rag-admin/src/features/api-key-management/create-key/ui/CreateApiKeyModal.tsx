// file: src/features/api-key-management/create-key/ui/CreateApiKeyModal.tsx

import React, { useState, useEffect } from 'react';
import {
  Dialog, DialogTitle, DialogContent, DialogActions, Button,
  TextField, FormControlLabel, Switch, Box, CircularProgress, Alert,
} from '@mui/material';
import { useCreateApiKey, type NewApiKey, type ApiKeyGenerated } from '@/entities/api-key';

// --- Props Interface ---
interface CreateApiKeyModalProps {
  isOpen: boolean;
  onClose: () => void;
  // Callback function to pass the newly created key to the parent component.
  onSuccess: (apiKey: string) => void;
}

// --- Helper Function for Error Handling ---
function getErrorMessage(error: unknown): string {
  const defaultMessage = 'An unexpected error occurred. Please try again.';
  if (!error || typeof error !== 'object') return defaultMessage;

  if ('response' in error && error.response && typeof error.response === 'object' &&
      'data' in error.response && error.response.data && typeof error.response.data === 'object' &&
      'detail' in error.response.data) {
    const detail = (error.response.data as any).detail;
    if (Array.isArray(detail) && detail.length > 0 && typeof detail[0] === 'object') {
      const firstError = detail[0];
      const location = firstError.loc?.join(' > ') || 'field';
      return `Validation Error: ${firstError.msg} (in ${location})`;
    }
    if (typeof detail === 'string') return detail;
  }
  if ('message' in error && typeof error.message === 'string') return error.message;
  return defaultMessage;
}

// --- Main Component ---
export const CreateApiKeyModal: React.FC<CreateApiKeyModalProps> = ({
  isOpen,
  onClose,
  onSuccess,
}) => {
  const [name, setName] = useState('');
  const [comment, setComment] = useState('');
  const [isActive, setIsActive] = useState(true);

  const { mutate: createKey, isPending, error, reset } = useCreateApiKey();

  // Effect to reset the form state when the modal is closed.
  useEffect(() => {
    if (!isOpen) {
      const timer = setTimeout(() => {
        setName('');
        setComment('');
        setIsActive(true);
        reset(); // Reset React Query mutation state (error, etc.)
      }, 300); // Delay to avoid state change during closing animation
      return () => clearTimeout(timer);
    }
  }, [isOpen, reset]);

  const handleSave = () => {
    const trimmedName = name.trim();
    if (!trimmedName) return; // Basic validation

    const newKey: NewApiKey = {
      name: trimmedName,
      comment: comment.trim() || null,
      is_active: isActive,
    };

    createKey(newKey, {
      onSuccess: (createdKey: ApiKeyGenerated) => {
        // Pass the raw API key to the parent component via the callback.
        onSuccess(createdKey.api_key);
      },
    });
  };

  return (
    <Dialog open={isOpen} onClose={onClose} fullWidth maxWidth="sm">
      <DialogTitle>Create New API Key</DialogTitle>
      <DialogContent>
        <Box component="form" noValidate sx={{ mt: 1 }}>
          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {getErrorMessage(error)}
            </Alert>
          )}
          <TextField
            autoFocus
            required
            margin="dense"
            id="name"
            label="Key Name"
            type="text"
            fullWidth
            variant="outlined"
            value={name}
            onChange={(e) => setName(e.target.value)}
            disabled={isPending}
          />
          <TextField
            margin="dense"
            id="comment"
            label="Comment (Optional)"
            type="text"
            fullWidth
            variant="outlined"
            value={comment}
            onChange={(e) => setComment(e.target.value)}
            disabled={isPending}
          />
          <FormControlLabel
            control={<Switch checked={isActive} onChange={(e) => setIsActive(e.target.checked)} disabled={isPending} />}
            label="Active"
          />
        </Box>
      </DialogContent>
      <DialogActions sx={{ px: 3, pb: 2 }}>
        <Button onClick={onClose} disabled={isPending}>Cancel</Button>
        <Button onClick={handleSave} variant="contained" disabled={isPending || !name.trim()}>
          {isPending ? <CircularProgress size={24} color="inherit" /> : 'Create Key'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};