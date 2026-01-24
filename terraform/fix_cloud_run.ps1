$PROJECT_ID = "usaginooekaki"
$REGION = "asia-northeast1"
$SERVICE_NAME = "voidoll-bot"

Write-Host "以前の適用失敗で残ってしまった $SERVICE_NAME の削除保護を解除します..."

# 削除保護を無効化
gcloud run services update $SERVICE_NAME --region $REGION --project $PROJECT_ID --no-deletion-protection

Write-Host "Done. Now 'terraform apply' should work!"
