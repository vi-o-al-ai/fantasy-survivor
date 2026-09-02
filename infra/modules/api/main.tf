# FastAPI on Lambda behind an API Gateway HTTP API (v2). The whole API is a
# single function with a $default route; FastAPI does the routing.

data "aws_iam_policy_document" "assume" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "lambda" {
  name               = "${var.name}-lambda"
  assume_role_policy = data.aws_iam_policy_document.assume.json
  tags               = var.tags
}

resource "aws_iam_role_policy_attachment" "basic_logs" {
  role       = aws_iam_role.lambda.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# Least privilege: only the actions the store uses, only on this table.
data "aws_iam_policy_document" "table" {
  statement {
    actions = [
      "dynamodb:GetItem",
      "dynamodb:PutItem",
      "dynamodb:Query",
    ]
    resources = [var.dynamodb_table_arn]
  }
}

resource "aws_iam_role_policy" "table" {
  name   = "dynamodb-access"
  role   = aws_iam_role.lambda.id
  policy = data.aws_iam_policy_document.table.json
}

resource "aws_cloudwatch_log_group" "lambda" {
  name              = "/aws/lambda/${var.name}"
  retention_in_days = var.log_retention_days
  tags              = var.tags
}

resource "aws_lambda_function" "api" {
  function_name    = var.name
  role             = aws_iam_role.lambda.arn
  runtime          = "python3.12"
  architectures    = ["x86_64"]
  handler          = "app.lambda_handler.handler"
  filename         = var.lambda_zip_path
  source_code_hash = filebase64sha256(var.lambda_zip_path)
  memory_size      = var.memory_mb
  timeout          = var.timeout_seconds

  environment {
    variables = var.environment
  }

  depends_on = [aws_cloudwatch_log_group.lambda]
  tags       = var.tags
}

resource "aws_apigatewayv2_api" "http" {
  name          = var.name
  protocol_type = "HTTP"

  cors_configuration {
    allow_origins     = var.cors_origins
    allow_methods     = ["GET", "PUT", "POST", "DELETE", "OPTIONS"]
    allow_headers     = ["authorization", "content-type"]
    allow_credentials = true
    max_age           = 3600
  }

  tags = var.tags
}

resource "aws_apigatewayv2_integration" "lambda" {
  api_id                 = aws_apigatewayv2_api.http.id
  integration_type       = "AWS_PROXY"
  integration_uri        = aws_lambda_function.api.invoke_arn
  payload_format_version = "2.0"
}

resource "aws_apigatewayv2_route" "default" {
  api_id    = aws_apigatewayv2_api.http.id
  route_key = "$default"
  target    = "integrations/${aws_apigatewayv2_integration.lambda.id}"
}

resource "aws_cloudwatch_log_group" "api_access" {
  name              = "/aws/apigateway/${var.name}"
  retention_in_days = var.log_retention_days
  tags              = var.tags
}

resource "aws_apigatewayv2_stage" "default" {
  api_id      = aws_apigatewayv2_api.http.id
  name        = "$default"
  auto_deploy = true

  access_log_settings {
    destination_arn = aws_cloudwatch_log_group.api_access.arn
    format = jsonencode({
      requestId = "$context.requestId"
      ip        = "$context.identity.sourceIp"
      method    = "$context.httpMethod"
      path      = "$context.path"
      status    = "$context.status"
      latencyMs = "$context.responseLatency"
      error     = "$context.integrationErrorMessage"
    })
  }

  default_route_settings {
    throttling_burst_limit = 50
    throttling_rate_limit  = 25
  }

  tags = var.tags
}

resource "aws_lambda_permission" "apigw" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.api.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.http.execution_arn}/*/*"
}
