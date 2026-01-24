terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = ">= 5.0.0"
    }
    time = {
      source  = "hashicorp/time"
      version = ">= 0.9.0"
    }
  }
  required_version = ">= 1.5.0"
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# 将来的にはGCSバックエンドを推奨しますが、まずはローカルステートで進めます
# terraform {
#   backend "gcs" {
#     bucket  = "YOUR_TERRAFORM_STATE_BUCKET"
#     prefix  = "terraform/state"
#   }
# }
