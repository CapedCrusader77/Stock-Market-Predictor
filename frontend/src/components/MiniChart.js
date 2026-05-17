import React from 'react';
import Plot from 'react-plotly.js';

function MiniChart({ ticker, data, height = 80 }) {
  if (!data || data.length === 0) {
    return (
      <div style={{
        height: `${height}px`,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        color: '#64748b',
        fontSize: '0.75rem',
        background: 'rgba(0, 0, 0, 0.2)',
        borderRadius: '4px'
      }}>
        No data
      </div>
    );
  }

  const prices = data.map(d => d.price);
  const dates = data.map(d => d.date);

  const firstPrice = prices[0];
  const lastPrice = prices[prices.length - 1];
  const isPositive = lastPrice >= firstPrice;

  const color = isPositive ? '#26a69a' : '#ef5350';
  const fillColor = isPositive ? 'rgba(38, 166, 154, 0.15)' : 'rgba(239, 83, 80, 0.15)';

  const trace = {
    x: dates,
    y: prices,
    type: 'scatter',
    mode: 'lines',
    line: {
      color: color,
      width: 2,
      shape: 'spline'
    },
    fill: 'tozeroy',
    fillcolor: fillColor,
    hoverinfo: 'x+y',
    hovertemplate: '%{x}<br>Price: $%{y:.2f}<extra></extra>'
  };

  const layout = {
    margin: { l: 0, r: 0, t: 0, b: 0 },
    showlegend: false,
    xaxis: {
      showgrid: false,
      showticklabels: false,
      zeroline: false,
      fixedrange: true
    },
    yaxis: {
      showgrid: false,
      showticklabels: false,
      zeroline: false,
      fixedrange: true
    },
    plot_bgcolor: 'transparent',
    paper_bgcolor: 'transparent',
    height: height,
    hovermode: 'x unified',
    dragmode: false
  };

  const config = {
    responsive: true,
    displayModeBar: false,
    displaylogo: false,
    scrollZoom: false,
    doubleClick: false
  };

  return (
    <div className="mini-chart" style={{ width: '100%', height: `${height}px` }}>
      <Plot
        data={[trace]}
        layout={layout}
        style={{ width: '100%', height: `${height}px` }}
        config={config}
        useResizeHandler={true}
      />
    </div>
  );
}

export default MiniChart;