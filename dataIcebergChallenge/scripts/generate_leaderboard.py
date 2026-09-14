"""Generate the checked-in community-reported results leaderboard."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from result_records import QUERY_NAMES, load_and_validate, submitted_records

RESULTS_DIRECTORY = Path("results")
README_PATH = Path("README.md")
README_START_MARKER = "<!-- leaderboard:start -->"
README_END_MARKER = "<!-- leaderboard:end -->"


def markdown_text(value: str) -> str:
    return value.replace("\\", "\\\\").replace("|", "\\|").replace("\n", " ")


def contributor(record: dict[str, Any]) -> str:
    return (
        f"{markdown_text(record['contributor_name'])} "
        f"(@{markdown_text(record['github_handle'])})"
    )


def report_link(path: Path, record: dict[str, Any]) -> str:
    label = f"{markdown_text(record['tool'])} {markdown_text(record['tool_version'])}"
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


def build_leaderboard() -> list[str]:
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
            lines.extend([
                "",
                f"### {heading}",
                "",
                "| Query | Runtime | Contributor | Tool / report | Code |",
                "|---|---:|---|---|---|",
            ])
            for query in QUERY_NAMES:
                leader = leaders_for_query(records, query, cache_state, execution_class)
                lines.append(
                    f"| `{query}` | {format_duration(leader[2]['runtime_ms'])} | {contributor(leader[1])} | "
                    f"{report_link(leader[0], leader[1])} | {code_link(leader[1])} |"
                    if leader
                    else f"| `{query}` | — | — | No submitted {cache_state} run | — |"
                )
        lines.extend([
            "",
            "### Lowest reported bytes read",
            "",
            "| Query | Bytes read | Contributor | Tool / report | Code |",
            "|---|---:|---|---|---|",
        ])
        for query in QUERY_NAMES:
            leader = bytes_leader(records, query, execution_class)
            lines.append(
                f"| `{query}` | {leader[2]['bytes_scanned']:,} | {contributor(leader[1])} | "
                f"{report_link(leader[0], leader[1])} | {code_link(leader[1])} |"
                if leader
                else f"| `{query}` | — | — | No submitted scan metric | — |"
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
                f"- {contributor(record)} — {report_link(path, record)} — {code_link(record)}, "
                f"{record['cache_state']} cache, community-reported"
                for path, record in complete
            )
        else:
            lines.append("No submission has completed all five queries yet.")
    lines.append("")
    return lines


def update_readme(leaderboard_lines: list[str]) -> None:
    readme = README_PATH.read_text()
    start = readme.find(README_START_MARKER)
    end = readme.find(README_END_MARKER)
    if start == -1 or end == -1 or end < start:
        raise ValueError("README.md must contain ordered leaderboard markers")
    embedded_lines = []
    for line in leaderboard_lines[1:]:
        if line.startswith("### "):
            embedded_lines.append(f"#### {line[4:]}")
        elif line.startswith("## "):
            embedded_lines.append(f"### {line[3:]}")
        else:
            embedded_lines.append(line)
    embedded = "\n".join(embedded_lines).strip()
    replacement = f"{README_START_MARKER}\n{embedded}\n{README_END_MARKER}"
    README_PATH.write_text(readme[:start] + replacement + readme[end + len(README_END_MARKER):])


def main() -> None:
    leaderboard_lines = build_leaderboard()
    update_readme(leaderboard_lines)


if __name__ == "__main__":
    main()
