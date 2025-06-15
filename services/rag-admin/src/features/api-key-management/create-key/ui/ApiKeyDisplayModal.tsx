// file: src/features/api-key-management/create-key/ui/ApiKeyDisplayModal.tsx

import React, { useState } from 'react';
import {
  Dialog, DialogTitle, DialogContent, DialogActions, Button,
  Typography, Box, IconButton, Tooltip, Alert,
} from '@mui/material';
import ContentCopyIcon from '@mui/icons-material/ContentCopy';

interface ApiKeyDisplayModalProps {
  apiKey: string | null;
  onClose: () => void;
}

export const ApiKeyDisplayModal: React.FC<ApiKeyDisplayModalProps> = ({ apiKey, onClose }) => {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    if (apiKey) {
      navigator.clipboard.writeText(apiKey);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000); // Reset after 2 seconds
    }
  };
  
  if (!apiKey) return null;

  return (
    <Dialog open={!!apiKey} onClose={onClose} fullWidth maxWidth="sm">
      <DialogTitle>API Key Generated Successfully</DialogTitle>
      <DialogContent>
        <Alert severity="warning" sx={{ mb: 2 }}>
          Please save this secret key somewhere safe. You will not be able to see it again.
        </Alert>

        <Box
          sx={{
            p: 2,
            border: '1px solid',
            borderColor: 'divider',
            borderRadius: 1,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            fontFamily: 'monospace',
            bgcolor: 'action.hover',
            wordBreak: 'break-all',
          }}
        >
          {apiKey}
          <Tooltip title={copied ? 'Copied!' : 'Copy to clipboard'}>
            <IconButton onClick={handleCopy}>
              <ContentCopyIcon />
            </IconButton>
          </Tooltip>
        </Box>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose} variant="contained">
          I have saved my key
        </Button>
      </DialogActions>
    </Dialog>
  );
};