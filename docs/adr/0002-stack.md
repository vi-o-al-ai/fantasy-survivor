# 0002. Core stack

Date: 2026-09-02
Status: Accepted

## Context

Requirements: Python backend, AWS as cloud provider, Terraform for
infrastructure, Auth0 for accounts, a web frontend now and a mobile app
later, a place to store stats. Start small, but with practices that hold
up as it grows.

## Decision

| Concern      | Choice                          | Why                                                                                         |
| ------------ | ------------------------------- | ------------------------------------------------------------------------------------------- |
| API          | FastAPI on AWS Lambda via Mangum | Typed, generates OpenAPI (the mobile contract), near-zero cost at low traffic.               |
| Storage      | DynamoDB, single table          | Serverless, no idle cost, fits key-based access patterns (season → contestants → stats).    |
| Auth         | Auth0, RS256 JWTs               | Backend verifies tokens against Auth0 JWKS; frontend and mobile use official Auth0 SDKs.    |
| Frontend     | React + TypeScript + Vite       | Widely known, static build served from S3 + CloudFront.                                     |
| Infra        | Terraform, module per concern   | One root per environment, remote state in S3 with DynamoDB locking.                         |
| Packaging    | Monorepo                        | One CI, atomic changes across API and client while the team is small.                       |

## Consequences

- Lambda cold starts are acceptable for a hobby-scale app. If latency
  matters later, the same container image can run on ECS/Fargate with
  Terraform changes only.
- DynamoDB access patterns must be designed up front (phase 4). Ad-hoc
  queries are not a strength; if analytics grows, export to S3/Athena.
- Auth0 free tier covers early usage. Role/permission claims live in the
  token so the backend stays stateless about users.
