"""Shared validation and loading for community leaderboard result records."""

from __future__ import annotations

import json
import math
import re
from datetime import date
from functools import lru_cache
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
TEMPLATE_JSON_NAME = "TEMPLATE.json"
TEMPLATE_MARKDOWN_NAME = "TEMPLATE.md"
PLACEHOLDER_PATTERN = re.compile(r"^<.*>$", re.DOTALL)
GITHUB_HANDLE_PATTERN = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9]|-(?=[A-Za-z0-9])){0,38}$")
REPOSITORY_URL_PATTERN = re.compile(r"^https://github\.com/[A-Za-z0-9._-]+/[A-Za-z0-9._-]+/?$")
MINIMUM_REPORT_CHARACTERS = 400


@lru_cache(maxsize=None)
def _template_directory(start: Path) -> Path | None:
    """Find the directory holding TEMPLATE.json, walking up from a record's directory."""
    for candidate in (start, *start.parents):
        if (candidate / TEMPLATE_JSON_NAME).is_file():
            return candidate
    return None


@lru_cache(maxsize=None)
def _placeholder_values(template_directory: Path) -> frozenset[str]:
    """Collect every `<...>` string in TEMPLATE.json, at any depth."""

    def walk(node: Any) -> list[str]:
        if isinstance(node, str):
            return [node] if PLACEHOLDER_PATTERN.match(node) else []
        if isinstance(node, dict):
            return [value for child in node.values() for value in walk(child)]
        if isinstance(node, list):
            return [value for child in node for value in walk(child)]
        return []

    template = json.loads((template_directory / TEMPLATE_JSON_NAME).read_text())
    return frozenset(walk(template))


def _unfilled_placeholders(record: dict[str, Any], placeholders: frozenset[str]) -> list[str]:
    """Report every field left at its TEMPLATE.json placeholder value."""
    unfilled = [
        field
        for field, value in record.items()
        if isinstance(value, str) and value in placeholders
    ]
    for index, result in enumerate(record.get("results", [])):
        if isinstance(result, dict):
            unfilled.extend(
                f"results[{index}].{field}"
                for field, value in result.items()
                if isinstance(value, str) and value in placeholders
            )
    return sorted(unfilled)


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

    if not GITHUB_HANDLE_PATTERN.match(record["github_handle"]):
        raise ValueError(f"{path}: github_handle must be a bare GitHub handle, without a leading @")
    if not REPOSITORY_URL_PATTERN.match(repository_url):
        raise ValueError(
            f"{path}: code_repository_url must look like https://github.com/<owner>/<repository>"
        )

    template_directory = _template_directory(path.parent)
    if template_directory is not None:
        if path.parent == template_directory:
            raise ValueError(
                f"{path}: records live in results/<github-handle>/, not the results root"
            )
        if path.parent.name.lower() != record["github_handle"].lower():
            raise ValueError(
                f"{path}: directory name must match github_handle "
                f"({path.parent.name!r} vs {record['github_handle']!r})"
            )
        unfilled = _unfilled_placeholders(record, _placeholder_values(template_directory))
        if unfilled:
            raise ValueError(
                f"{path}: these fields still hold TEMPLATE.json placeholders: "
                f"{', '.join(unfilled)}"
            )

    markdown_report = path.with_suffix(".md")
    if not markdown_report.is_file():
        raise ValueError(f"{path}: matching Markdown report is required: {markdown_report}")
    report_text = markdown_report.read_text()
    if template_directory is not None:
        template_markdown = template_directory / TEMPLATE_MARKDOWN_NAME
        if template_markdown.is_file() and report_text.strip() == template_markdown.read_text().strip():
            raise ValueError(f"{markdown_report}: report is an unedited copy of TEMPLATE.md")
    if len(report_text.strip()) < MINIMUM_REPORT_CHARACTERS:
        raise ValueError(
            f"{markdown_report}: report must describe the run in at least "
            f"{MINIMUM_REPORT_CHARACTERS} characters"
        )

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
