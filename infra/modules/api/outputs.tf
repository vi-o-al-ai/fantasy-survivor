output "url" {
  description = "Base URL of the API."
  value       = aws_apigatewayv2_api.http.api_endpoint
}

output "function_name" {
  value = aws_lambda_function.api.function_name
}
