import React from 'react';
import { Box, Paper } from '@mui/material';
import { Pie } from 'react-chartjs-2';
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js';

// Register Chart.js components
ChartJS.register(ArcElement, Tooltip, Legend);

const SentimentChart = ({ data }) => {
  const chartData = {
    labels: ['Positive', 'Neutral', 'Negative'],
    datasets: [
      {
        data: [
          data.positive || 0,
          data.neutral || 0,
          data.negative || 0
        ],
        backgroundColor: [
          '#4caf50', // Green for positive
          '#ffb74d', // Amber for neutral
          '#f44336'  // Red for negative
        ],
        borderWidth: 1,
      },
    ],
  };

  const options = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top',
      },
      tooltip: {
        callbacks: {
          label: function(context) {
            const label = context.label || '';
            const value = context.raw || 0;
            const total = context.dataset.data.reduce((a, b) => a + b, 0);
            const percentage = ((value / total) * 100).toFixed(1);
            return `${label}: ${value} (${percentage}%)`;
          }
        }
      }
    },
  };

  // If there's no data or all values are 0, show a message
  if (!data || (data.positive === 0 && data.neutral === 0 && data.negative === 0)) {
    return (
      <Paper sx={{ p: 3, textAlign: 'center' }}>
        No sentiment data available
      </Paper>
    );
  }

  return (
    <Box sx={{ maxWidth: 400, margin: '0 auto' }}>
      <Pie data={chartData} options={options} />
    </Box>
  );
};

export default SentimentChart;
