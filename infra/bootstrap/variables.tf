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
