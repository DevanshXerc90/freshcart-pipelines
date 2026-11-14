"""Check local FreshCart extraction and SQL safeguards without Snowflake."""

import gzip
import json

from elt.freshcart_pipeline import (
    QUALITY_CHECKS,
    SQL_10_ORDERS_CLEAN,
    setup_sql,
    write_landing,
)


def test_write_landing_writes_gzip_jsonl(tmp_path):
    record = {"order_id": "ORD-TEST", "amount": 12}
    path = write_landing("web", [record], "run-test", tmp_path)

    with gzip.open(path, "rt", encoding="utf-8") as landing_file:
        envelope = json.loads(landing_file.readline())

    assert envelope["source"] == "web"
    assert envelope["run_id"] == "run-test"
    assert envelope["data"] == record
    assert envelope["extracted_at"].endswith("+00:00")


def test_currency_rule_is_in_cleaning_validation():
    assert "unsupported_currency" in SQL_10_ORDERS_CLEAN
    assert "currency NOT IN ('INR', 'USD')" in SQL_10_ORDERS_CLEAN


def test_sixth_quality_check_is_future_date_rule():
    assert len(QUALITY_CHECKS) == 6
    assert QUALITY_CHECKS["future-dated silver orders"] == (
        "SELECT COUNT(*) FROM silver.orders_dedup WHERE order_date > CURRENT_DATE()"
    )


def test_setup_rejects_non_identifier_database_names():
    try:
        setup_sql("FRESHCART; DROP DATABASE PROD")
    except ValueError:
        return
    raise AssertionError("Unsafe database identifiers must be rejected")
