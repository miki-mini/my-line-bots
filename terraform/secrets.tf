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

# ------------------------------------------------------------------------------
# Bot-Specific LINE Channel Tokens (既存のSecret Managerシークレットを参照)
# 各ボットは個別のLINE Messaging APIチャネルを持つ
# ------------------------------------------------------------------------------

# 🦡 Mole (Train)
data "google_secret_manager_secret" "train_access_token" {
  secret_id = "TRAIN_ACCESS_TOKEN"
}
data "google_secret_manager_secret" "train_channel_secret" {
  secret_id = "TRAIN_CHANNEL_SECRET"
}

# 🦊 Fox
data "google_secret_manager_secret" "fox_access_token" {
  secret_id = "FOX_ACCESS_TOKEN"
}
data "google_secret_manager_secret" "fox_channel_secret" {
  secret_id = "FOX_CHANNEL_SECRET"
}

# 🐸 Frog (Weather)
data "google_secret_manager_secret" "frog_access_token" {
  secret_id = "FROG_ACCESS_TOKEN"
}
data "google_secret_manager_secret" "frog_channel_secret" {
  secret_id = "FROG_CHANNEL_SECRET"
}

# 🐧 Penguin
data "google_secret_manager_secret" "penguin_access_token" {
  secret_id = "PENGUIN_ACCESS_TOKEN"
}
data "google_secret_manager_secret" "penguin_channel_secret" {
  secret_id = "PENGUIN_CHANNEL_SECRET"
}

# 🐹 Capybara (News)
data "google_secret_manager_secret" "capybara_access_token" {
  secret_id = "CAPYBARA_ACCESS_TOKEN"
}
data "google_secret_manager_secret" "capybara_channel_secret" {
  secret_id = "CAPYBARA_CHANNEL_SECRET"
}

# 🐋 Whale
data "google_secret_manager_secret" "whale_access_token" {
  secret_id = "WHALE_ACCESS_TOKEN"
}
data "google_secret_manager_secret" "whale_channel_secret" {
  secret_id = "WHALE_CHANNEL_SECRET"
}

# 🦫 Beaver
data "google_secret_manager_secret" "beaver_access_token" {
  secret_id = "BEAVER_ACCESS_TOKEN"
}
data "google_secret_manager_secret" "beaver_channel_secret" {
  secret_id = "BEAVER_CHANNEL_SECRET"
}

# 🦇 Bat
data "google_secret_manager_secret" "bat_access_token" {
  secret_id = "BAT_ACCESS_TOKEN"
}
data "google_secret_manager_secret" "bat_channel_secret" {
  secret_id = "BAT_CHANNEL_SECRET"
}

# 🐰 Rabbit (Secret Manager未作成のため新規作成)
resource "google_secret_manager_secret" "rabbit_access_token" {
  secret_id = "RABBIT_ACCESS_TOKEN"
  replication {
    auto {}
  }
}
resource "google_secret_manager_secret" "rabbit_channel_secret" {
  secret_id = "RABBIT_CHANNEL_SECRET"
  replication {
    auto {}
  }
}

# 🦉 Owl (Secret Manager未作成のため新規作成)
resource "google_secret_manager_secret" "owl_access_token" {
  secret_id = "OWL_ACCESS_TOKEN"
  replication {
    auto {}
  }
}
resource "google_secret_manager_secret" "owl_channel_secret" {
  secret_id = "OWL_CHANNEL_SECRET"
  replication {
    auto {}
  }
}

# ------------------------------------------------------------------------------
# Shared Secrets
# ------------------------------------------------------------------------------

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
