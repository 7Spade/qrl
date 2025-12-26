# Technical Indicators Guide

Complete guide to the technical indicators implemented in the QRL trading bot, calculated from Redis-cached MEXC API data.

## Overview

The QRL trading bot now includes 6 advanced technical indicators, all calculated server-side from MEXC OHLCV data automatically cached in Redis. All indicators are displayed on interactive Chart.js visualizations.

##  📊 Indicators Implemented

### 1. Williams %R (Williams Percent Range)

**Purpose**: Momentum oscillator that measures overbought/oversold levels.

**Calculation**:
```
Williams %R = ((Highest High - Close) / (Highest High - Lowest Low)) × -100
```

**Parameters**:
- Period: 14
- Range: -100 to 0

**Interpretation**:
- **-20 to 0** (Overbought): Potential sell signal
- **-80 to -100** (Oversold): Potential buy signal
- **-20 to -80** (Normal range): No strong signal

**Chart Display**:
- Line chart with -20 and -80 reference lines
- Color: Orange (#ff6600)

---

### 2. Moving Averages (MA)

**Purpose**: Identify trend direction and support/resistance levels.

**Calculation**:
```
MA = Sum of closing prices over N periods / N
```

**Parameters**:
- MA20: 20-period simple moving average
- MA60: 60-period simple moving average

**Interpretation**:
- **Price > MA**: Uptrend
- **Price < MA**: Downtrend
- **MA20 > MA60**: Bull trend
- **MA20 < MA60**: Bear trend

**Chart Display**:
- Overlaid on price chart
- MA20: Yellow-orange (#ffaa00), dashed
- MA60: Orange (#ff6600), dashed

---

### 3. Exponential Moving Averages (EMA)

**Purpose**: Trend identification with more weight on recent prices.

**Calculation**:
```
EMA = Price(t) × k + EMA(y) × (1 − k)
where k = 2 / (N + 1)
```

**Parameters**:
- EMA20: 20-period exponential moving average
- EMA60: 60-period exponential moving average

**Interpretation**:
- Similar to MA but more responsive to recent price changes
- Used in the main trading strategy

**Chart Display**:
- Overlaid on price chart
- EMA20: Cyan (#00d4ff), dashed
- EMA60: Magenta (#ff00ff), dashed

---

### 4. MACD (Moving Average Convergence Divergence)

**Purpose**: Trend-following momentum indicator.

**Calculation**:
```
MACD Line = 12-EMA - 26-EMA
Signal Line = 9-EMA of MACD
Histogram = MACD - Signal
```

**Parameters**:
- Fast EMA: 12
- Slow EMA: 26
- Signal: 9

**Interpretation**:
- **MACD crosses above Signal**: Bullish signal
- **MACD crosses below Signal**: Bearish signal
- **Histogram growing**: Trend strengthening
- **Histogram shrinking**: Trend weakening

**Chart Display**:
- Separate chart with 3 components
- MACD: Cyan (#00d4ff), line
- Signal: Magenta (#ff00ff), line
- Histogram: Green (#00ff41), bars

---

### 5. RSI (Relative Strength Index)

**Purpose**: Measure the speed and magnitude of price changes.

**Calculation**:
```
RSI = 100 - (100 / (1 + RS))
where RS = Average Gain / Average Loss over N periods
```

**Parameters**:
- Period: 14
- Range: 0 to 100

**Interpretation**:
- **RSI > 70**: Overbought (potential sell signal)
- **RSI < 30**: Oversold (potential buy signal)
- **30-70**: Normal range
- **RSI divergence**: Potential trend reversal

**Chart Display**:
- Line chart with 30 and 70 reference lines
- Color: Green (#00ff41)
- Overbought line (70): Red
- Oversold line (30): Green

---

### 6. Volume

**Purpose**: Confirm price movements and identify trend strength.

**Display**:
```
Green bars: Close >= Open (bullish)
Red bars: Close < Open (bearish)
```

**Interpretation**:
- **High volume + price up**: Strong bullish momentum
- **High volume + price down**: Strong bearish momentum
- **Low volume**: Weak trend or consolidation

**Chart Display**:
- Bar chart below price chart
- Green bars: rgba(0, 255, 0, 0.7)
- Red bars: rgba(255, 0, 0, 0.7)

---

## Multi-Timeframe Support

All indicators are calculated for 7 different timeframes:

| Timeframe | Description | Best For |
|-----------|-------------|----------|
| 1m | 1 minute | Scalping, very short-term |
| 5m | 5 minutes | Short-term trading |
| 15m | 15 minutes | Intraday trading |
| 30m | 30 minutes | Intraday/swing |
| 1h | 1 hour | Swing trading (default) |
| 4h | 4 hours | Position trading |
| 1d | 1 day | Long-term trends |

**Switching Timeframes**:
- Click any timeframe button on the dashboard
- All charts and indicators update automatically
- Data is cached in Redis for fast switching

---

## Redis Caching Strategy

All indicator calculations use Redis-cached MEXC API data:

**Cache TTL**:
- OHLCV data: 60 seconds
- Chart data: Automatically cached with OHLCV
- Indicators: Calculated on-demand from cached OHLCV

**Performance**:
- First load: 200-500ms (MEXC API call + calculation)
- Subsequent loads: < 150ms (Redis cache)
- Automatic refresh: Every 60 seconds

---

## API Endpoints

### Chart Data Endpoint

```
GET /api/market/chart-data?timeframe=1h
```

**Response**:
```json
{
  "timeframe": "1h",
  "labels": ["12-26 10:00", "12-26 11:00", ...],
  "prices": [0.45, 0.46, ...],
  "open": [0.44, 0.45, ...],
  "high": [0.46, 0.47, ...],
  "low": [0.44, 0.45, ...],
  "volumes": [1000000, 1200000, ...],
  "volume_colors": ["rgba(0, 255, 0, 0.7)", ...],
  "ema20": [0.45, 0.455, ...],
  "ema60": [0.44, 0.445, ...],
  "ma20": [0.45, 0.453, ...],
  "ma60": [0.44, 0.443, ...]
}
```

### Indicators Endpoint

```
GET /api/market/indicators?timeframe=1h
```

**Response**:
```json
{
  "timeframe": "1h",
  "labels": ["12-26 10:00", "12-26 11:00", ...],
  "williams_r": [-45.2, -38.5, ...],
  "macd": [0.001, 0.0015, ...],
  "macd_signal": [0.0012, 0.0014, ...],
  "macd_histogram": [-0.0002, 0.0001, ...],
  "rsi": [55.3, 58.7, ...],
  "ma20": [0.45, 0.453, ...],
  "ma60": [0.44, 0.443, ...],
  "volumes": [1000000, 1200000, ...],
  "volume_colors": ["rgba(0, 255, 0, 0.7)", ...]
}
```

---

## Usage in Trading Strategy

### Current EMA Strategy

The bot currently uses EMA20 and EMA60 for trading decisions:

```python
# Buy Signal
if price <= ema60 * 1.02 and ema20 > ema60:
    # Price near EMA60 and upward momentum
    execute_buy()
```

### Potential Enhancements

**Using RSI**:
```python
if rsi < 30 and ema20 > ema60:
    # Oversold + uptrend
    strong_buy_signal = True
```

**Using MACD**:
```python
if macd > macd_signal and macd_histogram > 0:
    # MACD bullish crossover
    confirm_buy = True
```

**Using Williams %R**:
```python
if williams_r < -80:
    # Oversold condition
    potential_reversal = True
```

---

## Chart Display Features

### Interactive Features

- **Hover tooltips**: Exact values for all indicators
- **Zoom**: Mouse wheel or pinch on touch devices
- **Pan**: Drag to move along timeline
- **Legend**: Click to show/hide individual indicators
- **Auto-refresh**: Every 60 seconds

### Visual Design

- **Terminal-style**: Consistent with dashboard theme
- **Color coding**:
  - Green: Bullish/Buy signals
  - Red: Bearish/Sell signals
  - Cyan/Magenta: Neutral indicators
  - Orange: Momentum indicators
- **Reference lines**: Clear overbought/oversold zones
- **Responsive**: Adapts to screen size

---

## Best Practices

### Indicator Combinations

1. **Trend Confirmation**:
   - MA/EMA + MACD
   - Confirm trend direction with multiple indicators

2. **Entry Timing**:
   - Williams %R + RSI
   - Find optimal entry points

3. **Exit Strategy**:
   - MACD divergence + Volume
   - Identify weakening trends

### Timeframe Analysis

1. **Higher timeframe** (4h/1d): Identify overall trend
2. **Medium timeframe** (1h): Find entry setup
3. **Lower timeframe** (15m/30m): Fine-tune entry timing

### Avoiding False Signals

- **Don't rely on single indicator**: Use 2-3 for confirmation
- **Consider volume**: Low volume signals are less reliable
- **Check higher timeframes**: Confirm with longer-term trend
- **Wait for candle close**: Avoid signals mid-candle

---

## Technical Implementation

### Calculation Libraries

- **Pandas**: Data manipulation and rolling calculations
- **NumPy**: Efficient numerical operations (via pandas)
- **Native Python**: Custom indicator logic

### Performance Optimization

1. **Server-side calculation**: All indicators calculated in Python backend
2. **Redis caching**: OHLCV data cached for 60s
3. **Efficient algorithms**: Vectorized operations with pandas
4. **On-demand loading**: Indicators only calculated when requested

### Code Example

```python
import pandas as pd

# Calculate Williams %R
period = 14
df['highest_high'] = df['high'].rolling(window=period).max()
df['lowest_low'] = df['low'].rolling(window=period).min()
df['williams_r'] = ((df['highest_high'] - df['close']) / 
                   (df['highest_high'] - df['lowest_low'])) * -100

# Calculate RSI
delta = df['close'].diff()
gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
rs = gain / loss
df['rsi'] = 100 - (100 / (1 + rs))
```

---

## Troubleshooting

### Charts Not Loading

1. **Check Redis connection**: Verify `REDIS_URL` in `.env`
2. **Check API endpoints**: Visit `/api/market/indicators?timeframe=1h`
3. **Check browser console**: Look for JavaScript errors

### Indicator Values Seem Wrong

1. **Wait for full period**: Some indicators need N periods to stabilize
2. **Check timeframe**: Ensure correct timeframe is selected
3. **Verify data**: Check `/api/market/chart-data` for raw OHLCV

### Performance Issues

1. **Enable Redis**: Dramatically improves load times
2. **Lower timeframe**: Use 1h or higher for better performance
3. **Clear browser cache**: Force reload chart JavaScript

---

## Future Enhancements

Potential additions:

1. **Bollinger Bands**: Volatility indicator
2. **Stochastic Oscillator**: Additional momentum indicator
3. **ATR (Average True Range)**: Volatility measure
4. **Fibonacci Retracements**: Support/resistance levels
5. **Candlestick patterns**: Pattern recognition
6. **Volume Profile**: Volume-based support/resistance

---

## References

- [Williams %R - Investopedia](https://www.investopedia.com/terms/w/williamsr.asp)
- [MACD - Investopedia](https://www.investopedia.com/terms/m/macd.asp)
- [RSI - Investopedia](https://www.investopedia.com/terms/r/rsi.asp)
- [Moving Averages - Investopedia](https://www.investopedia.com/terms/m/movingaverage.asp)
- [MEXC API Documentation](https://mexcdevelop.github.io/apidocs/spot_v2_en/)

---

**Version**: 2.0.0
**Last Updated**: 2025-12-26
**Cache Strategy**: Redis with 60s TTL
**Data Source**: MEXC API via CCXT
