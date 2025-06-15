// file: src/features/api-key-management/create-key/ui/CreateApiKeyButton.tsx

import React, { useState } from 'react';
import { Button } from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import { CreateApiKeyModal } from './CreateApiKeyModal';
import { ApiKeyDisplayModal } from './ApiKeyDisplayModal';

/**
 * A feature component that orchestrates the entire API key creation flow.
 * It manages the state for both the creation form and the key display modal.
 */
export const CreateApiKeyButton: React.FC = () => {
  const [isFormOpen, setIsFormOpen] = useState(false);
  // This state will hold the newly generated key to be displayed
  const [newApiKey, setNewApiKey] = useState<string | null>(null);

  const handleFormOpen = () => setIsFormOpen(true);
  
  const handleFormClose = () => setIsFormOpen(false);
  
  const handleDisplayClose = () => setNewApiKey(null);

  // This function will be passed to the form modal to receive the new key
  const handleKeyCreated = (key: string) => {
    setIsFormOpen(false); // Close the form modal
    setNewApiKey(key);    // Set the new key to open the display modal
  };

  return (
    <>
      <Button variant="contained" startIcon={<AddIcon />} onClick={handleFormOpen}>
        Add New Key
      </Button>

      {/* The form modal */}
      <CreateApiKeyModal
        isOpen={isFormOpen}
        onClose={handleFormClose}
        onSuccess={handleKeyCreated}
      />

      {/* The result display modal */}
      <ApiKeyDisplayModal apiKey={newApiKey} onClose={handleDisplayClose} />
    </>
  );
};