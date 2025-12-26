# Cloud Scheduler + Cloud Run Jobs 設定指南

## 📋 概述

本指南說明如何使用 Google Cloud Scheduler 定時觸發 Cloud Run Jobs，實現交易機器人的自動化執行。

### 架構圖

```
Cloud Scheduler (定時器)
    ↓ (觸發)
Cloud Run Jobs (交易機器人)
    ↓ (執行交易邏輯)
MEXC 交易所 API
```

### 為什麼使用 Cloud Run Jobs？

- ✅ **適合批次任務**：執行完成後自動關閉，節省成本
- ✅ **與 Cloud Scheduler 完美整合**：原生支援定時觸發
- ✅ **免費額度**：Cloud Scheduler 前 3 個作業免費
- ✅ **簡單部署**：無需管理伺服器或編寫腳本
- ✅ **自動擴展**：根據需求自動調整資源

## 🎯 前置需求

1. Google Cloud 專案已建立
2. 已啟用以下 API：
   - Cloud Run API
   - Cloud Scheduler API
   - Cloud Build API
3. 已設定 VPC Connector（如需訪問 Redis）
4. 已準備環境變數（API keys, Redis URL 等）

## 🚀 部署步驟

### Step 1: 部署 Cloud Run Job

使用 Cloud Build 自動建置和部署：

```bash
# 1. 設定專案 ID
export PROJECT_ID="your-project-id"
gcloud config set project $PROJECT_ID

# 2. 執行 Cloud Build（會自動建置 Docker image 並部署 Cloud Run Job）
gcloud builds submit --config cloudbuild-job.yaml

# 3. 驗證部署成功
gcloud run jobs describe qrl-trading-job --region asia-east1
```

### Step 2: 建立 Cloud Scheduler 作業

#### 方法 1: 使用 gcloud 命令（推薦）

```bash
# 設定變數
export PROJECT_ID="your-project-id"
export REGION="asia-east1"
export JOB_NAME="qrl-trading-job"

# 建立 Cloud Scheduler 作業（每日上午 9:00 執行）
gcloud scheduler jobs create http qrl-trading-daily \
  --location=$REGION \
  --schedule="0 9 * * *" \
  --time-zone="Asia/Taipei" \
  --uri="https://$REGION-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/$PROJECT_ID/jobs/$JOB_NAME:run" \
  --http-method=POST \
  --oauth-service-account-email="$PROJECT_ID@appspot.gserviceaccount.com" \
  --description="Daily QRL trading bot execution"

# 驗證建立成功
gcloud scheduler jobs list --location=$REGION
```

#### 方法 2: 使用 Google Cloud Console

1. 前往 Cloud Console > Cloud Scheduler
2. 點擊「建立作業」
3. 填寫以下資訊：
   - **名稱**：`qrl-trading-daily`
   - **地區**：`asia-east1`
   - **頻率**：`0 9 * * *`（每日上午 9:00）
   - **時區**：`Asia/Taipei`
   - **目標類型**：選擇「HTTP」
   - **URL**：`https://asia-east1-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/YOUR_PROJECT_ID/jobs/qrl-trading-job:run`
   - **HTTP 方法**：`POST`
   - **驗證標頭**：選擇「新增 OAuth 權杖」，使用預設服務帳戶
4. 點擊「建立」

### Step 3: 測試執行

```bash
# 手動觸發 Scheduler 作業測試
gcloud scheduler jobs run qrl-trading-daily --location=asia-east1

# 檢查執行日誌
gcloud run jobs executions list --job qrl-trading-job --region asia-east1

# 查看最近執行的詳細日誌
gcloud logging read "resource.type=cloud_run_job AND resource.labels.job_name=qrl-trading-job" \
  --limit 50 \
  --format json
```

## 📅 排程設定範例

Cloud Scheduler 使用 Unix cron 格式：

```
格式: 分 時 日 月 週
     * * * * *
     │ │ │ │ │
     │ │ │ │ └─── 週幾 (0-6, 0=星期日)
     │ │ │ └───── 月份 (1-12)
     │ │ └─────── 日期 (1-31)
     │ └───────── 小時 (0-23)
     └─────────── 分鐘 (0-59)
```

### 常用排程

| 需求 | Cron 表達式 | 說明 |
|------|------------|------|
| 每日上午 9:00 | `0 9 * * *` | 適合開盤前執行 |
| 每 4 小時 | `0 */4 * * *` | 定期檢查市場 |
| 工作日上午 9:00 | `0 9 * * 1-5` | 週一到週五 |
| 每日 9:00 和 15:00 | `0 9,15 * * *` | 開盤和收盤前 |
| 每 30 分鐘 | `*/30 * * * *` | 高頻交易 |

### 利用免費額度（3 個作業）

```bash
# 作業 1: 早上檢查（6:00 AM）
gcloud scheduler jobs create http qrl-trading-morning \
  --location=asia-east1 \
  --schedule="0 6 * * *" \
  --time-zone="Asia/Taipei" \
  --uri="https://asia-east1-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/$PROJECT_ID/jobs/$JOB_NAME:run" \
  --http-method=POST \
  --oauth-service-account-email="$PROJECT_ID@appspot.gserviceaccount.com"

# 作業 2: 中午檢查（12:00 PM）
gcloud scheduler jobs create http qrl-trading-noon \
  --location=asia-east1 \
  --schedule="0 12 * * *" \
  --time-zone="Asia/Taipei" \
  --uri="https://asia-east1-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/$PROJECT_ID/jobs/$JOB_NAME:run" \
  --http-method=POST \
  --oauth-service-account-email="$PROJECT_ID@appspot.gserviceaccount.com"

# 作業 3: 傍晚檢查（6:00 PM）
gcloud scheduler jobs create http qrl-trading-evening \
  --location=asia-east1 \
  --schedule="0 18 * * *" \
  --time-zone="Asia/Taipei" \
  --uri="https://asia-east1-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/$PROJECT_ID/jobs/$JOB_NAME:run" \
  --http-method=POST \
  --oauth-service-account-email="$PROJECT_ID@appspot.gserviceaccount.com"
```

