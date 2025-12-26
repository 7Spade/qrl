# 快速開始 - Cloud Scheduler + Cloud Run Jobs

## 🚀 3 步驟部署

### Step 1: 部署 Cloud Run Job

```bash
# 設定專案
gcloud config set project YOUR_PROJECT_ID

# 一鍵部署
gcloud builds submit --config cloudbuild-job.yaml
```

**預計時間**: 2-3 分鐘

### Step 2: 建立 Cloud Scheduler

```bash
# 設定變數
export PROJECT_ID="YOUR_PROJECT_ID"
export REGION="asia-east1"

# 建立排程 1 (早上 6:00)
gcloud scheduler jobs create http qrl-trading-morning \
  --location=$REGION \
  --schedule="0 6 * * *" \
  --time-zone="Asia/Taipei" \
  --uri="https://$REGION-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/$PROJECT_ID/jobs/qrl-trading-job:run" \
  --http-method=POST \
  --oauth-service-account-email="$PROJECT_ID@appspot.gserviceaccount.com"

# 建立排程 2 (中午 12:00) - 可選
gcloud scheduler jobs create http qrl-trading-noon \
  --location=$REGION \
  --schedule="0 12 * * *" \
  --time-zone="Asia/Taipei" \
  --uri="https://$REGION-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/$PROJECT_ID/jobs/qrl-trading-job:run" \
  --http-method=POST \
  --oauth-service-account-email="$PROJECT_ID@appspot.gserviceaccount.com"

# 建立排程 3 (傍晚 18:00) - 可選
gcloud scheduler jobs create http qrl-trading-evening \
  --location=$REGION \
  --schedule="0 18 * * *" \
  --time-zone="Asia/Taipei" \
  --uri="https://$REGION-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/$PROJECT_ID/jobs/qrl-trading-job:run" \
  --http-method=POST \
  --oauth-service-account-email="$PROJECT_ID@appspot.gserviceaccount.com"
```

**預計時間**: 1 分鐘

### Step 3: 測試執行

```bash
# 手動觸發測試
gcloud scheduler jobs run qrl-trading-morning --location=asia-east1

# 查看執行結果
gcloud run jobs executions list --job qrl-trading-job --region asia-east1

# 查看日誌
gcloud logging read "resource.type=cloud_run_job" --limit 20
```

**預計時間**: 1 分鐘

## 💰 成本

- **Cloud Scheduler**: $0.00 (前 3 個作業免費)
- **Cloud Run Jobs**: ~$0.065/月 (每日 3 次執行)
- **總計**: ~NT$2/月

## 📚 完整文檔

| 文檔 | 用途 |
|------|------|
| [DEPLOYMENT_QUICKSTART.md](docs/DEPLOYMENT_QUICKSTART.md) | 快速部署指南 |
| [CLOUD_SCHEDULER_SETUP.md](docs/CLOUD_SCHEDULER_SETUP.md) | 詳細設定和故障排除 |
| [TRADING_STRATEGY_DISCUSSION.md](docs/TRADING_STRATEGY_DISCUSSION.md) | 策略分析和優化 |
| [ARCHITECTURE_DIAGRAM.md](docs/ARCHITECTURE_DIAGRAM.md) | 系統架構圖 |
| [SOLUTION_SUMMARY.md](docs/SOLUTION_SUMMARY.md) | 解決方案總結 |

## ⚡ 常用命令

### 查看狀態

```bash
# 查看 Scheduler 列表
gcloud scheduler jobs list --location=asia-east1

# 查看 Job 詳情
gcloud run jobs describe qrl-trading-job --region asia-east1

# 查看執行記錄
gcloud run jobs executions list --job qrl-trading-job --region asia-east1
```

### 管理排程

```bash
# 暫停排程
gcloud scheduler jobs pause qrl-trading-morning --location=asia-east1

# 恢復排程
gcloud scheduler jobs resume qrl-trading-morning --location=asia-east1

# 修改排程時間
gcloud scheduler jobs update http qrl-trading-morning \
  --location=asia-east1 \
  --schedule="0 10 * * *"
```

### 查看日誌

```bash
# 最近 50 條日誌
gcloud logging read "resource.type=cloud_run_job" --limit 50

# 即時日誌
gcloud logging tail "resource.type=cloud_run_job"

# 錯誤日誌
gcloud logging read "resource.type=cloud_run_job AND severity>=ERROR" --limit 20
```

## 🎯 架構

```
Cloud Scheduler (定時器)
    ↓ 觸發
Cloud Run Jobs (交易機器人)
    ↓ 執行
Trading Logic (策略 + 風控)
    ↓ API 呼叫
MEXC Exchange + Redis
```

## ✅ 需求滿足

- [x] 定時觸發: Cloud Scheduler
- [x] 策略討論: 完整文檔
- [x] Cloud Run Jobs: 批次執行
- [x] 免費額度: 前 3 個免費
- [x] 無腳本: 純 gcloud 命令

## 🔍 故障排除

### Scheduler 無法觸發

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

---

**完成！開始使用自動化交易系統。** 🎉
