"""The Lambda entrypoint must translate API Gateway HTTP API (v2) events."""

import json
from types import SimpleNamespace
from typing import Any, cast

from mangum.types import LambdaContext

CONTEXT = cast(
    LambdaContext,
    SimpleNamespace(
        function_name="api",
        memory_limit_in_mb=512,
        invoked_function_arn="arn:aws:lambda:us-east-1:123456789012:function:api",
        aws_request_id="req",
        get_remaining_time_in_millis=lambda: 10_000,
    ),
)


def _apigw_v2_event(path: str, method: str = "GET") -> dict[str, Any]:
    return {
        "version": "2.0",
        "routeKey": "$default",
        "rawPath": path,
        "rawQueryString": "",
        "headers": {"host": "example.execute-api.us-east-1.amazonaws.com"},
        "requestContext": {
            "accountId": "123456789012",
            "apiId": "api",
            "domainName": "example.execute-api.us-east-1.amazonaws.com",
            "http": {
                "method": method,
                "path": path,
                "protocol": "HTTP/1.1",
                "sourceIp": "127.0.0.1",
                "userAgent": "pytest",
            },
            "requestId": "req",
            "stage": "$default",
            "time": "02/Sep/2026:00:00:00 +0000",
            "timeEpoch": 0,
        },
        "isBase64Encoded": False,
    }


def test_handler_serves_health() -> None:
    from app.lambda_handler import handler

    response = handler(_apigw_v2_event("/health"), context=CONTEXT)

    assert response["statusCode"] == 200
    assert json.loads(response["body"])["status"] == "ok"


def test_handler_routes_unknown_path_to_404() -> None:
    from app.lambda_handler import handler

    assert handler(_apigw_v2_event("/nope"), context=CONTEXT)["statusCode"] == 404