## 🔧 進階設定

### 重試策略

```bash
gcloud scheduler jobs update http qrl-trading-daily \
  --location=asia-east1 \
  --max-retry-attempts=2 \
  --max-retry-duration=3600s \
  --min-backoff-duration=5s \
  --max-backoff-duration=60s
```

### 暫停/恢復作業

```bash
# 暫停
gcloud scheduler jobs pause qrl-trading-daily --location=asia-east1

# 恢復
gcloud scheduler jobs resume qrl-trading-daily --location=asia-east1
```

### 更新排程

```bash
gcloud scheduler jobs update http qrl-trading-daily \
  --location=asia-east1 \
  --schedule="0 10 * * *" \
  --time-zone="Asia/Taipei"
```

## 📊 監控與日誌

### 查看執行歷史

```bash
# Scheduler 執行記錄
gcloud scheduler jobs describe qrl-trading-daily --location=asia-east1

# Cloud Run Job 執行記錄
gcloud run jobs executions list --job qrl-trading-job --region asia-east1
```

### 查看即時日誌

```bash
# 最近 50 條日誌
gcloud logging read "resource.type=cloud_run_job AND resource.labels.job_name=qrl-trading-job" \
  --limit 50 \
  --format json

# 即時串流日誌（執行時監控）
gcloud logging tail "resource.type=cloud_run_job AND resource.labels.job_name=qrl-trading-job"
```

### 設定告警（可選）

前往 Cloud Console > Monitoring > Alerting，建立以下告警：

1. **Job 執行失敗**
   - 條件: Cloud Run Job 執行狀態 = Failed
   - 通知: Email/SMS

2. **Job 執行時間過長**
   - 條件: Job 執行時間 > 5 分鐘
   - 通知: Email

## 💰 成本估算

### Cloud Scheduler 費用

- **免費額度**：每月前 3 個作業免費
- **付費作業**：$0.10 USD/作業/月
- **範例**：
  - 1 個作業 = 免費
  - 3 個作業 = 免費
  - 5 個作業 = 免費（3 個）+ $0.20 USD（2 個）

### Cloud Run Jobs 費用

基於實際執行時間計費：

- **CPU 時間**：約 $0.00002400 USD/vCPU-second
- **記憶體**：約 $0.00000250 USD/GB-second
- **範例計算**（每次執行約 30 秒）：
  - 1 vCPU, 512 MB 記憶體
  - 每次執行成本：約 $0.00072 USD
  - 每日執行 3 次：約 $0.0022 USD/天
  - 每月成本：約 $0.065 USD

**總成本估算**（3 個免費 Scheduler + 每日 3 次執行）：
- Cloud Scheduler: $0.00 USD
- Cloud Run Jobs: ~$0.065 USD/月
- **總計**: ~$0.065 USD/月（約 NT$2）

## ⚠️ 注意事項

1. **時區設定**：確保使用正確的時區（如 `Asia/Taipei`）
2. **服務帳戶權限**：預設服務帳戶需要 `run.jobs.run` 權限
3. **Job 超時時間**：Cloud Run Jobs 預設超時 10 分鐘，可根據需求調整
4. **環境變數**：確保在 Cloud Run Job 中設定所有必要的環境變數
5. **VPC 連接**：如果需要連接私有 Redis，確保已設定 VPC Connector
6. **重試次數**：建議設定適當的重試次數，避免因暫時性錯誤導致交易失敗

## 🔍 故障排除

### Scheduler 無法觸發 Job

```bash
# 1. 檢查服務帳戶權限
gcloud projects get-iam-policy $PROJECT_ID \
  --flatten="bindings[].members" \
  --filter="bindings.members:$PROJECT_ID@appspot.gserviceaccount.com"

# 2. 授予必要權限
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$PROJECT_ID@appspot.gserviceaccount.com" \
  --role="roles/run.invoker"
```

### Job 執行失敗

```bash
# 查看詳細錯誤日誌
gcloud logging read "resource.type=cloud_run_job AND severity>=ERROR" \
  --limit 20 \
  --format json
```

### 環境變數未載入

檢查 Cloud Run Job 環境變數設定：

```bash
gcloud run jobs describe qrl-trading-job --region asia-east1 --format yaml
```

## 📚 參考資源

- [Cloud Scheduler 官方文檔](https://cloud.google.com/scheduler/docs)
- [Cloud Run Jobs 官方文檔](https://cloud.google.com/run/docs/create-jobs)
- [Cron 表達式產生器](https://crontab.guru/)
- [Cloud Run 定價](https://cloud.google.com/run/pricing)

## 🎯 最佳實踐

1. **從小開始**：先建立 1-2 個排程測試，確認正常後再增加
2. **監控日誌**：定期檢查執行日誌，確保交易邏輯正確執行
3. **成本控制**：使用免費額度的 3 個作業，避免不必要的開支
4. **測試環境**：在正式部署前，先在測試環境驗證完整流程
5. **文檔記錄**：記錄每個排程的用途和執行時間，方便維護
6. **告警設定**：設定適當的告警，及時發現和處理問題

---

**提示**：本指南完全使用 Google Cloud 原生服務，無需編寫任何腳本，符合「過程不考慮任何腳本」的要求。
