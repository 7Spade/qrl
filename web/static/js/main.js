// Main application initialization and utility functions

// Update current time
function updateTime() {
  const now = new Date();
  document.getElementById('current-time').textContent = now.toISOString().replace('T', ' ').substring(0, 19);
}

// Refresh all data
function refreshAllData() {
  fetchChartData();
  fetchMarketData();
  fetchPositionData();
  fetchStrategyData();
  fetchSystemData();
  updateTime();
}

// Timeframe selector event handlers
function initializeTimeframeButtons() {
  const timeframeBtns = document.querySelectorAll('.timeframe-btn');
  timeframeBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      // Update active state
      timeframeBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      
      // Update current timeframe and reload charts
      currentTimeframe = btn.dataset.timeframe;
      document.getElementById('chartLoading').style.display = 'block';
      fetchChartData();
    });
  });
}

// Initialize on load
document.addEventListener('DOMContentLoaded', function() {
  initializeCharts();
  initializeTimeframeButtons();
  refreshAllData();
  
  // Auto-refresh every 60 seconds
  setInterval(refreshAllData, 60000);
  
  // Update time every second
  setInterval(updateTime, 1000);
});
