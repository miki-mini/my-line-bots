# Secret Manager のシークレット定
# 注意: Terraformでは「シークレットの箱」を作成します。値そのもの（ペイロード）は
# セキュリティの観点からTerraformのコードには含めず、
# コンソールやコマンドライン、あるいは別途シークレット管理ツールから設定することを推奨します。

resource "google_secret_manager_secret" "line_channel_access_token" {
  secret_id = "LINE_CHANNEL_ACCESS_TOKEN"
  replication {
    auto {}
  }
}

resource "google_secret_manager_secret" "line_channel_secret" {
  secret_id = "LINE_CHANNEL_SECRET"
  replication {
    auto {}
  }
}

resource "google_secret_manager_secret" "voicevox_url" {
  secret_id = "VOICEVOX_URL"
  replication {
    auto {}
  }
}

resource "google_secret_manager_secret" "gcs_bucket_name" {
  secret_id = "GCS_BUCKET_NAME"
  replication {
    auto {}
  }
}

resource "google_secret_manager_secret" "gcp_project_id" {
  secret_id = "GCP_PROJECT_ID"
  replication {
    auto {}
  }
}
