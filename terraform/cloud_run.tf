
# ------------------------------------------------------------------------------
# IAM権限の伝播待ち (Time Sleep)
# ------------------------------------------------------------------------------
# サービスアカウントを作成し、Secret Accessor権限を付与した後、
# Cloud Runがその権限を認識するまでに（特に初回は）数十秒のラグが発生することがあります。
# これを防ぐため、権限付与後に30秒間待機します。
resource "time_sleep" "wait_for_iam" {
  depends_on = [google_project_iam_member.secret_accessor]

  create_duration = "30s"
}

resource "google_cloud_run_v2_service" "voidoll_bot" {
  name     = var.service_name
  location = var.region
  ingress  = "INGRESS_TRAFFIC_ALL"

  deletion_protection = false

  template {
    service_account = google_service_account.cloud_run_sa.email

    scaling {
      min_instance_count = 0
      max_instance_count = 3
    }

    containers {
      # 初期デプロイ用のプレースホルダーイメージ (Cloud Run Hello World)
      # これにより、まだアプリのイメージがArtifact RegistryになくてもTerraformが成功します。
      image = "us-docker.pkg.dev/cloudrun/container/hello"


      resources {
        limits = {
          cpu    = "1"
          memory = "512Mi"
        }
        # リクエスト処理中のみCPUを割り当て（アイドル時のCPU課金を防止）
        cpu_idle = true
        # コールドスタート時にCPUをブーストして起動を高速化
        startup_cpu_boost = true
      }

      # 環境変数設定 (Secret Manager からの読み込み)
      # 環境変数設定 (Secret Manager からの読み込み)
      env {
        name = "LINE_CHANNEL_ACCESS_TOKEN"
        value_source {
          secret_key_ref {
            secret  = google_secret_manager_secret.line_channel_access_token.secret_id
            version = "latest"
          }
        }
      }
      env {
        name = "LINE_CHANNEL_SECRET"
        value_source {
          secret_key_ref {
            secret  = google_secret_manager_secret.line_channel_secret.secret_id
            version = "latest"
          }
        }
      }
      # Voidoll用の環境変数 (中身はLINE_CHANNEL_...と同じシークレットを参照)
      env {
        name = "VOIDOLL_ACCESS_TOKEN"
        value_source {
          secret_key_ref {
            secret  = google_secret_manager_secret.line_channel_access_token.secret_id
            version = "latest"
          }
        }
      }
      env {
        name = "VOIDOLL_CHANNEL_SECRET"
        value_source {
          secret_key_ref {
            secret  = google_secret_manager_secret.line_channel_secret.secret_id
            version = "latest"
          }
        }
      }
      env {
        name = "VOICEVOX_URL"
        value_source {
          secret_key_ref {
            secret  = google_secret_manager_secret.voicevox_url.secret_id
            version = "latest"
          }
        }
      }
      env {
        name = "GCS_BUCKET_NAME"
        value_source {
          secret_key_ref {
            secret  = google_secret_manager_secret.gcs_bucket_name.secret_id
            version = "latest"
          }
        }
      }
      env {
        name  = "GCP_PROJECT_ID"
        value = var.project_id
      }

      # --------------------------------------------------------------------------------
      # Bot-Specific Tokens (各ボット固有のLINEチャネルシークレット)
      # --------------------------------------------------------------------------------

      # 🦡 Mole
      env {
        name = "TRAIN_ACCESS_TOKEN"
        value_source {
          secret_key_ref {
            secret  = data.google_secret_manager_secret.train_access_token.secret_id
            version = "latest"
          }
        }
      }
      env {
        name = "TRAIN_CHANNEL_SECRET"
        value_source {
          secret_key_ref {
            secret  = data.google_secret_manager_secret.train_channel_secret.secret_id
            version = "latest"
          }
        }
      }

      # 🦊 Fox
      env {
        name = "FOX_ACCESS_TOKEN"
        value_source {
          secret_key_ref {
            secret  = data.google_secret_manager_secret.fox_access_token.secret_id
            version = "latest"
          }
        }
      }
      env {
        name = "FOX_CHANNEL_SECRET"
        value_source {
          secret_key_ref {
            secret  = data.google_secret_manager_secret.fox_channel_secret.secret_id
            version = "latest"
          }
        }
      }

      # 🐸 Frog
      env {
        name = "FROG_ACCESS_TOKEN"
        value_source {
          secret_key_ref {
            secret  = data.google_secret_manager_secret.frog_access_token.secret_id
            version = "latest"
          }
        }
      }
      env {
        name = "FROG_CHANNEL_SECRET"
        value_source {
          secret_key_ref {
            secret  = data.google_secret_manager_secret.frog_channel_secret.secret_id
            version = "latest"
          }
        }
      }

      # 🐧 Penguin
      env {
        name = "PENGUIN_ACCESS_TOKEN"
        value_source {
          secret_key_ref {
            secret  = data.google_secret_manager_secret.penguin_access_token.secret_id
            version = "latest"
          }
        }
      }
      env {
        name = "PENGUIN_CHANNEL_SECRET"
        value_source {
          secret_key_ref {
            secret  = data.google_secret_manager_secret.penguin_channel_secret.secret_id
            version = "latest"
          }
        }
      }

      # 🐹 Capybara
      env {
        name = "CAPYBARA_ACCESS_TOKEN"
        value_source {
          secret_key_ref {
            secret  = data.google_secret_manager_secret.capybara_access_token.secret_id
            version = "latest"
          }
        }
      }
      env {
        name = "CAPYBARA_CHANNEL_SECRET"
        value_source {
          secret_key_ref {
            secret  = data.google_secret_manager_secret.capybara_channel_secret.secret_id
            version = "latest"
          }
        }
      }

      # 🐋 Whale
      env {
        name = "WHALE_ACCESS_TOKEN"
        value_source {
          secret_key_ref {
            secret  = data.google_secret_manager_secret.whale_access_token.secret_id
            version = "latest"
          }
        }
      }
      env {
        name = "WHALE_CHANNEL_SECRET"
        value_source {
          secret_key_ref {
            secret  = data.google_secret_manager_secret.whale_channel_secret.secret_id
            version = "latest"
          }
        }
      }

      # 🦫 Beaver
      env {
        name = "BEAVER_ACCESS_TOKEN"
        value_source {
          secret_key_ref {
            secret  = data.google_secret_manager_secret.beaver_access_token.secret_id
            version = "latest"
          }
        }
      }
      env {
        name = "BEAVER_CHANNEL_SECRET"
        value_source {
          secret_key_ref {
            secret  = data.google_secret_manager_secret.beaver_channel_secret.secret_id
            version = "latest"
          }
        }
      }

      # 🦇 Bat
      env {
        name = "BAT_ACCESS_TOKEN"
        value_source {
          secret_key_ref {
            secret  = data.google_secret_manager_secret.bat_access_token.secret_id
            version = "latest"
          }
        }
      }
      env {
        name = "BAT_CHANNEL_SECRET"
        value_source {
          secret_key_ref {
            secret  = data.google_secret_manager_secret.bat_channel_secret.secret_id
            version = "latest"
          }
        }
      }

      # 🐰 Rabbit / 🦉 Owl
      # Secret Managerに値が設定されていないため、Cloud Runの環境変数からは除外
      # トークンを設定したら、ここに env ブロックを追加すること
    }
  }

  traffic {
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
    percent = 100
  }

  # 依存関係の明示 (Sleepリソースに依存させることで待機を強制)
  depends_on = [time_sleep.wait_for_iam]

  # CI/CD (GitHub Actions) が新しいイメージをデプロイした後に
  # Terraformが「設定と違う！」と戻してしまわないように、イメージの変更を無視します。
  lifecycle {
    ignore_changes = [
      template[0].containers[0].image,
      template[0].labels,
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
