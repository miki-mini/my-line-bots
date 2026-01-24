$PROJECT_ID = "usaginooekaki"
$REGION = "asia-northeast1"

Write-Host "Checking Cloud Run Services in $REGION..."
gcloud run services list --region $REGION --project $PROJECT_ID

Write-Host "`nChecking Workload Identity Pool Providers..."
gcloud iam workload-identity-pools providers list --workload-identity-pool="github-actions-pool" --location="global" --project $PROJECT_ID
