# QRL Trading Bot 2.0 - 優化路線圖 / Optimization Roadmap

## 🎯 版本定位 / Version Positioning

**當前版本 (1.0)**: 基礎 EMA 策略交易機器人，單幣對買入策略
**目標版本 (2.0)**: 完整的交易系統，支援買賣策略、多幣對、風險控制、性能監控

---

## 📋 優化建議清單 / Optimization List

### 🔴 核心功能優化 / Core Functionality (Priority: HIGH)

#### 1. 完整交易循環 - 實作賣出策略
**當前狀態**: 只有買入邏輯，沒有賣出策略
**優化內容**:
- [ ] 實作賣出信號邏輯 (基於 EMA 或利潤目標)
- [ ] 止損機制 (Stop Loss)
- [ ] 止盈機制 (Take Profit)
- [ ] 追蹤止損 (Trailing Stop)

**實作建議**:
```python
# strategy.py 新增
def should_sell(ohlcv: list, entry_price: float, profit_target: float = 0.05) -> tuple[bool, str]:
    """
    判斷賣出條件
    
    返回: (是否賣出, 原因)
    - 利潤目標達成: price >= entry_price * (1 + profit_target)
    - EMA 死亡交叉: EMA20 < EMA60
    - 止損: price <= entry_price * 0.95
    """
    pass
```

**預期效益**:
- ✅ 實現完整交易閉環
- ✅ 自動獲利了結
- ✅ 控制虧損風險

---

#### 2. 訂單管理系統
**當前狀態**: 簡單的限價單，沒有訂單追蹤
**優化內容**:
- [ ] 訂單狀態追蹤 (pending, filled, cancelled)
- [ ] 未成交訂單自動取消機制
- [ ] 訂單重試邏輯
- [ ] 部分成交處理

**實作建議**:
```python
# orders.py (新模組)
class OrderManager:
    def create_order(self, side, amount, price)
    def get_order_status(self, order_id)
    def cancel_order(self, order_id)
    def get_open_orders()
    def cancel_stale_orders(max_age_hours=24)
```

**資料庫設計**:
```sql
CREATE TABLE orders (
    id INTEGER PRIMARY KEY,
    order_id TEXT UNIQUE,
    symbol TEXT,
    side TEXT,  -- 'buy' or 'sell'
    type TEXT,  -- 'limit', 'market'
    amount REAL,
    price REAL,
    status TEXT,  -- 'pending', 'filled', 'cancelled'
    created_at TIMESTAMP,
    filled_at TIMESTAMP,
    profit_usdt REAL  -- 實現利潤 (僅賣出訂單)
);
```

**預期效益**:
- ✅ 完整的訂單歷史記錄
- ✅ 避免掛單堆積
- ✅ 交易分析數據來源

---

#### 3. 持倉管理系統
**當前狀態**: 只記錄 USDT 總投入，沒有詳細持倉信息
**優化內容**:
- [ ] 記錄每筆買入的數量和價格
- [ ] 計算平均成本
- [ ] 追蹤未實現盈虧
- [ ] 支援 FIFO/LIFO 會計方法

**實作建議**:
```python
# positions.py (新模組)
class PositionManager:
    def add_buy(self, amount, price, timestamp)
    def add_sell(self, amount, price, timestamp)
    def get_average_cost()
    def get_total_quantity()
    def get_unrealized_pnl(current_price)
    def get_realized_pnl()
```

**資料庫設計**:
```sql
CREATE TABLE positions (
    id INTEGER PRIMARY KEY,
    symbol TEXT,
    quantity REAL,  -- QRL 數量
    avg_cost REAL,  -- 平均成本
    total_invested REAL,  -- 總投入 USDT
    realized_pnl REAL,  -- 已實現盈虧
    updated_at TIMESTAMP
);

CREATE TABLE transactions (
    id INTEGER PRIMARY KEY,
    order_id TEXT,
    symbol TEXT,
    side TEXT,
    quantity REAL,
    price REAL,
    fee REAL,
    timestamp TIMESTAMP
);
```

**預期效益**:
- ✅ 準確的成本計算
- ✅ 實時盈虧追蹤
- ✅ 交易績效分析

---

