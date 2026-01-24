
# ------------------------------------------------------------------------------
# IAM権限の伝播待ち (Time Sleep)
# ------------------------------------------------------------------------------
# サービスアカウントを作成し、Secret Accessor権限を付与した後、
# Cloud Runがその権限を認識するまでに（特に初回は）数十秒のラグが発生することがあります。
# これを防ぐため、権限付与後に30秒間待機します。
resource "time_sleep" "wait_for_iam" {
  depends_on = [ google_project_iam_member.secret_accessor ]

  create_duration = "30s"
}

resource "google_cloud_run_v2_service" "voidoll_bot" {
  name     = var.service_name
  location = var.region
  ingress  = "INGRESS_TRAFFIC_ALL"

  deletion_protection = false

  template {
    service_account = google_service_account.cloud_run_sa.email

    containers {
      # 初期デプロイ用のプレースホルダーイメージ (Cloud Run Hello World)
      # これにより、まだアプリのイメージがArtifact RegistryになくてもTerraformが成功します。
      image = "us-docker.pkg.dev/cloudrun/container/hello"


      resources {
        limits = {
          cpu    = "1"
          memory = "1Gi"
        }
      }

      # 環境変数設定 (Secret Manager からの読み込み)
      # 環境変数設定 (Secret Manager からの読み込み)
      env {
        name = "LINE_CHANNEL_ACCESS_TOKEN"
        value_source {
          secret_key_ref {
            secret = google_secret_manager_secret.line_channel_access_token.secret_id
            version = "latest"
          }
        }
      }
      env {
        name = "LINE_CHANNEL_SECRET"
        value_source {
          secret_key_ref {
            secret = google_secret_manager_secret.line_channel_secret.secret_id
            version = "latest"
          }
        }
      }
      # Voidoll用の環境変数 (中身はLINE_CHANNEL_...と同じシークレットを参照)
      env {
        name = "VOIDOLL_ACCESS_TOKEN"
        value_source {
          secret_key_ref {
            secret = google_secret_manager_secret.line_channel_access_token.secret_id
            version = "latest"
          }
        }
      }
      env {
        name = "VOIDOLL_CHANNEL_SECRET"
        value_source {
          secret_key_ref {
            secret = google_secret_manager_secret.line_channel_secret.secret_id
            version = "latest"
          }
        }
      }
      env {
        name = "VOICEVOX_URL"
        value_source {
          secret_key_ref {
            secret = google_secret_manager_secret.voicevox_url.secret_id
            version = "latest"
          }
        }
      }
      env {
        name = "GCS_BUCKET_NAME"
        value_source {
          secret_key_ref {
            secret = google_secret_manager_secret.gcs_bucket_name.secret_id
            version = "latest"
          }
        }
      }
      env {
        name = "GCP_PROJECT_ID"
        value_source {
          secret_key_ref {
            secret = google_secret_manager_secret.gcp_project_id.secret_id
            version = "latest"
          }
        }
      }
    }
  }

  traffic {
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
    percent = 100
  }

  # 依存関係の明示 (Sleepリソースに依存させることで待機を強制)
  depends_on = [ time_sleep.wait_for_iam ]

  # CI/CD (GitHub Actions) が新しいイメージをデプロイした後に
  # Terraformが「設定と違う！」と戻してしまわないように、イメージの変更を無視します。
  lifecycle {
    ignore_changes = [
      template[0].containers[0].image
    ]
  }
}

# 未認証アクセスを許可 (Public Access)
resource "google_cloud_run_service_iam_member" "noauth" {
  location = google_cloud_run_v2_service.voidoll_bot.location
  service  = google_cloud_run_v2_service.voidoll_bot.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}
