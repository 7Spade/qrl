# QRL Trading Bot - 專案結構說明

## 📁 專案結構 / Project Structure

```
qrl/
├── 📄 核心交易模組 / Core Trading Modules
│   ├── main.py              # 主執行程式 - 協調交易流程
│   ├── config.py            # 配置管理 - 環境變數與參數
│   ├── exchange.py          # 交易所整合 - MEXC API 封裝
│   ├── strategy.py          # 交易策略 - EMA 指標分析
│   ├── risk.py              # 風險管理 - 倉位限制檢查
│   ├── state.py             # 狀態管理 - SQLite 持久化
│   └── utils.py             # 工具函數 - 通用輔助功能
│
├── 🌐 網頁儀表板 / Web Dashboard
│   └── web/
│       ├── app.py           # FastAPI 應用程式
│       └── templates/
│           └── index.html   # 儀表板 HTML 模板
│
├── 📚 文檔 / Documentation
│   ├── README.md            # 主要說明文檔
│   ├── 快速開始.md          # 中文快速入門
│   ├── AUTHENTICATION_GUIDE.md  # Cloud Run 驗證指南
│   ├── MEXC_API_SETUP.md    # API 設定指南
│   ├── CHANGELOG.md         # 版本歷史
│   ├── SIMPLIFICATION_SUMMARY.md  # 精簡變更記錄
│   └── PROJECT_STRUCTURE.md # 本文檔 - 專案結構說明
│
├── 🚀 部署配置 / Deployment
│   ├── Dockerfile           # Docker 容器定義
│   ├── cloudbuild.yaml      # Google Cloud Build 配置
│   ├── .dockerignore        # Docker 建置排除
│   └── requirements.txt     # Python 依賴套件
│
└── ⚙️  環境配置 / Environment
    ├── .env.example         # 環境變數範本
    └── .gitignore          # Git 排除規則
```

---

## 🔧 模組功能說明 / Module Functions

### 核心交易模組 / Core Trading Modules

#### 1. `main.py` - 主執行程式
**職責**: 協調整個交易流程
- 獲取市場數據 (OHLCV)
- 評估交易策略
- 檢查風險規則
- 執行限價買單
- 更新倉位狀態

**執行方式**:
```bash
python main.py
```

#### 2. `config.py` - 配置管理
**職責**: 管理所有配置參數
- 載入環境變數 (.env)
- 定義交易參數
  - `SYMBOL`: 交易對 (預設: QRL/USDT)
  - `BASE_ORDER_USDT`: 單筆訂單金額 (預設: 50 USDT)
  - `MAX_POSITION_USDT`: 最大倉位限制 (預設: 500 USDT)
  - `PRICE_OFFSET`: 限價折扣 (預設: 0.98 = 2% 折扣)

#### 3. `exchange.py` - 交易所整合
**職責**: 封裝 MEXC 交易所 API
- 建立 CCXT 交易所實例
- 配置 API 金鑰
- 支援子帳戶交易
- 啟用速率限制保護

**主要函數**:
- `get_exchange()`: 返回配置好的交易所實例

#### 4. `strategy.py` - 交易策略
**職責**: 實作 EMA 基礎策略
- 計算 EMA20 (短期均線)
- 計算 EMA60 (長期均線)
- 判斷買入信號

**買入條件**:
1. 價格 ≤ EMA60 × 1.02 (接近支撐位)
2. EMA20 ≥ EMA60 (正向動能)

**主要函數**:
- `should_buy(ohlcv)`: 判斷是否應該買入

#### 5. `risk.py` - 風險管理
**職責**: 控制倉位風險
- 檢查倉位是否超過限制
- 防止過度曝險

**主要函數**:
- `can_buy(current_position, max_position)`: 檢查是否可以買入

#### 6. `state.py` - 狀態管理
**職責**: 持久化交易狀態
- 使用 SQLite 資料庫
- 存儲倉位資訊
- 交易式更新

**主要函數**:
- `get_position_usdt()`: 獲取當前倉位
- `update_position_usdt(value)`: 更新倉位值

#### 7. `utils.py` - 工具函數
**職責**: 提供通用輔助功能
- 價格格式化
- 百分比計算
- 時間戳處理
- 安全除法運算

**主要函數**:
- `format_price()`: 格式化價格
- `format_percentage()`: 格式化百分比
- `get_timestamp()`: 獲取時間戳
- `safe_divide()`: 安全除法
- `calculate_position_usage()`: 計算倉位使用率

---

### 網頁儀表板 / Web Dashboard

#### `web/app.py` - FastAPI 應用
**職責**: 提供監控儀表板
- 顯示市場數據 (價格、漲跌、交易量)
- 顯示倉位狀態 (當前倉位、使用率)
- 顯示策略指標 (EMA20、EMA60、趨勢)
- 顯示交易信號 (買入條件檢查)
- 提供 API 端點

**端點**:
- `GET /`: 儀表板頁面
- `GET /health`: 健康檢查
- `GET /api/data`: JSON 格式數據

**啟動方式**:
```bash
uvicorn web.app:app --reload
# 或在生產環境
uvicorn web.app:app --host 0.0.0.0 --port 8080
```