### 🟡 風險控制優化 / Risk Management (Priority: HIGH)

#### 4. 高級風險管理
**當前狀態**: 只有簡單的倉位上限檢查
**優化內容**:
- [ ] 單日最大虧損限制 (Daily Loss Limit)
- [ ] 單筆交易風險限制
- [ ] 連續虧損保護 (Circuit Breaker)
- [ ] 最大回撤控制
- [ ] 波動率適應性調整

**實作建議**:
```python
# risk_manager.py (擴展現有 risk.py)
class AdvancedRiskManager:
    def check_daily_loss_limit(self, current_loss, max_daily_loss=100)
    def check_consecutive_losses(self, loss_count, max_losses=3)
    def check_drawdown(self, current_dd, max_dd=0.15)
    def adjust_position_size_by_volatility(self, volatility)
    def should_pause_trading(self) -> tuple[bool, str]
```

**配置參數**:
```python
# config.py 新增
MAX_DAILY_LOSS_USDT = 100        # 單日最大虧損
MAX_CONSECUTIVE_LOSSES = 3       # 最大連續虧損次數
MAX_DRAWDOWN_PERCENT = 15        # 最大回撤 15%
VOLATILITY_ADJUSTMENT = True     # 根據波動率調整倉位
CIRCUIT_BREAKER_COOLDOWN = 3600  # 熔斷冷卻時間(秒)
```

**預期效益**:
- ✅ 防止單日巨額虧損
- ✅ 自動暫停異常交易
- ✅ 動態風險調整

---

#### 5. 資金管理系統
**當前狀態**: 固定訂單金額 (50 USDT)
**優化內容**:
- [ ] 動態倉位調整 (根據信號強度)
- [ ] 凱利公式倉位計算
- [ ] 金字塔加倉策略
- [ ] 分批建倉/離場

**實作建議**:
```python
# position_sizing.py (新模組)
class PositionSizer:
    def kelly_criterion(self, win_rate, avg_win, avg_loss)
    def fixed_fractional(self, capital, risk_percent=0.02)
    def pyramid_sizing(self, entry_num, initial_size)
    def scale_in_plan(self, total_amount, num_orders)
    def scale_out_plan(self, total_quantity, profit_levels)
```

**預期效益**:
- ✅ 優化資金使用效率
- ✅ 降低單次風險暴露
- ✅ 更靈活的進出場策略

---

### 🟢 策略與指標優化 / Strategy & Indicators (Priority: MEDIUM)

#### 6. 多策略支援
**當前狀態**: 單一 EMA 交叉策略
**優化內容**:
- [ ] 策略插件化架構
- [ ] 多策略並行運行
- [ ] 策略性能評估
- [ ] A/B 測試框架

**實作建議**:
```python
# strategies/ 目錄結構
strategies/
  ├── __init__.py
  ├── base.py          # 策略基類
  ├── ema_cross.py     # 現有 EMA 策略
  ├── rsi_strategy.py  # RSI 超買超賣策略
  ├── macd_strategy.py # MACD 策略
  ├── bbands_strategy.py # 布林帶策略
  └── multi_strategy.py  # 多策略組合

# base.py
class BaseStrategy:
    def should_buy(self, ohlcv) -> tuple[bool, float]:
        """返回: (是否買入, 信號強度 0-1)"""
        pass
    
    def should_sell(self, ohlcv, position) -> tuple[bool, str]:
        """返回: (是否賣出, 原因)"""
        pass
    
    def get_metrics(self) -> dict:
        """返回策略性能指標"""
        pass
```

**策略範例 - RSI**:
```python
def should_buy_rsi(ohlcv: list) -> bool:
    """
    RSI 超賣策略
    - RSI < 30: 超賣，買入信號
    - RSI > 70: 超買，避免買入
    """
    df = pd.DataFrame(ohlcv, columns=["ts", "open", "high", "low", "close", "vol"])
    rsi = RSIIndicator(df["close"], window=14).rsi()
    return rsi.iloc[-1] < 30
```

**預期效益**:
- ✅ 策略多樣化降低風險
- ✅ 適應不同市場環境
- ✅ 可測試新策略想法

---

