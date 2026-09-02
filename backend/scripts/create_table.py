"""Create the DynamoDB table locally (DynamoDB Local) or in AWS.

In AWS the table is normally created by Terraform; this exists for local
development and for the moto-backed tests, which share the definition.

    DYNAMODB_ENDPOINT_URL=http://localhost:8001 python scripts/create_table.py
"""

from __future__ import annotations

import logging
import sys

import boto3
from botocore.exceptions import ClientError

from app.config import get_settings
from app.storage.dynamodb import ATTRIBUTE_DEFINITIONS, KEY_SCHEMA

log = logging.getLogger("create_table")


def create_table(table_name: str, *, region: str, endpoint_url: str | None) -> bool:
    """Create the table. Returns False if it already existed."""
    client = boto3.client("dynamodb", region_name=region, endpoint_url=endpoint_url)
    try:
        client.create_table(
            TableName=table_name,
            KeySchema=KEY_SCHEMA,  # type: ignore[arg-type]
            AttributeDefinitions=ATTRIBUTE_DEFINITIONS,  # type: ignore[arg-type]
            BillingMode="PAY_PER_REQUEST",
        )
    except ClientError as exc:
        if exc.response["Error"]["Code"] == "ResourceInUseException":
            return False
        raise
    client.get_waiter("table_exists").wait(TableName=table_name)
    return True


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    settings = get_settings()
    created = create_table(
        settings.dynamodb_table,
        region=settings.aws_region,
        endpoint_url=settings.dynamodb_endpoint_url,
    )
    log.info("%s table %s", "created" if created else "already exists:", settings.dynamodb_table)
    return 0


if __name__ == "__main__":
    sys.exit(main())