#### `web/templates/index.html` - 儀表板模板
**特色**: 極簡風格的監控面板
- 響應式設計 (支援手機、平板)
- 終端機風格 (綠色文字 + 黑色背景)
- 6個資訊卡片:
  1. 💹 市場數據 - 價格、漲跌、交易量
  2. 💼 倉位與風險 - 當前倉位、使用率
  3. 📊 策略指標 - EMA20、EMA60、趨勢
  4. 🎯 交易信號 - 買入條件檢查
  5. ⚙️  配置參數 - 訂單金額、折扣
  6. 📈 24小時價格區間 - 最高、最低、波動
- 自動刷新 (每60秒)

---

## 📊 數據流程 / Data Flow

```
┌─────────────┐
│   main.py   │ ◄── 定時執行 (cron/scheduler)
└──────┬──────┘
       │
       ├─► exchange.py ──► MEXC API ──► 獲取 OHLCV 數據
       │
       ├─► strategy.py ──► 計算 EMA ──► 判斷買入信號
       │
       ├─► state.py ────► SQLite ────► 讀取當前倉位
       │
       ├─► risk.py ─────► 檢查倉位限制
       │
       └─► exchange.py ──► 下限價單 ──► 更新倉位
       
┌─────────────┐
│  web/app.py │ ◄── 網頁訪問
└──────┬──────┘
       │
       ├─► exchange.py ──► 獲取市場數據
       │
       ├─► strategy.py ──► 計算策略指標
       │
       ├─► state.py ────► 讀取倉位狀態
       │
       └─► templates/index.html ──► 渲染儀表板
```

---

## 🎯 擴展指南 / Extension Guide

### 如何添加新策略 / Add New Strategy

1. 在 `strategy.py` 中添加新函數:
```python
def should_sell(ohlcv: list) -> bool:
    """判斷賣出條件"""
    # 實作賣出邏輯
    pass
```

2. 在 `main.py` 中整合:
```python
if should_sell(ohlcv):
    # 執行賣出邏輯
    pass
```

### 如何添加新指標 / Add New Indicator

1. 在 `strategy.py` 中計算新指標:
```python
def calculate_rsi(ohlcv: list) -> float:
    """計算 RSI 指標"""
    # 使用現有的 pandas 和 ta 套件
    pass
```

2. 在 `web/app.py` 中添加到儀表板:
```python
rsi = calculate_rsi(ohlcv)
# 傳遞給模板
```

### 如何支援多幣對 / Support Multiple Pairs

1. 修改 `config.py`:
```python
SYMBOLS = ["QRL/USDT", "BTC/USDT", "ETH/USDT"]
```

2. 修改 `main.py` 使用迴圈處理
3. 修改 `state.py` 為每個幣對分別存儲

### 如何添加通知 / Add Notifications

1. 創建 `notifications.py`:
```python
def send_notification(message: str):
    """發送通知 (Email/Telegram/等)"""
    pass
```

2. 在 `main.py` 中整合:
```python
from notifications import send_notification

if should_buy(ohlcv):
    send_notification("買入信號觸發!")
```

---

## 🔒 最佳實踐 / Best Practices

### 1. 配置管理
- ✅ 使用 `.env` 文件管理敏感信息
- ✅ 不要提交 `.env` 到 Git
- ✅ 提供 `.env.example` 作為範本

### 2. 錯誤處理
- ✅ 使用 try-except 處理 API 錯誤
- ✅ 記錄錯誤日誌
- ✅ 優雅降級 (顯示 N/A 而非崩潰)

### 3. 代碼組織
- ✅ 單一職責原則 (每個模組專注一件事)
- ✅ 函數文檔字串 (Docstring)
- ✅ 類型提示 (Type hints)

### 4. 測試
- ✅ 本地測試後再部署
- ✅ 使用小額測試交易
- ✅ 監控儀表板確認運行正常

### 5. 部署
- ✅ 使用 Docker 容器化
- ✅ Cloud Run 自動擴展
- ✅ 定時任務自動執行

---

## 📝 維護檢查清單 / Maintenance Checklist

### 日常維護
- [ ] 檢查儀表板數據是否正常
- [ ] 檢查倉位是否在合理範圍
- [ ] 檢查 API 金鑰是否有效

### 每週維護
- [ ] 查看交易記錄
- [ ] 檢查策略表現
- [ ] 備份資料庫 (data/state.db)

### 每月維護
- [ ] 更新依賴套件
- [ ] 檢查 API 權限
- [ ] 審查配置參數

---

## 🆘 常見問題 / FAQ

### Q: 如何修改交易參數?
A: 編輯 `config.py` 或設定環境變數

### Q: 如何查看交易歷史?
A: 目前僅存儲當前倉位，需要查看 MEXC 交易記錄

### Q: 如何停止機器人?
A: 停止定時任務或關閉 Cloud Run 服務

### Q: 資料庫在哪裡?
A: `data/state.db` (SQLite 檔案)

### Q: 如何重置倉位?
A: 刪除 `data/state.db` 或手動更新資料庫

---

**文檔版本**: 1.0  
**更新日期**: 2025-12-26  
**維護者**: QRL Trading Bot Team