#### 7. 技術指標擴充
**當前狀態**: 僅使用 EMA20/EMA60
**優化內容**:
- [ ] RSI (相對強弱指標)
- [ ] MACD (移動平均收斂發散指標)
- [ ] 布林帶 (Bollinger Bands)
- [ ] 成交量指標 (Volume Profile)
- [ ] ATR (真實波動幅度) - 用於止損設定

**實作建議**:
```python
# indicators.py (新模組)
from ta.momentum import RSIIndicator
from ta.trend import MACD
from ta.volatility import BollingerBands, AverageTrueRange

class TechnicalIndicators:
    @staticmethod
    def calculate_all(df):
        """計算所有指標"""
        indicators = {}
        
        # 趨勢指標
        indicators['ema20'] = EMAIndicator(df['close'], 20).ema_indicator()
        indicators['ema60'] = EMAIndicator(df['close'], 60).ema_indicator()
        
        # 動量指標
        indicators['rsi'] = RSIIndicator(df['close'], 14).rsi()
        
        # MACD
        macd = MACD(df['close'])
        indicators['macd'] = macd.macd()
        indicators['macd_signal'] = macd.macd_signal()
        
        # 波動率指標
        bb = BollingerBands(df['close'])
        indicators['bb_upper'] = bb.bollinger_hband()
        indicators['bb_lower'] = bb.bollinger_lband()
        
        # ATR (用於動態止損)
        indicators['atr'] = AverageTrueRange(df['high'], df['low'], df['close']).average_true_range()
        
        return indicators
```

**預期效益**:
- ✅ 更全面的市場分析
- ✅ 多維度確認信號
- ✅ 動態止損設定

---

### 🔵 多幣對與擴展性 / Multi-Pair & Scalability (Priority: MEDIUM)

#### 8. 多幣對交易支援
**當前狀態**: 僅支援 QRL/USDT
**優化內容**:
- [ ] 配置多個交易對
- [ ] 獨立的倉位管理
- [ ] 資金分配策略
- [ ] 相關性分析

**實作建議**:
```python
# config.py
TRADING_PAIRS = [
    {
        "symbol": "QRL/USDT",
        "base_order": 50,
        "max_position": 500,
        "strategy": "ema_cross",
        "enabled": True
    },
    {
        "symbol": "BTC/USDT",
        "base_order": 100,
        "max_position": 1000,
        "strategy": "rsi_strategy",
        "enabled": True
    }
]

# main.py 重構
def trade_all_pairs():
    for pair_config in TRADING_PAIRS:
        if not pair_config["enabled"]:
            continue
        
        strategy = get_strategy(pair_config["strategy"])
        execute_strategy(pair_config, strategy)
```

**預期效益**:
- ✅ 分散投資風險
- ✅ 捕捉更多機會
- ✅ 提高資金使用率

---

#### 9. 性能優化與擴展
**當前狀態**: 同步單線程執行
**優化內容**:
- [ ] 異步 API 調用
- [ ] 數據緩存機制
- [ ] 並行處理多幣對
- [ ] 資料庫連接池

**實作建議**:
```python
# async_trader.py
import asyncio
import aiohttp

class AsyncTrader:
    async def fetch_all_tickers(self, symbols):
        """並行獲取多個幣對價格"""
        tasks = [self.fetch_ticker(symbol) for symbol in symbols]
        return await asyncio.gather(*tasks)
    
    async def process_all_pairs(self):
        """並行處理所有交易對"""
        tasks = [self.process_pair(config) for config in TRADING_PAIRS]
        await asyncio.gather(*tasks)
```

**預期效益**:
- ✅ 降低 API 延遲
- ✅ 提高處理速度
- ✅ 支援更多幣對

---

### 🟣 監控與通知 / Monitoring & Notifications (Priority: MEDIUM)

#### 10. 通知系統
**當前狀態**: 僅終端輸出，無外部通知
**優化內容**:
- [ ] Telegram 機器人通知
- [ ] Email 報告
- [ ] 交易信號推送
- [ ] 異常告警

