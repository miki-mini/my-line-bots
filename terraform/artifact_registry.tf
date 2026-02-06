resource "google_artifact_registry_repository" "repo" {
  location      = var.region
  repository_id = var.repository_name
  description   = "Production Docker images for LINE Bot"
  format        = "DOCKER"

  cleanup_policies {
    id     = "delete-old-images"
    action = "DELETE"
    condition {
      tag_state  = "ANY"
      older_than = "1209600s" # 14 days
    }
  }

  cleanup_policies {
    id     = "keep-recent-5"
    action = "KEEP"
    most_recent_versions {
      keep_count = 5
    }
  }
}
