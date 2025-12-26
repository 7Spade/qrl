# 快速部署指南 - Cloud Scheduler + Cloud Run Jobs

## 🎯 目標

實現交易機器人自動化執行，使用 Google Cloud 原生服務，無需編寫腳本。

```
Cloud Scheduler (定時器)
    ↓
Cloud Run Jobs (交易機器人)
    ↓
執行交易邏輯
```

## ⚡ 快速開始（3 步驟）

### Step 1: 部署 Cloud Run Job

```bash
# 設定專案
gcloud config set project YOUR_PROJECT_ID

# 建置並部署
gcloud builds submit --config cloudbuild-job.yaml
```

### Step 2: 建立 Cloud Scheduler

```bash
# 設定變數
export PROJECT_ID="YOUR_PROJECT_ID"
export REGION="asia-east1"

# 建立每日排程（上午 9:00）
gcloud scheduler jobs create run qrl-trading-daily \
  --location=$REGION \
  --schedule="0 9 * * *" \
  --time-zone="Asia/Taipei" \
  --uri="https://$REGION-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/$PROJECT_ID/jobs/qrl-trading-job:run" \
  --http-method=POST \
  --oauth-service-account-email="$PROJECT_ID@appspot.gserviceaccount.com"
```

### Step 3: 測試執行

```bash
# 手動觸發測試
gcloud scheduler jobs run qrl-trading-daily --location=asia-east1

# 查看執行結果
gcloud run jobs executions list --job qrl-trading-job --region asia-east1
```

## 📋 完整部署流程

### 1. 前置準備

```bash
# 啟用必要的 API
gcloud services enable run.googleapis.com
gcloud services enable cloudscheduler.googleapis.com
gcloud services enable cloudbuild.googleapis.com

# 確認專案設定
gcloud config list
```

### 2. 配置環境變數

編輯 `cloudbuild-job.yaml` 中的環境變數：

```yaml
--set-env-vars SYMBOL=QRL/USDT,\
BASE_ORDER_USDT=1.5,\
MAX_POSITION_USDT=2.0,\
PRICE_OFFSET=0.98,\
REDIS_URL=redis://your-redis-url,\
REDIS_CACHE_TTL=600,\
MEXC_API_KEY=your-api-key,\
MEXC_API_SECRET=your-api-secret
```

### 3. 部署 Cloud Run Job

```bash
# 執行 Cloud Build
gcloud builds submit --config cloudbuild-job.yaml

# 驗證部署
gcloud run jobs describe qrl-trading-job --region asia-east1
```

### 4. 設定排程（利用免費額度）

#### 排程 1: 早上檢查（6:00 AM）

```bash
gcloud scheduler jobs create run qrl-trading-morning \
  --location=asia-east1 \
  --schedule="0 6 * * *" \
  --time-zone="Asia/Taipei" \
  --uri="https://asia-east1-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/$PROJECT_ID/jobs/qrl-trading-job:run" \
  --http-method=POST \
  --oauth-service-account-email="$PROJECT_ID@appspot.gserviceaccount.com"
```

#### 排程 2: 中午檢查（12:00 PM）

```bash
gcloud scheduler jobs create run qrl-trading-noon \
  --location=asia-east1 \
  --schedule="0 12 * * *" \
  --time-zone="Asia/Taipei" \
  --uri="https://asia-east1-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/$PROJECT_ID/jobs/qrl-trading-job:run" \
  --http-method=POST \
  --oauth-service-account-email="$PROJECT_ID@appspot.gserviceaccount.com"
```

#### 排程 3: 傍晚檢查（6:00 PM）

```bash
gcloud scheduler jobs create run qrl-trading-evening \
  --location=asia-east1 \
  --schedule="0 18 * * *" \
  --time-zone="Asia/Taipei" \
  --uri="https://asia-east1-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/$PROJECT_ID/jobs/qrl-trading-job:run" \
  --http-method=POST \
  --oauth-service-account-email="$PROJECT_ID@appspot.gserviceaccount.com"
```

### 5. 測試和驗證

```bash
# 手動觸發測試
gcloud scheduler jobs run qrl-trading-morning --location=asia-east1

# 查看執行狀態
gcloud run jobs executions list --job qrl-trading-job --region asia-east1

# 查看日誌
gcloud logging read "resource.type=cloud_run_job" --limit 20
```