**實作建議**:
```python
# notifications.py
import requests

class NotificationManager:
    def __init__(self):
        self.telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    def send_trade_alert(self, action, symbol, price, quantity):
        """發送交易通知"""
        message = f"""
🤖 QRL Trading Bot

{action.upper()} Signal
Symbol: {symbol}
Price: {price}
Quantity: {quantity}
Time: {datetime.now()}
        """
        self._send_telegram(message)
    
    def send_error_alert(self, error_msg):
        """發送錯誤告警"""
        pass
    
    def send_daily_report(self, stats):
        """發送每日報告"""
        pass
```

**通知類型**:
- 🟢 買入信號觸發
- 🔴 賣出信號觸發
- ⚠️ 風險告警 (達到止損、倉位上限等)
- 📊 每日交易總結
- ❌ 系統錯誤告警

**預期效益**:
- ✅ 實時掌握交易狀態
- ✅ 快速響應異常
- ✅ 定期績效回顧

---

#### 11. 性能追蹤與分析
**當前狀態**: 無交易性能統計
**優化內容**:
- [ ] 勝率統計
- [ ] 盈虧比計算
- [ ] 最大回撤追蹤
- [ ] 夏普比率
- [ ] 交易日誌

**實作建議**:
```python
# analytics.py
class PerformanceAnalytics:
    def calculate_win_rate(self):
        """計算勝率"""
        pass
    
    def calculate_profit_factor(self):
        """計算盈虧比"""
        pass
    
    def calculate_max_drawdown(self):
        """計算最大回撤"""
        pass
    
    def calculate_sharpe_ratio(self, risk_free_rate=0.02):
        """計算夏普比率"""
        pass
    
    def generate_report(self, start_date, end_date):
        """生成績效報告"""
        return {
            "total_trades": 0,
            "win_rate": 0.0,
            "profit_factor": 0.0,
            "max_drawdown": 0.0,
            "sharpe_ratio": 0.0,
            "total_pnl": 0.0
        }
```

**儀表板集成**:
在 web/app.py 新增績效頁面，顯示:
- 📈 累計收益曲線
- 📊 交易統計圖表
- 🎯 策略性能對比
- 📅 歷史交易記錄

**預期效益**:
- ✅ 量化策略效果
- ✅ 識別改進空間
- ✅ 數據驅動優化

---

### 🟠 回測與測試 / Backtesting & Testing (Priority: LOW-MEDIUM)

#### 12. 回測系統
**當前狀態**: 無回測能力
**優化內容**:
- [ ] 歷史數據回測
- [ ] 策略參數優化
- [ ] 模擬交易環境
- [ ] 回測報告生成

**實作建議**:
```python
# backtesting.py
class Backtester:
    def __init__(self, strategy, start_date, end_date):
        self.strategy = strategy
        self.start_date = start_date
        self.end_date = end_date
    
    def run(self, initial_capital=1000):
        """執行回測"""
        # 獲取歷史數據
        # 模擬逐日交易
        # 記錄每筆交易
        # 計算績效指標
        pass
    
    def optimize_parameters(self, param_grid):
        """參數優化"""
        # 網格搜索最佳參數
        pass
    
    def generate_report(self):
        """生成回測報告"""
        return {
            "start_date": self.start_date,
            "end_date": self.end_date,
            "initial_capital": 1000,
            "final_capital": 1500,
            "total_return": 50.0,
            "max_drawdown": -10.5,
            "sharpe_ratio": 1.8,
            "total_trades": 45,
            "win_rate": 62.2
        }
```

**預期效益**:
- ✅ 驗證策略有效性
- ✅ 優化策略參數
- ✅ 降低實盤風險

---

#### 13. 單元測試與集成測試
**當前狀態**: 無測試代碼
**優化內容**:
- [ ] 核心模組單元測試
- [ ] 策略邏輯測試
- [ ] 模擬交易測試
- [ ] CI/CD 集成

**實作建議**:
```python
# tests/test_strategy.py
import pytest

def test_should_buy_ema_cross():
    """測試 EMA 買入邏輯"""
    # 構造測試數據
    ohlcv = create_test_ohlcv(ema20_above_ema60=True, price_near_ema60=True)
    
    # 執行測試
    result = should_buy(ohlcv)
    
    # 驗證結果
    assert result == True

def test_risk_management():
    """測試風險控制"""
    assert can_buy(450, 500) == True
    assert can_buy(500, 500) == False
```

