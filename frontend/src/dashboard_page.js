import React, { useState, useEffect } from 'react';
import { Paper, Grid, Typography, Button } from '@mui/material';
import { useSuspenseQuery } from '@tanstack/react-query';
import { stockApi } from '../api/stockApi';
import type { StockData } from '~types/stock';

const Dashboard = () => {
  const [state, setState] = useState('');
  const { data, isLoading } = useSuspenseQuery<StockData>({
    queryKey: ['stock'],
    queryFn: () => stockApi.getStock(),
  });

  if (isLoading) return <div>Loading...</div>;

  return (
    <Paper sx={{ p: 2 }}>
      <Grid container spacing={2}>
        <Grid item xs={12}>
          <Typography variant="h5">Current Stock Price</Typography>
        </Grid>
        <Grid item xs={12}>
          <Typography variant="body1">${data?.stockPrice}</Typography>
        </Grid>
        <Grid item xs={12}>
          <Button variant="contained" onClick={() => setState('updated')}>Update</Button>
        </Grid>
        {data?.map((stock) => (
          <Grid item xs={12} key={stock.id}>
            <Typography variant="body1">{stock.name}</Typography>
            <img src={stock.graph} alt={stock.name} />
          </Grid>
        ))}
      </Grid>
    </Paper>
  );
};

export default Dashboard;
