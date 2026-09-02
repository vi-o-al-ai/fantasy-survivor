variable "project" {
  description = "Project slug used in resource names."
  type        = string
  default     = "fantasy-survivor"
}

variable "region" {
  description = "AWS region for the state bucket and lock table."
  type        = string
  default     = "us-east-1"
}

variable "github_repository" {
  description = "GitHub repo allowed to assume the deploy role, as owner/name."
  type        = string
}

variable "deploy_branches" {
  description = "Branches whose workflows may deploy."
  type        = list(string)
  default     = ["main"]
}
