# 交易機器人策略討論

## 📋 目錄

1. [當前策略分析](#當前策略分析)
2. [策略改進方向](#策略改進方向)
3. [定時觸發策略](#定時觸發策略)
4. [多時段執行策略](#多時段執行策略)
5. [風險管理優化](#風險管理優化)

## 當前策略分析

### EMA 累積策略 (EMA Accumulation Strategy)

**策略邏輯**:
```python
買入條件（同時滿足）:
1. 價格接近支撐: 當前價格 ≤ EMA60 × 1.02
2. 正向動能: EMA20 ≥ EMA60
```

**優點**:
- ✅ 低風險買入：在支撐位附近進場
- ✅ 趨勢確認：確保處於上升趨勢
- ✅ 簡單可靠：邏輯清晰，易於理解和維護

**限制**:
- ⚠️ 單次執行：每次只判斷一次，可能錯過機會
- ⚠️ 固定參數：EMA20/60 參數固定，缺乏靈活性
- ⚠️ 無賣出邏輯：只累積，無獲利了結機制

## 策略改進方向

### 1. 多時段檢查策略

利用 Cloud Scheduler 免費額度（3 個作業），在不同時段檢查市場：

```yaml
時段配置:
  早上檢查 (6:00 AM):
    - 目的: 捕捉亞洲市場開盤機會
    - 策略: 標準 EMA 策略
    
  中午檢查 (12:00 PM):
    - 目的: 捕捉歐洲市場開盤機會
    - 策略: 標準 EMA 策略
    
  傍晚檢查 (6:00 PM):
    - 目的: 捕捉美國市場開盤機會
    - 策略: 標準 EMA 策略
```

**優勢**:
- ✅ 增加買入機會：每日 3 次檢查 vs 1 次
- ✅ 覆蓋全球市場：亞洲、歐洲、美國時段
- ✅ 免費執行：充分利用 Cloud Scheduler 免費額度

### 2. 時段特定策略

根據不同時段的市場特性，調整策略參數：

```python
# 示例：時段感知策略
class TimeAwareEMAStrategy(BaseStrategy):
    def analyze(self, ohlcv: pd.DataFrame) -> Signal:
        current_hour = datetime.now(timezone.utc).hour
        
        # 亞洲時段 (UTC 0-8): 較保守
        if 0 <= current_hour < 8:
            ema_multiplier = 1.015  # 更嚴格的支撐條件
        
        # 歐洲時段 (UTC 8-16): 標準
        elif 8 <= current_hour < 16:
            ema_multiplier = 1.02   # 標準條件
        
        # 美國時段 (UTC 16-24): 較積極
        else:
            ema_multiplier = 1.025  # 更寬鬆的條件
        
        # 應用策略邏輯...
```

### 3. 累積速率控制

防止過度集中買入，實現平穩累積：

```python
class RateLimitedStrategy(BaseStrategy):
    def __init__(self, min_hours_between_buys: int = 4):
        self.min_hours_between_buys = min_hours_between_buys
    
    def can_buy(self, last_trade_time: datetime) -> bool:
        """檢查是否滿足最小間隔時間"""
        if not last_trade_time:
            return True
        
        hours_since_last = (datetime.now() - last_trade_time).total_seconds() / 3600
        return hours_since_last >= self.min_hours_between_buys
```

## 定時觸發策略

### 推薦配置

#### 配置 A: 保守型（每日 1 次）

```bash
# 每日上午 9:00 執行
gcloud scheduler jobs create http qrl-trading-daily \
  --schedule="0 9 * * *" \
  --time-zone="Asia/Taipei"
```

**適用場景**:
- 長期累積
- 低風險偏好
- 最小化執行成本

#### 配置 B: 平衡型（每日 3 次）- **推薦**

```bash
# 早上 6:00
gcloud scheduler jobs create http qrl-trading-morning \
  --schedule="0 6 * * *" \
  --time-zone="Asia/Taipei"

# 中午 12:00
gcloud scheduler jobs create http qrl-trading-noon \
  --schedule="0 12 * * *" \
  --time-zone="Asia/Taipei"

# 傍晚 18:00
gcloud scheduler jobs create http qrl-trading-evening \
  --schedule="0 18 * * *" \
  --time-zone="Asia/Taipei"
```

**適用場景**:
- 捕捉多個時段機會
- 利用免費額度
- 平衡執行頻率和成本

#### 配置 C: 積極型（工作日多次）

```bash
# 工作日每 4 小時執行一次
gcloud scheduler jobs create http qrl-trading-regular \
  --schedule="0 */4 * * 1-5" \
  --time-zone="Asia/Taipei"
```

**適用場景**:
- 高頻買入需求
- 快速累積目標
- 注意：超過 3 個作業需付費

## 多時段執行策略

### 策略 1: 全時段平均累積

**目標**: 在所有時段均勻買入，降低時機風險

```yaml
配置:
  早上 (6:00):  BASE_ORDER_USDT=1.5
  中午 (12:00): BASE_ORDER_USDT=1.5
  傍晚 (18:00): BASE_ORDER_USDT=1.5
  
優勢:
  - 分散時間風險
  - 平滑成本基礎
  - 避免集中在單一時段
```

### 策略 2: 波動性感知執行

**目標**: 在高波動時段減少買入量，低波動時段增加

```python
# 示例實作
class VolatilityAwareStrategy(BaseStrategy):
    def calculate_order_size(self, volatility: float, base_order: float) -> float:
        """根據波動率調整訂單大小"""
        if volatility > 0.05:  # 高波動
            return base_order * 0.5
        elif volatility < 0.02:  # 低波動
            return base_order * 1.5
        else:
            return base_order
```

### 策略 3: 市場時段權重

**目標**: 根據歷史表現，在不同時段使用不同權重

```yaml
時段權重:
  亞洲時段 (6:00):  權重 1.0, 訂單 1.5 USDT
  歐洲時段 (12:00): 權重 1.2, 訂單 1.8 USDT
  美國時段 (18:00): 權重 0.8, 訂單 1.2 USDT

調整依據:
  - 歷史回測數據
  - 時段成交量
  - 價格波動特性
```

## 風險管理優化

### 1. 動態持倉限制

根據市場狀況動態調整最大持倉：

```python
class DynamicRiskManager:
    def calculate_max_position(self, market_conditions: dict) -> float:
        base_max = 500.0  # 基礎最大持倉
        
        # 根據市場狀況調整
        if market_conditions['trend'] == 'strong_uptrend':
            return base_max * 1.2  # 600 USDT
        elif market_conditions['trend'] == 'downtrend':
            return base_max * 0.8  # 400 USDT
        else:
            return base_max
```

### 2. 訂單大小階梯

根據當前持倉比例調整訂單大小：

```python
def calculate_scaled_order_size(current_position: float, max_position: float, base_order: float) -> float:
    """階梯式調整訂單大小"""
    utilization = current_position / max_position
    
    if utilization < 0.3:  # 前 30%
        return base_order * 1.5  # 較大訂單
    elif utilization < 0.7:  # 30-70%
        return base_order  # 標準訂單
    else:  # 70%+
        return base_order * 0.5  # 較小訂單
```

### 3. 時間分散風險

避免在短時間內集中買入：

```python
class TimeSpreadRiskManager:
    def __init__(self, min_interval_hours: int = 4):
        self.min_interval_hours = min_interval_hours
        self.last_trade_times = []
    
    def should_skip_trade(self) -> bool:
        """檢查是否應該跳過本次交易"""
        if not self.last_trade_times:
            return False
        
        recent_trades = [
            t for t in self.last_trade_times
            if (datetime.now() - t).total_seconds() < 86400  # 24 hours
        ]
        
        # 如果 24 小時內已有 3 筆交易，跳過
        return len(recent_trades) >= 3
```

## 實作建議

### Phase 1: 基礎多時段執行（當前實作）

1. ✅ 部署 Cloud Run Job
2. ✅ 設定 3 個 Cloud Scheduler 作業（利用免費額度）
3. ✅ 使用現有 EMA 策略
4. ✅ 監控執行結果

### Phase 2: 策略優化（未來擴展）

1. 實作時段感知策略
2. 加入波動性分析
3. 動態調整訂單大小
4. 優化進場條件

### Phase 3: 高級功能（可選）

1. 賣出邏輯實作
2. 多策略並行
3. 機器學習預測
4. 自動參數優化

## 監控和調整

### 關鍵指標

```yaml
監控指標:
  執行指標:
    - 每日執行次數
    - 實際買入次數
    - 執行成功率
  
  策略指標:
    - 平均買入價格
    - 持倉累積速度
    - 策略觸發頻率
  
  風險指標:
    - 持倉利用率
    - 最大持倉接近度
    - 買入時間分布
```

### 定期檢視

- **每日**: 檢查執行日誌，確認正常運作
- **每週**: 分析買入記錄，評估策略效果
- **每月**: 回測策略表現，調整參數

## 結論

### 推薦配置（當前階段）

```yaml
部署模式: Cloud Scheduler + Cloud Run Jobs
執行頻率: 每日 3 次（利用免費額度）
執行時段: 6:00, 12:00, 18:00 (Asia/Taipei)
策略: EMA 累積策略（現有實作）
訂單大小: 1.5 USDT
最大持倉: 2.0 USDT（測試環境）
```

### 優勢

1. ✅ **成本效益**: 利用免費額度，月成本約 NT$2
2. ✅ **簡單可靠**: 使用現有策略，無需額外開發
3. ✅ **易於管理**: 純 Google Cloud 服務，無需維護腳本
4. ✅ **風險可控**: 多時段執行，分散時間風險
5. ✅ **可擴展**: 未來可輕鬆調整策略和參數

### 下一步

1. 部署 Cloud Run Job 和 Cloud Scheduler
2. 運行 1-2 週，收集執行數據
3. 分析結果，評估是否需要調整
4. 根據表現，考慮實作進階策略

---

**注意**: 本文檔為策略討論和規劃，實際實作應根據市場狀況和個人風險承受能力調整。
