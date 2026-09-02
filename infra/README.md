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

## Continuous deployment

`.github/workflows/deploy-dev.yml` deploys on every push to `main` that
touches `backend/`, `frontend/`, or `infra/`. It authenticates to AWS with
GitHub OIDC (no stored keys), builds the Lambda zip, applies the dev root,
then builds the frontend against the deployed API URL and syncs it to S3.

### One-time setup

1. Run `infra/bootstrap` with `github_repository` set (see
   `bootstrap.example.tfvars`). It creates the OIDC provider and a deploy
   role scoped to `main` and the `dev` environment.
2. In the GitHub repo, create an **environment** named `dev` and set these
   **variables** (Settings → Secrets and variables → Actions → Variables):

   | Variable               | Value                                            |
   | ---------------------- | ------------------------------------------------ |
   | `AWS_DEPLOY_ROLE_ARN`  | `terraform output deploy_role_arn` from bootstrap |
   | `AWS_REGION`           | e.g. `us-east-1`                                  |
   | `TF_STATE_BUCKET`      | `terraform output state_bucket`                   |
   | `TF_LOCK_TABLE`        | `terraform output lock_table`                     |
   | `AUTH0_DOMAIN`         | Auth0 tenant domain                               |
   | `AUTH0_AUDIENCE`       | Auth0 API identifier                              |
   | `AUTH0_SPA_CLIENT_ID`  | Auth0 Single Page Application client id           |

   None of these are secrets, so plain variables are correct.
3. After the first deploy, add the `web_url` output to the Auth0 SPA's
   allowed callback, logout, and web origins.

Rollback is `git revert` and push. Terraform converges the Lambda to the
reverted package and the frontend sync replaces the bundle.