**測試覆蓋目標**:
- Strategy: 90%+
- Risk Management: 100%
- Order Management: 85%+
- Position Management: 90%+

**預期效益**:
- ✅ 提高代碼質量
- ✅ 防止回歸錯誤
- ✅ 安全重構

---

### ⚪ 基礎設施優化 / Infrastructure (Priority: LOW)

#### 14. 配置管理增強
**當前狀態**: 簡單的 .env 配置
**優化內容**:
- [ ] 配置驗證
- [ ] 環境分離 (dev/staging/prod)
- [ ] 配置熱重載
- [ ] 敏感信息加密

**實作建議**:
```python
# config_manager.py
from pydantic import BaseModel, validator

class TradingConfig(BaseModel):
    symbol: str
    base_order_usdt: float
    max_position_usdt: float
    price_offset: float
    
    @validator('base_order_usdt')
    def validate_order_size(cls, v):
        if v <= 0 or v > 10000:
            raise ValueError('Order size must be between 0 and 10000')
        return v
    
    @validator('price_offset')
    def validate_offset(cls, v):
        if v < 0.9 or v > 1.1:
            raise ValueError('Price offset must be between 0.9 and 1.1')
        return v

# 使用
config = TradingConfig.parse_obj({
    "symbol": "QRL/USDT",
    "base_order_usdt": 50,
    "max_position_usdt": 500,
    "price_offset": 0.98
})
```

**預期效益**:
- ✅ 防止配置錯誤
- ✅ 環境隔離
- ✅ 提高安全性

---

#### 15. 日誌系統
**當前狀態**: print() 輸出
**優化內容**:
- [ ] 結構化日誌
- [ ] 日誌級別管理
- [ ] 日誌文件輪轉
- [ ] 集中式日誌查詢

**實作建議**:
```python
# logger.py
import logging
from logging.handlers import RotatingFileHandler

def setup_logger(name, level=logging.INFO):
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # 文件處理器
    file_handler = RotatingFileHandler(
        f'logs/{name}.log',
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    ))
    
    logger.addHandler(file_handler)
    return logger

# 使用
logger = setup_logger('trading')
logger.info(f"買入信號觸發: {symbol} @ {price}")
logger.warning(f"接近倉位上限: {position}/{max_position}")
logger.error(f"API 錯誤: {error}")
```

**預期效益**:
- ✅ 問題追溯
- ✅ 性能分析
- ✅ 合規審計

---

#### 16. 資料庫優化
**當前狀態**: 簡單的 SQLite 單表
**優化內容**:
- [ ] 多表關聯設計
- [ ] 索引優化
- [ ] 定期備份
- [ ] 數據遷移工具

**資料庫架構**:
```sql
-- 交易對配置
CREATE TABLE symbols (
    id INTEGER PRIMARY KEY,
    symbol TEXT UNIQUE NOT NULL,
    base_order REAL,
    max_position REAL,
    enabled BOOLEAN,
    strategy TEXT
);

-- 訂單表
CREATE TABLE orders (
    id INTEGER PRIMARY KEY,
    order_id TEXT UNIQUE,
    symbol_id INTEGER,
    side TEXT,
    type TEXT,
    amount REAL,
    price REAL,
    status TEXT,
    created_at TIMESTAMP,
    filled_at TIMESTAMP,
    FOREIGN KEY (symbol_id) REFERENCES symbols(id)
);

-- 持倉表
CREATE TABLE positions (
    id INTEGER PRIMARY KEY,
    symbol_id INTEGER,
    quantity REAL,
    avg_cost REAL,
    unrealized_pnl REAL,
    updated_at TIMESTAMP,
    FOREIGN KEY (symbol_id) REFERENCES symbols(id)
);

-- 交易歷史
CREATE TABLE trades (
    id INTEGER PRIMARY KEY,
    order_id TEXT,
    symbol_id INTEGER,
    side TEXT,
    quantity REAL,
    price REAL,
    fee REAL,
    pnl REAL,
    timestamp TIMESTAMP,
    FOREIGN KEY (symbol_id) REFERENCES symbols(id),
    FOREIGN KEY (order_id) REFERENCES orders(order_id)
);

-- 性能指標快照
CREATE TABLE performance_snapshots (
    id INTEGER PRIMARY KEY,
    date DATE UNIQUE,
    total_value REAL,
    realized_pnl REAL,
    unrealized_pnl REAL,
    win_rate REAL,
    sharpe_ratio REAL
);

-- 索引
CREATE INDEX idx_orders_symbol ON orders(symbol_id);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_trades_timestamp ON trades(timestamp);
CREATE INDEX idx_trades_symbol ON trades(symbol_id);
```

