import json
import logging

from app.logging import JsonFormatter


def test_json_formatter_includes_extra_fields() -> None:
    record = logging.LogRecord("t", logging.INFO, __file__, 1, "hello %s", ("world",), None)
    record.request_id = "abc"

    payload = json.loads(JsonFormatter().format(record))

    assert payload["msg"] == "hello world"
    assert payload["level"] == "INFO"
    assert payload["request_id"] == "abc"
    assert "ts" in payload
