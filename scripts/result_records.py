"""Shared validation and loading for community leaderboard result records."""

from __future__ import annotations

import json
import math
from datetime import date
from pathlib import Path
from typing import Any

QUERY_NAMES = tuple(f"{number:02d}_{name}.sql" for number, name in [
    (1, "fleet_on_a_day"),
    (2, "model_mix"),
    (3, "failure_rate_by_model"),
    (4, "smart_warning_signals"),
    (5, "capacity_growth"),
])
REQUIRED_TOP_LEVEL_FIELDS = {
    "schema_version",
    "contributor_name",
    "github_handle",
    "code_repository_url",
    "run_date_utc",
    "language",
    "tool",
    "tool_version",
    "execution_class",
    "node_count",
    "vcpu_per_node",
    "ram_gib_per_node",
    "compute_and_network",
    "table_state",
    "cache_state",
    "command",
    "date_range",
    "sql_changes",
    "results",
}


def submitted_records(results_directory: Path) -> list[Path]:
    return sorted(
        path for path in results_directory.rglob("*.json") if path.name != "TEMPLATE.json"
    )


def load_and_validate(path: Path) -> dict[str, Any]:
    try:
        record = json.loads(path.read_text())
    except json.JSONDecodeError as error:
        raise ValueError(f"{path}: invalid JSON: {error.msg}") from error

    if not isinstance(record, dict):
        raise ValueError(f"{path}: record must be a JSON object")
    missing = REQUIRED_TOP_LEVEL_FIELDS - record.keys()
    if missing:
        raise ValueError(f"{path}: missing fields: {', '.join(sorted(missing))}")
    if record["schema_version"] != 1:
        raise ValueError(f"{path}: schema_version must be 1")
    for field in (
        "contributor_name",
        "github_handle",
        "run_date_utc",
        "language",
        "tool",
        "tool_version",
        "compute_and_network",
        "table_state",
        "command",
        "date_range",
        "sql_changes",
    ):
        if not isinstance(record[field], str) or not record[field].strip():
            raise ValueError(f"{path}: {field} must be a non-empty string")
    try:
        date.fromisoformat(record["run_date_utc"])
    except ValueError as error:
        raise ValueError(f"{path}: run_date_utc must be an ISO-8601 date") from error
    repository_url = record["code_repository_url"]
    if not isinstance(repository_url, str) or not repository_url.startswith("https://github.com/"):
        raise ValueError(f"{path}: code_repository_url must be a public GitHub HTTPS URL")
    if record["cache_state"] not in {"cold", "warm", "disabled", "unknown"}:
        raise ValueError(f"{path}: cache_state must be cold, warm, disabled, or unknown")
    execution_class = record["execution_class"]
    if execution_class not in {"single_node", "distributed"}:
        raise ValueError(f"{path}: execution_class must be single_node or distributed")
    for field in ("node_count", "vcpu_per_node", "ram_gib_per_node"):
        value = record[field]
        if isinstance(value, bool) or not isinstance(value, int) or value < 1:
            raise ValueError(f"{path}: {field} must be a positive integer")
    if execution_class == "single_node" and record["node_count"] != 1:
        raise ValueError(f"{path}: single_node records must have node_count of 1")
    if execution_class == "distributed" and not 2 <= record["node_count"] <= 4:
        raise ValueError(f"{path}: distributed records must use 2 to 4 nodes")
    if record["vcpu_per_node"] > 8 or record["ram_gib_per_node"] > 32:
        raise ValueError(f"{path}: each node is limited to 8 vCPU and 32 GiB RAM")

    markdown_report = path.with_suffix(".md")
    if not markdown_report.is_file():
        raise ValueError(f"{path}: matching Markdown report is required: {markdown_report}")

    results = record["results"]
    if not isinstance(results, list) or len(results) != len(QUERY_NAMES):
        raise ValueError(f"{path}: results must contain exactly the five challenge queries")
    query_names = [result.get("query") for result in results if isinstance(result, dict)]
    if set(query_names) != set(QUERY_NAMES) or len(set(query_names)) != len(QUERY_NAMES):
        raise ValueError(f"{path}: results must contain each challenge query exactly once")

    for result in results:
        if not isinstance(result, dict):
            raise ValueError(f"{path}: each result must be a JSON object")
        if result.get("status") not in {"pass", "fail", "not_run"}:
            raise ValueError(f"{path}: result status must be pass, fail, or not_run")
        for metric in ("runtime_ms", "bytes_scanned", "files_scanned"):
            value = result.get(metric)
            if value is not None and (
                isinstance(value, bool)
                or not isinstance(value, (int, float))
                or not math.isfinite(value)
                or value < 0
            ):
                raise ValueError(f"{path}: {metric} must be a non-negative number or null")
            if metric != "runtime_ms" and value is not None and not isinstance(value, int):
                raise ValueError(f"{path}: {metric} must be an integer or null")
        if result["status"] == "pass" and result.get("runtime_ms") is None:
            raise ValueError(f"{path}: passing results require runtime_ms")
        if result["status"] == "pass" and not isinstance(
            result.get("result_evidence"), str
        ):
            raise ValueError(f"{path}: passing results require string result_evidence")
        if result["status"] == "pass" and not result["result_evidence"].strip():
            raise ValueError(f"{path}: passing results require non-empty result_evidence")
    return record
