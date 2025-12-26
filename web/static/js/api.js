// API data fetching module

// Fetch chart data from Redis-cached API
async function fetchChartData() {
  try {
    const [chartResponse, indicatorsResponse] = await Promise.all([
      fetch(`/api/market/chart-data?timeframe=${currentTimeframe}`),
      fetch(`/api/market/indicators?timeframe=${currentTimeframe}`)
    ]);
    
    const chartData = await chartResponse.json();
    const indicatorsData = await indicatorsResponse.json();
    
    if (chartData.error || indicatorsData.error) {
      const errorMsg = chartData.message || indicatorsData.message || chartData.error || indicatorsData.error;
      console.log('Chart data unavailable:', errorMsg);
      document.getElementById('chartLoading').innerHTML = 
        `<span class="status-warning">${errorMsg}</span>`;
      return;
    }
    
    updateCharts(chartData, indicatorsData);
  } catch (error) {
    console.error('Error fetching chart data:', error);
    document.getElementById('chartLoading').innerHTML = 
      `<span class="negative">Failed to load charts</span>`;
  }
}

// Fetch market data
async function fetchMarketData() {
  try {
    const response = await fetch('/api/market');
    const data = await response.json();
    
    if (data.error) {
      // Show error message for market data
      document.getElementById('market-data').innerHTML = 
        `<div class="data-row"><span class="status-warning">${data.error}</span></div>`;
      // Don't return early - market data error doesn't affect balance display
    } else {
      const changeClass = data.change_24h >= 0 ? 'positive' : 'negative';
      const changeSymbol = data.change_24h >= 0 ? '+' : '';
      
      document.getElementById('market-data').innerHTML = `
        <div class="data-row">
          <span class="label">Symbol:</span>
          <span class="value">${data.symbol}</span>
        </div>
        <div class="data-row">
          <span class="label">Price:</span>
          <span class="value">$${data.price.toFixed(6)}</span>
        </div>
        <div class="data-row">
          <span class="label">24H Change:</span>
          <span class="value ${changeClass}">${changeSymbol}${data.change_24h.toFixed(2)}%</span>
        </div>
        <div class="data-row">
          <span class="label">EMA 20:</span>
          <span class="value">$${data.ema20.toFixed(6)}</span>
        </div>
        <div class="data-row">
          <span class="label">EMA 60:</span>
          <span class="value">$${data.ema60.toFixed(6)}</span>
        </div>
        <div class="data-row">
          <span class="label">Data Delay:</span>
          <span class="value status-connected">< 1s (Redis)</span>
        </div>
      `;
    }
  } catch (error) {
    console.error('Error fetching market data:', error);
    document.getElementById('market-data').innerHTML = 
      `<div class="data-row"><span class="negative">Failed to fetch market data</span></div>`;
  }
}

// Fetch position data
async function fetchPositionData() {
  try {
    const statsResponse = await fetch('/api/statistics');
    const statsData = await statsResponse.json();
    
    // Fetch market data for balances
    const marketResponse = await fetch('/api/market');
    const marketData = await marketResponse.json();
    
    // Get values with fallbacks (don't block on errors)
    const utilization = statsData.position_utilization_pct || 0;
    const currentPosition = statsData.current_position || 0;
    const maxPosition = statsData.max_position_usdt || 0;
    const availableCapacity = statsData.available_capacity || 0;
    
    // Get balances from market data - ALWAYS display these
    const qrlBalance = marketData.balances?.qrl || 0;
    const usdtBalance = marketData.balances?.usdt || 0;
    
    document.getElementById('position-data').innerHTML = `
      <div class="data-row">
        <span class="label">QRL Holdings:</span>
        <span class="value positive">${qrlBalance.toFixed(4)} QRL</span>
      </div>
      <div class="data-row">
        <span class="label">USDT Balance:</span>
        <span class="value">${usdtBalance.toFixed(2)} USDT</span>
      </div>
      <div class="data-row">
        <span class="label">Current Position:</span>
        <span class="value">$${currentPosition.toFixed(2)}</span>
      </div>
      <div class="data-row">
        <span class="label">Max Position:</span>
        <span class="value">$${maxPosition.toFixed(2)}</span>
      </div>
      <div class="data-row">
        <span class="label">Available:</span>
        <span class="value">$${availableCapacity.toFixed(2)}</span>
      </div>
      <div class="data-row">
        <span class="label">Utilization:</span>
      </div>
      <div class="progress-bar">
        <div class="progress-fill" style="width: ${utilization}%">${utilization.toFixed(1)}%</div>
      </div>
    `;
  } catch (error) {
    console.error('Error fetching position data:', error);
    document.getElementById('position-data').innerHTML = 
      `<div class="data-row"><span class="negative">Error loading position data</span></div>`;
  }
}

