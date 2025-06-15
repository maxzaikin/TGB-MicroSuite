// file: src/widgets/ApiKeysTable/TableSkeleton.tsx

import React from 'react';
import { Skeleton, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper } from '@mui/material';

export const TableSkeleton: React.FC = () => (
  <TableContainer component={Paper}>
    <Table>
      <TableHead>
        <TableRow>
          {[...Array(6)].map((_, i) => ( // Render 6 skeleton header cells
            <TableCell key={i}><Skeleton variant="text" sx={{ fontSize: '1rem' }} /></TableCell>
          ))}
        </TableRow>
      </TableHead>
      <TableBody>
        {[...Array(5)].map((_, i) => ( // Render 5 skeleton body rows
          <TableRow key={i}>
            {[...Array(6)].map((_, j) => (
              <TableCell key={j}><Skeleton variant="text" /></TableCell>
            ))}
          </TableRow>
        ))}
      </TableBody>
    </Table>
  </TableContainer>
);