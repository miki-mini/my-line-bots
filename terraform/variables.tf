variable "project_id" {
  description = "Google Cloud Project ID"
  type        = string
  default     = "usaginooekaki"
}

variable "region" {
  description = "Google Cloud region to deploy resources"
  type        = string
  default     = "asia-northeast1"
}

variable "service_name" {
  description = "Cloud Run service name"
  type        = string
  default     = "voidoll-bot"
}

variable "repository_name" {
  description = "Artifact Registry repository name"
  type        = string
  default     = "my-bot-repo"
}

variable "github_repository" {
  description = "The GitHub repository to allow access (format: owner/repo)"
  type        = string
  default     = "miki-mini/my-line-bots"
}
