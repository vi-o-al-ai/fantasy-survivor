provider "aws" {
  region = var.region

  default_tags {
    tags = local.tags
  }
}

locals {
  name = "${var.project}-${var.environment}"
  tags = {
    Project     = var.project
    Environment = var.environment
    ManagedBy   = "terraform"
  }
}

module "frontend" {
  source = "../../modules/frontend"
  name   = "${local.name}-web"
}

module "table" {
  source = "../../modules/dynamodb"
  name   = local.name
}

module "api" {
  source = "../../modules/api"

  name               = "${local.name}-api"
  lambda_zip_path    = var.lambda_zip_path
  dynamodb_table_arn = module.table.arn
  cors_origins       = concat([module.frontend.url], var.extra_cors_origins)

  environment = {
    APP_ENV        = var.environment
    LOG_FORMAT     = "json"
    LOG_LEVEL      = "INFO"
    STORE_BACKEND  = "dynamodb"
    DYNAMODB_TABLE = module.table.name
    AUTH0_DOMAIN   = var.auth0_domain
    AUTH0_AUDIENCE = var.auth0_audience
    CORS_ORIGINS   = jsonencode(concat([module.frontend.url], var.extra_cors_origins))
  }
}
