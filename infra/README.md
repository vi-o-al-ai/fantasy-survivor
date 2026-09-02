# Infrastructure

Terraform for everything in AWS. One module per concern, one root per
environment. Nothing here is required to run the app locally.

```
infra/
  bootstrap/        one-off: S3 bucket + DynamoDB lock table for remote state
  modules/
    dynamodb/       the single application table
    api/            Lambda + API Gateway HTTP API + IAM + logs
    frontend/       private S3 bucket + CloudFront (SPA fallback)
  envs/
    dev/            wires the modules together for dev
```

## First-time setup (once per AWS account)

```sh
cd infra/bootstrap
terraform init && terraform apply
terraform output backend_config      # paste into ../envs/dev/backend.hcl
```

## Deploying dev

```sh
# 1. Build the Lambda package
backend/scripts/build_lambda.sh

# 2. Plan / apply
cd infra/envs/dev
cp dev.example.tfvars dev.tfvars        # fill in Auth0 values
cp backend.example.hcl backend.hcl      # from bootstrap output
terraform init -backend-config=backend.hcl
terraform plan -var-file=dev.tfvars
terraform apply -var-file=dev.tfvars

# 3. Note the outputs; the frontend build needs api_url
terraform output
```

Uploading the frontend build to the bucket is done by the deploy
pipeline (phase 8); by hand it is `aws s3 sync frontend/dist s3://<web_bucket>`
followed by a CloudFront invalidation.

## Conventions

- `terraform fmt -recursive` and `terraform validate` run in CI.
- Secrets never go in `.tfvars` committed to git; `*.tfvars` is ignored,
  `*.example.tfvars` is not. Auth0 domain and audience are not secrets.
- Lambda gets least-privilege IAM: only the DynamoDB actions the store
  uses, on the one table.
- Add a `prod` root by copying `envs/dev` and changing `environment`,
  enabling `point_in_time_recovery` on the table.
