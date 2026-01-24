resource "google_artifact_registry_repository" "repo" {
  location      = var.region
  repository_id = var.repository_name
  description   = "Production Docker images for LINE Bot"
  format        = "DOCKER"
}
