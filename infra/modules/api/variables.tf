variable "name" {
  description = "Base name for the function, role, and API."
  type        = string
}

variable "lambda_zip_path" {
  description = "Path to the built backend/lambda.zip."
  type        = string
}

variable "environment" {
  description = "Environment variables for the function (APP_ENV, AUTH0_*, ...)."
  type        = map(string)
}

variable "dynamodb_table_arn" {
  type = string
}

variable "cors_origins" {
  description = "Browser origins allowed by API Gateway."
  type        = list(string)
}

variable "log_retention_days" {
  type    = number
  default = 14
}

variable "memory_mb" {
  type    = number
  default = 512
}

variable "timeout_seconds" {
  type    = number
  default = 10
}

variable "tags" {
  type    = map(string)
  default = {}
}
