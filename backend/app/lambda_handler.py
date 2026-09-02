"""AWS Lambda entrypoint. API Gateway (HTTP API v2) events -> ASGI via Mangum."""

from mangum import Mangum

from app.main import app

handler = Mangum(app, lifespan="off")
