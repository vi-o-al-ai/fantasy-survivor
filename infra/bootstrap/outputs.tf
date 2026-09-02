output "state_bucket" {
  value = aws_s3_bucket.state.bucket
}

output "lock_table" {
  value = aws_dynamodb_table.lock.name
}

output "backend_config" {
  description = "Paste into envs/<env>/backend.hcl"
  value       = <<-EOT
    bucket         = "${aws_s3_bucket.state.bucket}"
    dynamodb_table = "${aws_dynamodb_table.lock.name}"
    region         = "${var.region}"
  EOT
}
