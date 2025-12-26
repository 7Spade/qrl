// Chart management module
// Global chart instances
let priceChart = null;
let volumeChart = null;
let williamsChart = null;
let macdChart = null;
let rsiChart = null;
let currentTimeframe = '1m';

// Initialize all charts
function initializeCharts() {
  // Price Chart
  const priceCtx = document.getElementById('priceChart').getContext('2d');
  priceChart = new Chart(priceCtx, {
    type: 'line',
    data: {
      labels: [],
      datasets: [
        {
          label: 'Price (QRL/USDT)',
          data: [],
          borderColor: '#00ff41',
          backgroundColor: 'rgba(0, 255, 65, 0.1)',
          borderWidth: 2,
          pointRadius: 0,
          tension: 0.1
        },
        {
          label: 'MA 20',
          data: [],
          borderColor: '#ff9500',
          borderWidth: 1,
          pointRadius: 0,
          tension: 0.1
        },
        {
          label: 'MA 60',
          data: [],
          borderColor: '#00d4ff',
          borderWidth: 1,
          pointRadius: 0,
          tension: 0.1
        },
        {
          label: 'EMA 20',
          data: [],
          borderColor: '#ff00ff',
          borderWidth: 1,
          borderDash: [5, 5],
          pointRadius: 0,
          tension: 0.1
        },
        {
          label: 'EMA 60',
          data: [],
          borderColor: '#ffff00',
          borderWidth: 1,
          borderDash: [5, 5],
          pointRadius: 0,
          tension: 0.1
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: {
        intersect: false,
        mode: 'index'
      },
      plugins: {
        legend: {
          labels: { color: '#00ff41' }
        },
        tooltip: {
          backgroundColor: 'rgba(0, 0, 0, 0.8)',
          borderColor: '#00ff41',
          borderWidth: 1
        }
      },
      scales: {
        x: {
          ticks: { color: '#00ff41', maxTicksLimit: 10 },
          grid: { color: 'rgba(0, 255, 65, 0.1)' }
        },
        y: {
          ticks: { color: '#00ff41' },
          grid: { color: 'rgba(0, 255, 65, 0.1)' }
        }
      }
    }
  });

  // Volume Chart
  const volumeCtx = document.getElementById('volumeChart').getContext('2d');
  volumeChart = new Chart(volumeCtx, {
    type: 'bar',
    data: {
      labels: [],
      datasets: [{
        label: 'Volume',
        data: [],
        backgroundColor: [],
        borderColor: [],
        borderWidth: 1
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { labels: { color: '#00ff41' } }
      },
      scales: {
        x: {
          ticks: { color: '#00ff41', maxTicksLimit: 10 },
          grid: { color: 'rgba(0, 255, 65, 0.1)' }
        },
        y: {
          ticks: { color: '#00ff41' },
          grid: { color: 'rgba(0, 255, 65, 0.1)' }
        }
      }
    }
  });

  // Williams %R Chart
  const williamsCtx = document.getElementById('williamsChart').getContext('2d');
  williamsChart = new Chart(williamsCtx, {
    type: 'line',
    data: {
      labels: [],
      datasets: [{
        label: 'Williams %R',
        data: [],
        borderColor: '#ff9500',
        backgroundColor: 'rgba(255, 149, 0, 0.1)',
        borderWidth: 2,
        pointRadius: 0,
        tension: 0.1
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { labels: { color: '#00ff41' } },
        annotation: {
          annotations: {
            oversold: {
              type: 'line',
              yMin: -80,
              yMax: -80,
              borderColor: '#00ff41',
              borderWidth: 1,
              borderDash: [5, 5]
            },
            overbought: {
              type: 'line',
              yMin: -20,
              yMax: -20,
              borderColor: '#ff0000',
              borderWidth: 1,
              borderDash: [5, 5]
            }
          }
        }
      },
      scales: {
        x: {
          ticks: { color: '#00ff41', maxTicksLimit: 10 },
          grid: { color: 'rgba(0, 255, 65, 0.1)' }
        },
        y: {
          min: -100,
          max: 0,
          ticks: { color: '#00ff41' },
          grid: { color: 'rgba(0, 255, 65, 0.1)' }
        }
      }
    }
  });

  // MACD Chart
  const macdCtx = document.getElementById('macdChart').getContext('2d');
  macdChart = new Chart(macdCtx, {
    type: 'line',
    data: {
      labels: [],
      datasets: [
        {
          label: 'MACD',
          data: [],
          borderColor: '#00d4ff',
          borderWidth: 2,
          pointRadius: 0,
          tension: 0.1,
          yAxisID: 'y'
        },
        {
          label: 'Signal',
          data: [],
          borderColor: '#ff9500',
          borderWidth: 2,
          pointRadius: 0,
          tension: 0.1,
          yAxisID: 'y'
        },
        {
          label: 'Histogram',
          data: [],
          backgroundColor: 'rgba(0, 255, 65, 0.3)',
          borderColor: '#00ff41',
          borderWidth: 1,
          type: 'bar',
          yAxisID: 'y'
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { labels: { color: '#00ff41' } }
      },
      scales: {
        x: {
          ticks: { color: '#00ff41', maxTicksLimit: 10 },
          grid: { color: 'rgba(0, 255, 65, 0.1)' }
        },
        y: {
          ticks: { color: '#00ff41' },
          grid: { color: 'rgba(0, 255, 65, 0.1)' }
        }
      }
    }
  });

  // RSI Chart
  const rsiCtx = document.getElementById('rsiChart').getContext('2d');
  rsiChart = new Chart(rsiCtx, {
    type: 'line',
    data: {
      labels: [],
      datasets: [{
        label: 'RSI',
        data: [],
        borderColor: '#00ff41',
        backgroundColor: 'rgba(0, 255, 65, 0.1)',
        borderWidth: 2,
        pointRadius: 0,
        tension: 0.1
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { labels: { color: '#00ff41' } },
        annotation: {
          annotations: {
            oversold: {
              type: 'line',
              yMin: 30,
              yMax: 30,
              borderColor: '#00ff41',
              borderWidth: 1,
              borderDash: [5, 5]
            },
            overbought: {
              type: 'line',
              yMin: 70,
              yMax: 70,
              borderColor: '#ff0000',
              borderWidth: 1,
              borderDash: [5, 5]
            }
          }
        }
      },
      scales: {
        x: {
          ticks: { color: '#00ff41', maxTicksLimit: 10 },
          grid: { color: 'rgba(0, 255, 65, 0.1)' }
        },
        y: {
          min: 0,
          max: 100,
          ticks: { color: '#00ff41' },
          grid: { color: 'rgba(0, 255, 65, 0.1)' }
        }
      }
    }
  });
}

// Update all charts with new data
function updateCharts(chartData, indicatorsData) {
  if (!priceChart) {
    initializeCharts();
  }
  
  // Update Price Chart
  priceChart.data.labels = chartData.labels;
  priceChart.data.datasets[0].data = chartData.prices;
  priceChart.data.datasets[1].data = chartData.ma20;
  priceChart.data.datasets[2].data = chartData.ma60;
  priceChart.data.datasets[3].data = chartData.ema20;
  priceChart.data.datasets[4].data = chartData.ema60;
  priceChart.update();
  
  // Update Volume Chart
  volumeChart.data.labels = chartData.labels;
  volumeChart.data.datasets[0].data = chartData.volumes;
  volumeChart.data.datasets[0].backgroundColor = indicatorsData.volume_colors;
  volumeChart.data.datasets[0].borderColor = indicatorsData.volume_colors;
  volumeChart.update();
  
  // Update Williams %R Chart
  williamsChart.data.labels = indicatorsData.labels;
  williamsChart.data.datasets[0].data = indicatorsData.williams_r;
  williamsChart.update();
  
  // Update MACD Chart
  macdChart.data.labels = indicatorsData.labels;
  macdChart.data.datasets[0].data = indicatorsData.macd;
  macdChart.data.datasets[1].data = indicatorsData.macd_signal;
  macdChart.data.datasets[2].data = indicatorsData.macd_histogram;
  macdChart.update();
  
  // Update RSI Chart
  rsiChart.data.labels = indicatorsData.labels;
  rsiChart.data.datasets[0].data = indicatorsData.rsi;
  rsiChart.update();
  
  // Hide loading message
  document.getElementById('chartLoading').style.display = 'none';
}
