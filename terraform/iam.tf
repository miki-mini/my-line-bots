# ==============================================================================
# Cloud Run 用サービスアカウント
# ==============================================================================
resource "google_service_account" "cloud_run_sa" {
  account_id   = "${var.service_name}-sa"
  display_name = "Cloud Run Service Account for ${var.service_name}"
}

# Secret Manager へのアクセス権限 (Secret Accessor)
resource "google_project_iam_member" "secret_accessor" {
  project = var.project_id
  role    = "roles/secretmanager.secretAccessor"
  member  = "serviceAccount:${google_service_account.cloud_run_sa.email}"
}

# 他に必要な権限があればここに追加（例: Firestore, Vertex AIなど）
# resource "google_project_iam_member" "vertex_ai_user" {
#   project = var.project_id
#   role    = "roles/aiplatform.user"
#   member  = "serviceAccount:${google_service_account.cloud_run_sa.email}"
# }

# ==============================================================================
# Workload Identity Federation (GitHub Actions 用)
# ==============================================================================
resource "google_iam_workload_identity_pool" "github_pool" {
  workload_identity_pool_id = "github-actions-pool"
  display_name              = "GitHub Actions Pool"
  description               = "Identity pool for GitHub Actions"
}

resource "google_iam_workload_identity_pool_provider" "github_provider" {
  workload_identity_pool_id          = google_iam_workload_identity_pool.github_pool.workload_identity_pool_id
  workload_identity_pool_provider_id = "github-actions-provider"
  display_name                       = "GitHub Actions Provider"
  description                        = "OIDC identity provider for GitHub Actions"

  attribute_mapping = {
    "google.subject"       = "assertion.sub"
    "attribute.actor"      = "assertion.actor"
    "attribute.repository" = "assertion.repository"
  }

  # エラー回避のため明示的な条件を追加
  attribute_condition = "assertion.repository == '${var.github_repository}'"

  oidc {
    issuer_uri = "https://token.actions.githubusercontent.com"
  }
}

# GitHub Actions が使用するサービスアカウント (Deployer)
resource "google_service_account" "github_actions_sa" {
  account_id   = "github-actions-deployer"
  display_name = "GitHub Actions Deployer"
}

# GitHub Actions からのなりすましを許可 (Workload Identity User)
resource "google_service_account_iam_member" "workload_identity_user" {
  service_account_id = google_service_account.github_actions_sa.name
  role               = "roles/iam.workloadIdentityUser"

  # 特定のリポジトリ（var.github_repository）からのアクセスのみを許可
  member = "principalSet://iam.googleapis.com/${google_iam_workload_identity_pool.github_pool.name}/attribute.repository/${var.github_repository}"
}

# ==============================================================================
# GitHub Actions 用サービスアカウントへの権限付与
# ==============================================================================

# Artifact Registry への書き込み権限
resource "google_project_iam_member" "artifact_registry_writer" {
  project = var.project_id
  role    = "roles/artifactregistry.writer"
  member  = "serviceAccount:${google_service_account.github_actions_sa.email}"
}

# Cloud Run へのデプロイ権限 (Developer)
resource "google_project_iam_member" "cloud_run_developer" {
  project = var.project_id
  role    = "roles/run.developer"
  member  = "serviceAccount:${google_service_account.github_actions_sa.email}"
}

# Cloud Run 実行用サービスアカウントを使用する権限 (Service Account User)
resource "google_service_account_iam_member" "cloud_run_sa_user" {
  service_account_id = google_service_account.cloud_run_sa.name
  role               = "roles/iam.serviceAccountUser"
  member             = "serviceAccount:${google_service_account.github_actions_sa.email}"
}
