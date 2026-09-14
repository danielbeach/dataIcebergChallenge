"""Generate the checked-in community-reported results leaderboard."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from result_records import QUERY_NAMES, load_and_validate, submitted_records

RESULTS_DIRECTORY = Path("results")
LEADERBOARD_PATH = Path("LEADERBOARD.md")


def report_link(path: Path, record: dict[str, Any]) -> str:
    label = (
        f"{record['tool']} {record['tool_version']} "
        f"({record['contributor_name']}, @{record['github_handle']})"
    )
    return f"[{label}]({path.with_suffix('.md').as_posix()})"


def code_link(record: dict[str, Any]) -> str:
    return f"[repository]({record['code_repository_url']})"


def format_duration(milliseconds: float) -> str:
    if milliseconds < 1_000:
        return f"{milliseconds:g} ms"
    return f"{milliseconds / 1_000:g} s"


def leaders_for_query(
    records: list[tuple[Path, dict[str, Any]]],
    query: str,
    cache_state: str,
    execution_class: str,
) -> tuple[Path, dict[str, Any], dict[str, Any]] | None:
    candidates = [
        (path, record, result)
        for path, record in records
        if record["cache_state"] == cache_state
        and record["execution_class"] == execution_class
        for result in record["results"]
        if result["query"] == query and result["status"] == "pass"
    ]
    return min(candidates, key=lambda candidate: candidate[2]["runtime_ms"]) if candidates else None


def bytes_leader(
    records: list[tuple[Path, dict[str, Any]]], query: str, execution_class: str
) -> tuple[Path, dict[str, Any], dict[str, Any]] | None:
    candidates = [
        (path, record, result)
        for path, record in records
        for result in record["results"]
        if record["execution_class"] == execution_class
        and result["query"] == query
        and result["status"] == "pass"
        and result["bytes_scanned"] is not None
    ]
    return min(candidates, key=lambda candidate: candidate[2]["bytes_scanned"]) if candidates else None


def main() -> None:
    records = [
        (path, load_and_validate(path)) for path in submitted_records(RESULTS_DIRECTORY)
    ]
    lines = [
        "# Community Runtime Leaderboard",
        "",
        "> Results are contributor-reported, not controlled benchmarks. Report links identify "
        "the contributor and link their public GitHub code repository, with hardware, network, "
        "cache state, table state, and query translation details.",
        "",
    ]
    for execution_class, title in (
        ("single_node", "Single-node engines (max: 8 vCPU / 32 GiB RAM)"),
        ("distributed", "Distributed engines (max: 4 nodes; 8 vCPU / 32 GiB RAM each)"),
    ):
        lines.extend(["", f"## {title}"])
        for cache_state, heading in (("cold", "Fastest cold runs"), ("warm", "Fastest warm runs")):
            lines.extend(["", f"### {heading}", "", "| Query | Runtime | Tool / report | Code |", "|---|---:|---|---|"])
            for query in QUERY_NAMES:
                leader = leaders_for_query(records, query, cache_state, execution_class)
                lines.append(
                    f"| `{query}` | {format_duration(leader[2]['runtime_ms'])} | "
                    f"{report_link(leader[0], leader[1])} | {code_link(leader[1])} |"
                    if leader
                    else f"| `{query}` | — | No submitted {cache_state} run | — |"
                )
        lines.extend(["", "### Lowest reported bytes read", "", "| Query | Bytes read | Tool / report | Code |", "|---|---:|---|---|"])
        for query in QUERY_NAMES:
            leader = bytes_leader(records, query, execution_class)
            lines.append(
                f"| `{query}` | {leader[2]['bytes_scanned']:,} | "
                f"{report_link(leader[0], leader[1])} | {code_link(leader[1])} |"
                if leader
                else f"| `{query}` | — | No submitted scan metric | — |"
            )
        complete = [
            (path, record)
            for path, record in records
            if record["execution_class"] == execution_class
            and all(result["status"] == "pass" for result in record["results"])
        ]
        lines.extend(["", "### Completed all five queries", ""])
        if complete:
            lines.extend(
                f"- {report_link(path, record)} — {code_link(record)}, "
                f"{record['cache_state']} cache, community-reported"
                for path, record in complete
            )
        else:
            lines.append("No submission has completed all five queries yet.")
    lines.append("")
    LEADERBOARD_PATH.write_text("\n".join(lines))


if __name__ == "__main__":
    main()
