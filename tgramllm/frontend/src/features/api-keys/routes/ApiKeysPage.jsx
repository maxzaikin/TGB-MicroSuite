import React, { useReducer, useEffect } from 'react';
import axios from 'axios';
import {
  Table, TableBody, TableCell, TableContainer,
  TableHead, TableRow, Paper, Typography, Box
} from '@mui/material';

const initialState = {
  data: [],
  isLoading: false,
  isError: false,
};

const reducer = (state, action) => {
  switch (action.type) {
    case 'FETCH_INIT':
      return { ...state, isLoading: true, isError: false };
    case 'FETCH_SUCCESS':
      return { ...state, isLoading: false, isError: false, data: action.payload };
    case 'FETCH_FAILURE':
      return { ...state, isLoading: false, isError: true, data: [] };
    default:
      return state;
  }
};

const ApiKeysPage = () => {
  const [state, dispatch] = useReducer(reducer, initialState);

  useEffect(() => {
    const fetchData = async () => {
      dispatch({ type: 'FETCH_INIT' });
      try {
        const response = await axios.get('/api/v1/api-keys');
        if (Array.isArray(response.data)) {
          dispatch({ type: 'FETCH_SUCCESS', payload: response.data });
        } else {
          dispatch({ type: 'FETCH_FAILURE' });
        }
      } catch (error) {
        console.error('Failed to fetch API keys:', error);
        dispatch({ type: 'FETCH_FAILURE' });
      }
    };

    fetchData();
  }, []);

  return (
    <Box p={3}>
      <Typography variant="h5" gutterBottom>
        API Key Management
      </Typography>

      {state.isError && (
        <Typography variant="body2" color="error" sx={{ mb: 2 }}>
          ❌ Error loading data from server. Please try again later.
        </Typography>
      )}

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>ID</TableCell>
              <TableCell>Name</TableCell>
              <TableCell>Token</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {state.data.length > 0 ? (
              state.data.map((row) => (
                <TableRow key={row.id}>
                  <TableCell>{row.id}</TableCell>
                  <TableCell>{row.name}</TableCell>
                  <TableCell>{row.token}</TableCell>
                </TableRow>
              ))
            ) : (
              <TableRow>
                <TableCell colSpan={3} align="center">
                  No data available
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
};

export default ApiKeysPage;
