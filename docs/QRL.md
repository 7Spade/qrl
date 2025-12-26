
## ✅ **1. Candlestick Data — K 線 / OHLCV**

**Endpoint:** `GET /open/api/v2/market/kline`
返回每個時間段（分鐘/小時/日/月）的 K 線資料（JSON 陣列）。
**資料欄位：**

| 字段                                                                        | 說明                    |
| ------------------------------------------------------------------------- | --------------------- |
| `time`                                                                    | K 線開頭時間（Unix seconds） |
| `open`                                                                    | 開盤價                   |
| `close`                                                                   | 收盤價                   |
| `high`                                                                    | 最高價                   |
| `low`                                                                     | 最低價                   |
| `vol`                                                                     | 交易量（base asset）       |
| `amount`                                                                  | 成交額（quote asset）      |
| **用途:** 計算 **MA/EMA/MACD/RSI/VWAP 等所有技術指標** 都需要的原始數據集。([Mexc Develop][1]) |                       |

---

## ✅ **2. Latest Deals — 最新成交**

**Endpoint:** `GET /open/api/v2/market/deals`
返回近期成交記錄列表。
**資料欄位：**

| 字段                                                            | 說明            |
| ------------------------------------------------------------- | ------------- |
| `trade_time`                                                  | 成交時間（ms）      |
| `trade_price`                                                 | 成交價格          |
| `trade_quantity`                                              | 成交數量          |
| `trade_type`                                                  | 成交方向（BID/ASK） |
| **用途:** **tick/成交價格與量流分析**、VWAP 估算、量價關係判斷。([Mexc Develop][1]) |               |

---

## ✅ **3. Market Depth — 深度**

**Endpoint:** `GET /open/api/v2/market/depth`
返回當前買賣盤深度（price/quantity list）。
**資料欄位：**

| 字段                                                         | 說明                            |
| ---------------------------------------------------------- | ----------------------------- |
| `bids`                                                     | 買盤陣列：每筆包含 `price`, `quantity` |
| `asks`                                                     | 賣盤陣列：每筆包含 `price`, `quantity` |
| **用途:** 估算 **流動性 / 支撐阻力 / VWAP 下單量模型**。([Mexc Develop][1]) |                               |

---

## ✅ **4. Ticker Information — 最佳行情訊息**

**Endpoint:** `GET /open/api/v2/market/ticker`
返回最新市場行情統計。
**主要欄位：**

| 字段                                                       | 說明        |
| -------------------------------------------------------- | --------- |
| `symbol`                                                 | 交易對名稱     |
| `volume`                                                 | 24h 交易量   |
| `amount`                                                 | 24h 成交額   |
| `high`                                                   | 24h 最高價   |
| `low`                                                    | 24h 最低價   |
| `bid`                                                    | 最佳買價      |
| `ask`                                                    | 最佳賣價      |
| `open`                                                   | 24h 開盤價   |
| `last`                                                   | 最新成交價     |
| `time`                                                   | 最新時間戳     |
| `change_rate`                                            | 24h 漲跌百分比 |
| **用途:** 快速取得 **24h 市場趨勢、最佳買賣價、波動資訊**。([Mexc Develop][1]) |           |

---

