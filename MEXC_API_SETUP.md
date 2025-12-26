# MEXC API 設定指南 / MEXC API Setup Guide

## 中文說明

### MEXC API 憑證說明

當您在 MEXC 交易所建立 API 金鑰時，MEXC 會提供兩個憑證：

1. **Access Key（存取金鑰）**
   - 也稱為 "API Key"
   - 這是公開的識別碼
   - 在 `.env` 檔案中設定為 `MEXC_API_KEY`

2. **Secret Key（密鑰）**
   - 也稱為 "API Secret"
   - 這是私密金鑰，用於簽署請求
   - 在 `.env` 檔案中設定為 `MEXC_API_SECRET`

### 取得 API 金鑰的步驟

1. 登入 MEXC 交易所
2. 前往 **用戶中心** → **API 管理**：https://www.mexc.com/user/openapi
3. 點擊「建立 API」
4. 設定 API 名稱和權限：
   - ✅ 勾選「現貨交易」權限
   - ✅ 可選擇綁定 IP 位址以提高安全性
   - ⚠️ 不要勾選「提現」權限（除非您需要）
5. 完成身份驗證（例如 2FA）
6. 記錄您的 **Access Key** 和 **Secret Key**
   - ⚠️ **重要**：Secret Key 只會顯示一次，請妥善保存
   - 如果遺失，需要刪除並重新建立 API 金鑰

### 設定 .env 檔案

```bash
# 複製範例檔案
cp .env.example .env

# 編輯 .env 並填入您的憑證
MEXC_API_KEY=your_access_key_here       # 填入您的 Access Key
MEXC_API_SECRET=your_secret_key_here    # 填入您的 Secret Key
SYMBOL=QRL/USDT                          # 交易對
```

### 子帳戶交易（選用）

如果您使用 MEXC 子帳戶進行交易：

```bash
MEXC_SUBACCOUNT=your_subaccount_name    # 子帳戶名稱
```

---

## English Guide

### MEXC API Credentials Explanation

When you create an API key on MEXC exchange, MEXC provides two credentials:

1. **Access Key**
   - Also called "API Key"
   - This is your public identifier
   - Set as `MEXC_API_KEY` in the `.env` file

2. **Secret Key**
   - Also called "API Secret"
   - This is your private key used to sign requests
   - Set as `MEXC_API_SECRET` in the `.env` file

### Steps to Obtain API Keys

1. Log in to MEXC exchange
2. Go to **User Center** → **API Management**: https://www.mexc.com/user/openapi
3. Click "Create API"
4. Configure API name and permissions:
   - ✅ Enable "Spot Trading" permission
   - ✅ Optionally bind IP addresses for enhanced security
   - ⚠️ Do NOT enable "Withdrawal" permission (unless needed)
5. Complete authentication (e.g., 2FA)
6. Record your **Access Key** and **Secret Key**
   - ⚠️ **Important**: Secret Key is shown only once - save it securely
   - If lost, you must delete and recreate the API key

### Configure .env File

```bash
# Copy the example file
cp .env.example .env

# Edit .env and fill in your credentials
MEXC_API_KEY=your_access_key_here       # Your Access Key
MEXC_API_SECRET=your_secret_key_here    # Your Secret Key
SYMBOL=QRL/USDT                          # Trading pair
```

### Subaccount Trading (Optional)

If you're using a MEXC subaccount for trading:

```bash
MEXC_SUBACCOUNT=your_subaccount_name    # Subaccount name
```

---

## 常見問題 / FAQ

### Q: MEXC 沒有提供 MEXC_API_SECRET，該怎麼辦？

**A**: MEXC 確實有提供 Secret Key。當您建立 API 金鑰時，會同時顯示 Access Key 和 Secret Key：
- **Access Key** = `MEXC_API_KEY`
- **Secret Key** = `MEXC_API_SECRET`

如果您只看到一個金鑰，請確認是否已完成所有建立步驟。Secret Key 只會在建立時顯示一次，如果遺失需要重新建立 API。

### Q: What if MEXC doesn't provide MEXC_API_SECRET?

**A**: MEXC does provide a Secret Key. When you create an API key, both Access Key and Secret Key are displayed:
- **Access Key** = `MEXC_API_KEY`
- **Secret Key** = `MEXC_API_SECRET`

If you only see one key, please ensure you've completed all creation steps. The Secret Key is shown only once during creation - if lost, you must recreate the API.

### Q: 我應該使用哪些權限？/ What permissions should I use?

**A (中文)**: 
- ✅ **現貨交易** (Spot Trading) - 必需
- ✅ **讀取** (Read) - 自動包含
- ⚠️ **提現** (Withdrawal) - 不建議啟用（安全考量）
- ⚠️ **槓桿/合約** - 本機器人不需要

**A (English)**:
- ✅ **Spot Trading** - Required
- ✅ **Read** - Automatically included
- ⚠️ **Withdrawal** - Not recommended (security risk)
- ⚠️ **Margin/Futures** - Not needed for this bot

### Q: 如何提高 API 安全性？/ How to improve API security?

**A (中文)**:
1. 綁定 IP 位址 - 限制只有特定 IP 可以使用
2. 不要啟用提現權限
3. 定期更換 API 金鑰
4. 不要分享或提交 Secret Key 到版本控制系統
5. 使用環境變數儲存憑證

**A (English)**:
1. Bind IP addresses - restrict to specific IPs only
2. Don't enable withdrawal permissions
3. Rotate API keys regularly
4. Never share or commit Secret Key to version control
5. Use environment variables to store credentials

---

## 安全警告 / Security Warning

⚠️ **中文**：
- 絕對不要在程式碼中寫死 API 金鑰
- 絕對不要將 `.env` 檔案提交到 Git
- 如果不小心洩漏了 Secret Key，立即刪除該 API 並建立新的
- 建議使用 Google Secret Manager 等服務儲存生產環境的憑證

⚠️ **English**:
- NEVER hardcode API keys in your code
- NEVER commit `.env` file to Git
- If Secret Key is leaked, immediately delete the API and create a new one
- Consider using Google Secret Manager for production credentials

---

## 測試連線 / Test Connection

執行以下指令測試 API 連線 / Run this to test API connection:

```python
python3 << 'PYTHON'
import ccxt
import os
from dotenv import load_dotenv

load_dotenv()

exchange = ccxt.mexc({
    'apiKey': os.getenv('MEXC_API_KEY'),
    'secret': os.getenv('MEXC_API_SECRET'),
    'enableRateLimit': True,
})

try:
    balance = exchange.fetch_balance()
    print("✓ API 連線成功！/ API connection successful!")
    print(f"✓ USDT 餘額 / USDT Balance: {balance['USDT']['free']}")
except Exception as e:
    print(f"✗ API 連線失敗 / API connection failed: {e}")
PYTHON
```

---

## 參考連結 / References

- MEXC API 管理頁面 / API Management: https://www.mexc.com/user/openapi
- MEXC API 文件 / Documentation: https://mexcdevelop.github.io/apidocs/spot_v3_en/
- CCXT 文件 / CCXT Docs: https://docs.ccxt.com/

---

**最後更新 / Last Updated**: 2024-12-26
