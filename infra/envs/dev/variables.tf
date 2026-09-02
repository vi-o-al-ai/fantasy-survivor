variable "region" {
  type    = string
  default = "us-east-1"
}

variable "project" {
  type    = string
  default = "fantasy-survivor"
}

variable "environment" {
  type    = string
  default = "dev"
}

variable "auth0_domain" {
  description = "Auth0 tenant domain, e.g. your-tenant.us.auth0.com"
  type        = string
}

variable "auth0_audience" {
  description = "Auth0 API identifier the backend accepts as audience."
  type        = string
}

variable "lambda_zip_path" {
  description = "Path to backend/lambda.zip built by backend/scripts/build_lambda.sh"
  type        = string
  default     = "../../../backend/lambda.zip"
}

variable "extra_cors_origins" {
  description = "Additional browser origins (e.g. http://localhost:5173 for dev)."
  type        = list(string)
  default     = ["http://localhost:5173"]
}
