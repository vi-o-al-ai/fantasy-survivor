output "api_url" {
  value = module.api.url
}

output "web_url" {
  value = module.frontend.url
}

output "web_bucket" {
  value = module.frontend.bucket
}

output "web_distribution_id" {
  value = module.frontend.distribution_id
}

output "lambda_function_name" {
  value = module.api.function_name
}
