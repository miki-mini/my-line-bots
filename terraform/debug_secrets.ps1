$PROJECT_ID = "usaginooekaki"
$SA_EMAIL = "voidoll-bot-sa@usaginooekaki.iam.gserviceaccount.com"

Write-Host "Checking Secret Versions..."
foreach ($secret in @("LINE_CHANNEL_ACCESS_TOKEN", "LINE_CHANNEL_SECRET", "VOICEVOX_URL", "GCS_BUCKET_NAME", "GCP_PROJECT_ID")) {
    Write-Host "Checking $secret..."
    gcloud secrets versions list $secret --project $PROJECT_ID --limit 1 --format="table(name, state)"
}

Write-Host "`nChecking IAM Role for $SA_EMAIL..."
$policy = gcloud projects get-iam-policy $PROJECT_ID --flatten="bindings[].members" --filter="bindings.role:roles/secretmanager.secretAccessor" --format="value(bindings.members)"

if ($policy -like "*$SA_EMAIL*") {
    Write-Host "SUCCESS: Service Account has Secret Accessor role." -ForegroundColor Green
}
else {
    Write-Host "FAILURE: Service Account does NOT have Secret Accessor role." -ForegroundColor Red
    Write-Host "Current members with 'roles/secretmanager.secretAccessor':"
    Write-Host $policy
}
