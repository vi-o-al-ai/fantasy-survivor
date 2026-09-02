# Copy to backend.hcl (git-ignored). Values come from `terraform output` in infra/bootstrap.
bucket         = "fantasy-survivor-tfstate-123456789012"
dynamodb_table = "fantasy-survivor-tfstate-lock"
region         = "us-east-1"
