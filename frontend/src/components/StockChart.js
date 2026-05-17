import React from 'react';
import Plot from 'react-plotly.js';

function StockChart({ data }) {
  if (!data || !data.data || data.data.length === 0) {
    return (
      <div style={{
        height: '400px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        color: '#94a3b8',
        flexDirection: 'column',
        gap: '0.5rem',
        background: 'linear-gradient(135deg, rgba(51, 65, 85, 0.1) 0%, transparent 100%)',
        borderRadius: '12px',
        border: '1px solid rgba(51, 65, 85, 0.3)'
      }}>
        <span style={{ fontSize: '2rem' }}>📊</span>
        <span>No chart data available</span>
      </div>
    );
  }

  const ticker = data.ticker;
  
  // Extract prices and dates from data
  const dates = data.data.map(d => d.date);
  const opens = data.data.map(d => d.open);
  const highs = data.data.map(d => d.high);
  const lows = data.data.map(d => d.low);
  const closes = data.data.map(d => d.close);
  const volumes = data.data.map(d => d.volume);

  // Candlestick trace
  const candleData = {
    x: dates,
    open: opens,
    high: highs,
    low: lows,
    close: closes,
    type: 'candlestick',
    name: ticker,
    increasing: { line: { color: '#10b981' }, fillcolor: '#10b981' },
    decreasing: { line: { color: '#ef4444' }, fillcolor: '#ef4444' },
  };

  // Volume trace
  const volumeData = {
    x: dates,
    y: volumes,
    type: 'bar',
    name: 'Volume',
    marker: {
      color: closes.map((c, i) => c >= opens[i] ? '#10b98160' : '#ef444460'),
    },
    yaxis: 'y2',
  };

  const traceData = [candleData, volumeData];

  const layout = {
    title: {
      text: `${ticker} ${data.period ? `(${data.period})` : ''}`,
      font: {
        color: '#e2e8f0',
        size: 18,
        weight: 'bold'
      }
    },
    yaxis: {
      title: { text: 'Price ($)', font: { color: '#e2e8f0', size: 14 } },
      side: 'left',
      gridcolor: '#334155',
      tickfont: { color: '#94a3b8' },
      zerolinecolor: '#334155',
    },
    yaxis2: {
      title: { text: 'Volume', font: { color: '#e2e8f0', size: 14 } },
      overlaying: 'y',
      side: 'right',
      tickfont: { color: '#94a3b8' },
      zerolinecolor: '#334155',
      showgrid: false,
    },
    xaxis: {
      type: 'date',
      tickfont: { color: '#94a3b8' },
      gridcolor: '#334155',
      zerolinecolor: '#334155',
    },
    plot_bgcolor: '#0f172a',
    paper_bgcolor: '#1e293b',
    hovermode: 'x unified',
    font: { color: '#e2e8f0', family: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif' },
    height: 500,
    margin: { l: 60, r: 60, t: 60, b: 60 },
    legend: {
      font: { color: '#e2e8f0' },
      bgcolor: 'rgba(30, 41, 59, 0.8)',
      bordercolor: '#334155',
      borderwidth: 1
    }
  };

  const config = {
    responsive: true,
    displayModeBar: true,
    modeBarButtonsToRemove: ['lasso2d', 'select2d'],
    displaylogo: false,
    toImageButtonOptions: {
      format: 'png',
      filename: `${ticker}_chart`,
      height: 500,
      width: 1200,
      scale: 2
    }
  };

  return (
    <div className="chart-container" style={{ animation: 'fadeIn 0.6s ease' }}>
      <Plot
        data={traceData}
        layout={layout}
        style={{ width: '100%', height: '500px' }}
        config={config}
      />
      <div style={{
        marginTop: '1rem',
        padding: '1rem',
        background: 'linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, transparent 100%)',
        borderRadius: '8px',
        border: '1px solid rgba(51, 65, 85, 0.5)',
        display: 'flex',
        gap: '2rem',
        justifyContent: 'space-around',
        flexWrap: 'wrap'
      }}>
        <div style={{ textAlign: 'center' }}>
          <div style={{ fontSize: '0.85rem', color: '#94a3b8', marginBottom: '0.25rem' }}>📈 Range</div>
          <div style={{ fontSize: '1.1rem', color: '#e2e8f0', fontWeight: '600' }}>
            ${Math.min(...closes).toFixed(2)} - ${Math.max(...closes).toFixed(2)}
          </div>
        </div>
        <div style={{ textAlign: 'center' }}>
          <div style={{ fontSize: '0.85rem', color: '#94a3b8', marginBottom: '0.25rem' }}>📊 Data Points</div>
          <div style={{ fontSize: '1.1rem', color: '#e2e8f0', fontWeight: '600' }}>
            {closes.length.toLocaleString()}
          </div>
        </div>
        <div style={{ textAlign: 'center' }}>
          <div style={{ fontSize: '0.85rem', color: '#94a3b8', marginBottom: '0.25rem' }}>💰 Current</div>
          <div style={{ fontSize: '1.1rem', color: '#e2e8f0', fontWeight: '600' }}>
            ${closes[closes.length - 1]?.toFixed(2) || 'N/A'}
          </div>
        </div>
      </div>
      <style>{`
        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(10px); }
          to { opacity: 1; transform: translateY(0); }
        }
      `}</style>
    </div>
  );
}

export default StockChart;