**預期效益**:
- ✅ 更完整的數據模型
- ✅ 查詢性能提升
- ✅ 數據安全性

---

## 📊 實施優先級與時間規劃 / Implementation Priority & Timeline

### Phase 1: 核心功能完善 (1-2 個月)
**目標**: 實現完整交易閉環

1. ✅ 賣出策略實作 (1 週)
2. ✅ 訂單管理系統 (2 週)
3. ✅ 持倉管理系統 (1 週)
4. ✅ 高級風險管理 (1 週)
5. ✅ 通知系統 (Telegram) (3 天)

**里程碑**: 能夠自動買入、賣出、止損，有完整交易記錄

---

### Phase 2: 策略與分析 (1-2 個月)
**目標**: 提升策略多樣性和可分析性

6. ✅ 技術指標擴充 (1 週)
7. ✅ 多策略支援 (2 週)
8. ✅ 性能追蹤與分析 (1 週)
9. ✅ 資金管理系統 (1 週)
10. ✅ 回測系統基礎版 (2 週)

**里程碑**: 有3+個可用策略，完整的性能分析報告

---

### Phase 3: 擴展與優化 (1 個月)
**目標**: 支援多幣對，提升性能

11. ✅ 多幣對交易支援 (1 週)
12. ✅ 性能優化 (異步) (1 週)
13. ✅ 資料庫優化 (1 週)
14. ✅ 單元測試 (持續)

**里程碑**: 穩定運行 5+ 幣對，響應時間 < 1 秒

---

### Phase 4: 精進與維護 (持續)
**目標**: 持續改進和維護

15. ✅ 配置管理增強
16. ✅ 日誌系統完善
17. ✅ CI/CD 集成
18. ✅ 文檔更新

**里程碑**: 生產級別的穩定性和可維護性

---

## 💰 預期效益總結 / Expected Benefits

### 功能面
- ✅ 完整的自動化交易系統
- ✅ 多策略、多幣對支援
- ✅ 完善的風險控制機制
- ✅ 實時監控和告警

### 技術面
- ✅ 模組化、可擴展架構
- ✅ 高性能異步處理
- ✅ 完整的測試覆蓋
- ✅ 生產級別的穩定性

### 數據面
- ✅ 完整的交易記錄
- ✅ 詳細的性能分析
- ✅ 數據驅動的優化
- ✅ 回測驗證能力

---

## 🎯 成功指標 / Success Metrics

### 交易性能
- 勝率 > 55%
- 盈虧比 > 1.5
- 最大回撤 < 15%
- 夏普比率 > 1.0

### 系統性能
- API 響應時間 < 1 秒
- 訂單執行成功率 > 99%
- 系統可用性 > 99.5%
- 支援 10+ 幣對並行

### 開發效率
- 新策略開發時間 < 1 天
- 測試覆蓋率 > 80%
- 部署頻率: 每週
- 平均修復時間 < 4 小時

---

## 📝 結論 / Conclusion

Trading Bot 2.0 將是一個**完整、穩健、可擴展**的交易系統。透過分階段實施，逐步建立起:

1. **完整的交易閉環** (買入 → 持有 → 賣出)
2. **多維度風險控制** (止損、倉位、回撤)
3. **數據驅動優化** (回測、分析、調整)
4. **生產級別穩定性** (測試、日誌、監控)

建議優先實施 **Phase 1 核心功能**，確保基礎穩固後再擴展。每個階段都應該:
- ✅ 充分測試
- ✅ 文檔更新
- ✅ 性能驗證
- ✅ 漸進式上線

**下一步行動**: 請確認優先級，我們可以開始實作 Phase 1 的功能！

---

**文檔版本**: 1.0  
**更新日期**: 2025-12-26  
**作者**: QRL Trading Bot Team
