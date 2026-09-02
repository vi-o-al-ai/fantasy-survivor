# 0005. Deployment topology on AWS

Date: 2026-09-02
Status: Accepted

## Context

The app must run cheaply when idle, deploy from CI with Terraform, and
keep the option of a mobile client hitting the same API.

## Decision

- **API:** one Lambda function (Python 3.12, x86_64) running FastAPI via
  Mangum behind an API Gateway HTTP API with a single `$default` route.
  FastAPI does the routing; API Gateway handles CORS, throttling, and
  access logs. The function's IAM role allows only `GetItem`, `PutItem`,
  and `Query` on the one table.
- **Data:** one DynamoDB table, on-demand billing, encryption on, PITR
  off in dev (on in prod).
- **Web:** a private S3 bucket served through CloudFront with Origin
  Access Control. 403/404 rewrite to `index.html` for client-side routes.
- **State:** S3 backend with DynamoDB locking, created once by
  `infra/bootstrap`. Each environment is its own root under `infra/envs/`
  with its own state key.
- **Packaging:** `backend/scripts/build_lambda.sh` resolves wheels for
  the Lambda platform, so the zip is reproducible from any developer
  machine or CI runner.

## Consequences

- Cold starts of roughly a second on first request after idle. Fine for
  a fantasy league; revisit with provisioned concurrency or containers
  if it matters.
- Zip deploys cap at 50 MB. The current package is about 24 MB; a move
  to container images is a module change, not an app change.
- Provider lock files are committed and currently carry only the
  `linux_amd64` hash. Run `terraform providers lock -platform=darwin_arm64`
  (or your platform) once to add others.
- No custom domain or WAF yet. Both attach to the existing CloudFront
  and API Gateway resources without restructuring.
