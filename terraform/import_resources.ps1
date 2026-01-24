$PROJECT_ID = "usaginooekaki"
$REGION = "asia-northeast1"

Write-Host "以前に手動で作成したリソースをTerraformに取り込みます..."

# Secret Manager Keys
# 既に存在しているシークレットを取り込みます
Write-Host "Importing Secret Manager Secrets..."
terraform import google_secret_manager_secret.line_channel_access_token projects/$PROJECT_ID/secrets/LINE_CHANNEL_ACCESS_TOKEN
terraform import google_secret_manager_secret.line_channel_secret projects/$PROJECT_ID/secrets/LINE_CHANNEL_SECRET
terraform import google_secret_manager_secret.voicevox_url projects/$PROJECT_ID/secrets/VOICEVOX_URL
terraform import google_secret_manager_secret.gcs_bucket_name projects/$PROJECT_ID/secrets/GCS_BUCKET_NAME
terraform import google_secret_manager_secret.gcp_project_id projects/$PROJECT_ID/secrets/GCP_PROJECT_ID

# Workload Identity Federation
Write-Host "Importing Workload Identity Federation..."
terraform import google_iam_workload_identity_pool.github_pool projects/$PROJECT_ID/locations/global/workloadIdentityPools/github-actions-pool
terraform import google_iam_workload_identity_pool_provider.github_provider projects/$PROJECT_ID/locations/global/workloadIdentityPools/github-actions-pool/providers/github-actions-provider

# Artifact Registry
Write-Host "Importing Artifact Registry..."
terraform import google_artifact_registry_repository.repo projects/$PROJECT_ID/locations/$REGION/repositories/my-bot-repo

# Cloud Run
Write-Host "Importing Cloud Run..."
terraform import google_cloud_run_v2_service.voidoll_bot projects/$PROJECT_ID/locations/$REGION/services/voidoll-bot

Write-Host "完了しました。もう一度 'terraform plan' を実行して差分を確認してください。"
Write-Host "※もしサービスアカウント等の取り込みエラーが出た場合は、別途個別に取り込むか、terraform applyで作成されるのに任せてください。"
