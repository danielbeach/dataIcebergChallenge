"""Generate the checked-in community-reported results leaderboard.

Writes the standalone `LEADERBOARD.md` and mirrors the same tables into the
`<!-- leaderboard:start -->` / `<!-- leaderboard:end -->` block in `README.md`,
so the two can never drift. Each query lists its top `TOP_N` submissions.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from result_records import QUERY_NAMES, load_and_validate, submitted_records

RESULTS_DIRECTORY = Path("results")
LEADERBOARD_PATH = Path("LEADERBOARD.md")
README_PATH = Path("README.md")
README_START_MARKER = "<!-- leaderboard:start -->"
README_END_MARKER = "<!-- leaderboard:end -->"

TOP_N = 5

RUNTIME_HEADER = (
    "| Query | Rank | Runtime | Contributor | Specs | Tool / report | Code |",
    "|---|---:|---:|---|---|---|---|",
)
BYTES_HEADER = (
    "| Query | Rank | Bytes read | Contributor | Specs | Tool / report | Code |",
    "|---|---:|---:|---|---|---|---|",
)
EMPTY_CELLS = "— | — |"


def markdown_text(value: str) -> str:
    """Escape a contributor-supplied string so it cannot break out of a table cell."""
    return value.replace("\\", "\\\\").replace("|", "\\|").replace("\n", " ")


def contributor(record: dict[str, Any]) -> str:
    return (
        f"{markdown_text(record['contributor_name'])} "
        f"(@{markdown_text(record['github_handle'])})"
    )


def specs(record: dict[str, Any]) -> str:
    """Render the reported hardware, e.g. `1 x 8 vCPU / 32 GiB, Ryzen 7950X, us-west`."""
    shape = (
        f"{record['node_count']} x {record['vcpu_per_node']} vCPU / "
        f"{record['ram_gib_per_node']} GiB"
    )
    return f"{shape}, {markdown_text(record['compute_and_network'])}"


def report_link(path: Path, record: dict[str, Any]) -> str:
    label = f"{markdown_text(record['tool'])} {markdown_text(record['tool_version'])}"
    return f"[{label}]({path.with_suffix('.md').as_posix()})"


def code_link(record: dict[str, Any]) -> str:
    return f"[repository]({record['code_repository_url']})"


def format_duration(milliseconds: float) -> str:
    if milliseconds < 1_000:
        return f"{milliseconds:g} ms"
    return f"{milliseconds / 1_000:g} s"


def leader_row(
    query: str, rank: int, metric: str, leader: tuple[Path, dict[str, Any], Any]
) -> str:
    """Render one ranked row; the query cell is filled only on the first row of its group."""
    path, record, _ = leader
    query_cell = f"`{query}`" if rank == 1 else ""
    return (
        f"| {query_cell} | {rank} | {metric} | {contributor(record)} | {specs(record)} | "
        f"{report_link(path, record)} | {code_link(record)} |"
    )


def empty_row(query: str, reason: str) -> str:
    return f"| `{query}` | — | — | {EMPTY_CELLS} {reason} | — |"


def leaders_for_query(
    records: list[tuple[Path, dict[str, Any]]],
    query: str,
    cache_state: str,
    execution_class: str,
    limit: int = TOP_N,
) -> list[tuple[Path, dict[str, Any], dict[str, Any]]]:
    """Return the fastest `limit` passing runs for one query, cache state, and class."""
    candidates = [
        (path, record, result)
        for path, record in records
        if record["cache_state"] == cache_state
        and record["execution_class"] == execution_class
        for result in record["results"]
        if result["query"] == query and result["status"] == "pass"
    ]
    candidates.sort(key=lambda candidate: (candidate[2]["runtime_ms"], candidate[0].as_posix()))
    return candidates[:limit]


def bytes_leaders(
    records: list[tuple[Path, dict[str, Any]]],
    query: str,
    execution_class: str,
    limit: int = TOP_N,
) -> list[tuple[Path, dict[str, Any], dict[str, Any]]]:
    """Return the `limit` smallest reported scans for one query and execution class."""
    candidates = [
        (path, record, result)
        for path, record in records
        for result in record["results"]
        if record["execution_class"] == execution_class
        and result["query"] == query
        and result["status"] == "pass"
        and result["bytes_scanned"] is not None
    ]
    candidates.sort(key=lambda candidate: (candidate[2]["bytes_scanned"], candidate[0].as_posix()))
    return candidates[:limit]


def build_leaderboard() -> list[str]:
    records = [
        (path, load_and_validate(path)) for path in submitted_records(RESULTS_DIRECTORY)
    ]
    lines = [
        "# Community Runtime Leaderboard",
        "",
        f"> Results are contributor-reported, not controlled benchmarks. Each query lists its "
        f"top {TOP_N} submissions. Each row names the contributor, the hardware they reported, "
        "and the public repository holding their code; the linked report adds network, cache "
        "state, table state, and query translation details.",
    ]
    for execution_class, title in (
        ("single_node", "Single-node engines (max: 8 vCPU / 32 GiB RAM)"),
        ("distributed", "Distributed engines (max: 4 nodes; 8 vCPU / 32 GiB RAM each)"),
    ):
        lines.extend(["", f"## {title}"])
        for cache_state, heading in (("cold", "Fastest cold runs"), ("warm", "Fastest warm runs")):
            lines.extend(["", f"### {heading}", "", *RUNTIME_HEADER])
            for query in QUERY_NAMES:
                leaders = leaders_for_query(records, query, cache_state, execution_class)
                if leaders:
                    lines.extend(
                        leader_row(query, rank, format_duration(leader[2]["runtime_ms"]), leader)
                        for rank, leader in enumerate(leaders, start=1)
                    )
                else:
                    lines.append(empty_row(query, f"No submitted {cache_state} run"))
        lines.extend(["", "### Lowest reported bytes read", "", *BYTES_HEADER])
        for query in QUERY_NAMES:
            leaders = bytes_leaders(records, query, execution_class)
            if leaders:
                lines.extend(
                    leader_row(query, rank, f"{leader[2]['bytes_scanned']:,}", leader)
                    for rank, leader in enumerate(leaders, start=1)
                )
            else:
                lines.append(empty_row(query, "No submitted scan metric"))
        complete = [
            (path, record)
            for path, record in records
            if record["execution_class"] == execution_class
            and all(result["status"] == "pass" for result in record["results"])
        ]
        lines.extend(["", "### Completed all five queries", ""])
        if complete:
            lines.extend(
                f"- {contributor(record)} — {specs(record)} — {report_link(path, record)} — "
                f"{code_link(record)}, {record['cache_state']} cache, community-reported"
                for path, record in complete
            )
        else:
            lines.append("No submission has completed all five queries yet.")
    lines.append("")
    return lines


def update_readme(leaderboard_lines: list[str]) -> None:
    """Mirror the leaderboard into README.md, demoting headings one level."""
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
    LEADERBOARD_PATH.write_text("\n".join(leaderboard_lines))
    update_readme(leaderboard_lines)
    print(f"Wrote {LEADERBOARD_PATH} and refreshed the {README_PATH} leaderboard block.")


if __name__ == "__main__":
    main()