## 🔧 常用管理命令

### 查看排程

```bash
# 列出所有排程
gcloud scheduler jobs list --location=asia-east1

# 查看特定排程詳情
gcloud scheduler jobs describe qrl-trading-daily --location=asia-east1
```

### 修改排程

```bash
# 更改執行時間
gcloud scheduler jobs update run qrl-trading-daily \
  --location=asia-east1 \
  --schedule="0 10 * * *"

# 暫停排程
gcloud scheduler jobs pause qrl-trading-daily --location=asia-east1

# 恢復排程
gcloud scheduler jobs resume qrl-trading-daily --location=asia-east1
```

### 更新 Cloud Run Job

```bash
# 重新建置並部署
gcloud builds submit --config cloudbuild-job.yaml

# 手動更新環境變數
gcloud run jobs update qrl-trading-job \
  --region asia-east1 \
  --set-env-vars KEY=VALUE
```

## 📊 監控和日誌

### 即時日誌

```bash
# 串流日誌
gcloud logging tail "resource.type=cloud_run_job AND resource.labels.job_name=qrl-trading-job"

# 查看最近 50 條日誌
gcloud logging read "resource.type=cloud_run_job" --limit 50
```

### 執行歷史

```bash
# Cloud Run Job 執行記錄
gcloud run jobs executions list --job qrl-trading-job --region asia-east1

# Scheduler 執行記錄
gcloud scheduler jobs describe qrl-trading-daily --location=asia-east1
```

## 💰 成本估算

### 免費額度

- Cloud Scheduler: **前 3 個作業免費**
- Cloud Run Jobs: 每月有免費額度
  - 180,000 vCPU-seconds
  - 360,000 GiB-seconds

### 預估成本（3 個排程，每日執行）

- **Cloud Scheduler**: $0.00（使用免費額度）
- **Cloud Run Jobs**: ~$0.065 USD/月
- **總計**: ~$0.065 USD/月（約 NT$2）

## ⚠️ 注意事項

1. **環境變數安全**：不要在 cloudbuild-job.yaml 中提交敏感資訊
   - 使用 Secret Manager 儲存 API keys
   - 參考 [Secret Manager 整合指南](https://cloud.google.com/run/docs/configuring/secrets)

2. **時區設定**：確保使用正確的時區（`Asia/Taipei` = UTC+8）

3. **執行超時**：Cloud Run Jobs 預設超時 10 分鐘
   - 如需更長執行時間，使用 `--task-timeout` 參數調整

4. **重試設定**：建議設定適當的重試次數
   ```bash
   gcloud scheduler jobs update run qrl-trading-daily \
     --location=asia-east1 \
     --max-retry-attempts=2
   ```

5. **服務帳戶權限**：確保服務帳戶有 `run.jobs.run` 權限

## 🔍 故障排除

### Scheduler 無法觸發 Job

```bash
# 檢查權限
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$PROJECT_ID@appspot.gserviceaccount.com" \
  --role="roles/run.invoker"
```

### Job 執行失敗

```bash
# 查看錯誤日誌
gcloud logging read "resource.type=cloud_run_job AND severity>=ERROR" --limit 20

# 查看 Job 設定
gcloud run jobs describe qrl-trading-job --region asia-east1 --format yaml
```

### 環境變數問題

```bash
# 檢查 Job 環境變數
gcloud run jobs describe qrl-trading-job --region asia-east1 \
  --format="value(spec.template.spec.containers[0].env)"
```

## 📚 相關文檔

- [詳細設定指南](./CLOUD_SCHEDULER_SETUP.md)
- [Cloud Run Jobs 官方文檔](https://cloud.google.com/run/docs/create-jobs)
- [Cloud Scheduler 官方文檔](https://cloud.google.com/scheduler/docs)
- [Cron 表達式產生器](https://crontab.guru/)

## 🎯 最佳實踐

1. ✅ 先在測試環境驗證
2. ✅ 使用 Secret Manager 管理敏感資訊
3. ✅ 設定適當的告警和監控
4. ✅ 定期檢查執行日誌
5. ✅ 利用免費額度（3 個 Scheduler）
6. ✅ 記錄每次配置變更

---

**完成！** 您已成功設定 Cloud Scheduler + Cloud Run Jobs 自動化交易系統。