// Fetch strategy status
async function fetchStrategyData() {
  try {
    const marketResponse = await fetch('/api/market');
    const marketData = await marketResponse.json();
    
    const statsResponse = await fetch('/api/statistics');
    const statsData = await statsResponse.json();
    
    // Handle errors with specific messages
    if (marketData.error) {
      const errorMsg = marketData.error.includes('OHLCV') || marketData.error.includes('empty') 
        ? '⚠️ Waiting for market data... (Exchange may be initializing)'
        : marketData.error.includes('not initialized')
        ? '⚠️ System initializing... Please wait.'
        : `⚠️ ${marketData.error}`;
      
      document.getElementById('strategy-data').innerHTML = 
        `<div class="data-row"><span class="status-warning">${errorMsg}</span></div>`;
      return;
    }
    
    if (statsData.error) {
      document.getElementById('strategy-data').innerHTML = 
        `<div class="data-row"><span class="status-warning">⚠️ ${statsData.error}</span></div>`;
      return;
    }
    
    const buyThreshold = marketData.ema60 * 1.02;
    let statusText = '⏸️ Waiting';
    let detailText = 'Analyzing market conditions...';
    
    if (marketData.buy_signal) {
      statusText = '✅ Ready to Buy';
      detailText = 'Conditions met - Ready to execute';
    } else if (marketData.price > buyThreshold) {
      if (marketData.ema20 < marketData.ema60) {
        detailText = 'Price too high & Momentum weak';
      } else {
        detailText = 'Price above threshold';
      }
    } else if (marketData.ema20 < marketData.ema60) {
      detailText = 'Weak momentum (EMA20 < EMA60)';
    }
    
    document.getElementById('strategy-data').innerHTML = `
      <div class="data-row">
        <span class="label">Status:</span>
        <span class="value ${marketData.buy_signal ? 'positive' : 'status-warning'}">${statusText}</span>
      </div>
      <div class="data-row">
        <span class="label">Details:</span>
        <span class="value">${detailText}</span>
      </div>
      <div class="data-row">
        <span class="label">Buy Condition:</span>
        <span class="value">Price ≤ $${buyThreshold.toFixed(6)}</span>
      </div>
      <div class="data-row">
        <span class="label">Last Trade:</span>
        <span class="value">${statsData.last_trade_time || 'None'}</span>
      </div>
    `;
  } catch (error) {
    console.error('Error fetching strategy data:', error);
  }
}

// Fetch system status
async function fetchSystemData() {
  try {
    const healthResponse = await fetch('/health');
    const healthData = await healthResponse.json();
    
    const cacheResponse = await fetch('/api/cache/stats');
    const cacheData = await cacheResponse.json();
    
    // Health check status
    const healthStatus = healthData.status === 'healthy' ? '✅ Healthy' : '❌ Unhealthy';
    const healthStatusClass = healthData.status === 'healthy' ? 'status-connected' : 'status-disconnected';
    
    // API connection status
    const apiStatus = healthData.status === 'healthy' ? '● Connected' : '⚠ Error';
    const apiStatusClass = healthData.status === 'healthy' ? 'status-connected' : 'status-disconnected';
    
    // Cache status
    const cacheStatus = cacheData.enabled ? '✅ Enabled' : '❌ Disabled';
    const cacheStatusClass = cacheData.enabled ? 'status-connected' : 'status-disconnected';
    
    document.getElementById('system-data').innerHTML = `
      <div class="data-row">
        <span class="label">System Health:</span>
        <span class="value ${healthStatusClass}">${healthStatus}</span>
      </div>
      <div class="data-row">
        <span class="label">API Connection:</span>
        <span class="value ${apiStatusClass}">${apiStatus}</span>
      </div>
      <div class="data-row">
        <span class="label">Redis Cache:</span>
        <span class="value ${cacheStatusClass}">${cacheStatus}</span>
      </div>
      <div class="data-row">
        <span class="label">Data Delay:</span>
        <span class="value status-connected">${cacheData.enabled ? '< 100ms' : '200-500ms'}</span>
      </div>
      <div class="data-row">
        <span class="label">Cache Keys:</span>
        <span class="value">${cacheData.cache_keys || 0}</span>
      </div>
    `;
  } catch (error) {
    console.error('Error fetching system data:', error);
  }
}
