"""Check the files a pull request touches before a maintainer reads it.

Catches the mistakes that are tedious to spot by eye: committed credentials,
committed data extracts, oversized files, a submission that edits somebody
else's results directory, and a submission that hand-carries the generated
leaderboard files.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

RESULTS_DIRECTORY = "results/"
GENERATED_PATHS = ("LEADERBOARD.md", "README.md")
MAXIMUM_FILE_BYTES = 1_000_000
FORBIDDEN_SUFFIXES = {
    ".7z",
    ".avro",
    ".csv",
    ".db",
    ".duckdb",
    ".gz",
    ".key",
    ".orc",
    ".p12",
    ".parquet",
    ".pem",
    ".tar",
    ".tsv",
    ".zip",
}
FORBIDDEN_NAMES = {".env", "credentials", "secrets.json"}
ALLOWED_RESULT_SUFFIXES = {".json", ".md", ".py", ".rs", ".go", ".java", ".scala", ".sql", ".toml",
                           ".txt", ".ts", ".js", ".sh", ".yaml", ".yml", ".lock", ".ipynb"}
CREDENTIAL_PATTERNS = (
    ("AWS access key id", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("Backblaze application key", re.compile(r"\b00[0-9a-f]{5}[0-9a-zA-Z]{25,}\b")),
    ("assigned secret", re.compile(
        r"(?i)\b(aws_secret_access_key|application_?key|secret_?access_?key|s3_secret"
        r"|password|api_?token)\b\s*[:=]\s*[\"']?[A-Za-z0-9/+=_-]{12,}"
    )),
    ("private key block", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
)
PLACEHOLDER_SECRET = re.compile(r"(?i)<[^>]*>|your[-_ ]|example|redacted|xxx+|\.\.\.|\$\{|changeme")


def git(*arguments: str) -> str:
    """Run a git command, failing with the message rather than a traceback."""
    result = subprocess.run(
        ["git", *arguments], capture_output=True, text=True, errors="replace"
    )
    if result.returncode != 0:
        raise SystemExit(
            f"error: git {' '.join(arguments)} failed: {result.stderr.strip()}\n"
            "Check that both refs exist; CI needs a full checkout (fetch-depth: 0)."
        )
    return result.stdout


def changed_files(base: str, head: str) -> list[str]:
    diff = git("diff", "--name-only", "--diff-filter=d", f"{base}...{head}")
    return [line for line in diff.splitlines() if line]


def added_lines(base: str, head: str, path: str) -> list[tuple[int, str]]:
    """Return the (line number, text) pairs this pull request adds to one file."""
    diff = git("diff", "--unified=0", f"{base}...{head}", "--", path)
    lines: list[tuple[int, str]] = []
    line_number = 0
    for line in diff.splitlines():
        hunk = re.match(r"^@@ -\d+(?:,\d+)? \+(\d+)", line)
        if hunk:
            line_number = int(hunk.group(1))
        elif line.startswith("+") and not line.startswith("+++"):
            lines.append((line_number, line[1:]))
            line_number += 1
    return lines


def check_file_shape(path: str, problems: list[str]) -> None:
    candidate = Path(path)
    if candidate.name in FORBIDDEN_NAMES or candidate.suffix.lower() in FORBIDDEN_SUFFIXES:
        problems.append(f"{path}: this file type must never be committed")
        return
    if not candidate.is_file():
        return
    size = candidate.stat().st_size
    if size > MAXIMUM_FILE_BYTES:
        problems.append(
            f"{path}: {size:,} bytes exceeds the {MAXIMUM_FILE_BYTES:,} byte limit; "
            "reports carry summary evidence, not result data"
        )
    if path.startswith(RESULTS_DIRECTORY) and candidate.suffix.lower() not in ALLOWED_RESULT_SUFFIXES:
        problems.append(f"{path}: unexpected file type under {RESULTS_DIRECTORY}")


def check_credentials(base: str, head: str, path: str, problems: list[str]) -> None:
    for line_number, text in added_lines(base, head, path):
        if PLACEHOLDER_SECRET.search(text):
            continue
        for label, pattern in CREDENTIAL_PATTERNS:
            if pattern.search(text):
                problems.append(f"{path}:{line_number}: looks like a committed {label}")
                break


def submission_paths(paths: list[str]) -> list[str]:
    """The result-record files this pull request touches."""
    return [
        path
        for path in paths
        if path.startswith(RESULTS_DIRECTORY) and len(Path(path).parts) > 2
    ]


def check_generated_files(paths: list[str], problems: list[str]) -> None:
    """A submission must not carry the generated leaderboard; the bot regenerates it on merge."""
    if not submission_paths(paths):
        return
    carried = [path for path in GENERATED_PATHS if path in paths]
    if carried:
        problems.append(
            f"{', '.join(carried)} is generated from the result records and is rewritten "
            "automatically after merge. Revert it from this pull request "
            "(git checkout origin/main -- " + " ".join(carried) + "); "
            "send unrelated documentation edits as a separate pull request"
        )


def check_single_contributor(paths: list[str], problems: list[str]) -> None:
    directories = {
        Path(path).parts[1]
        for path in paths
        if path.startswith(RESULTS_DIRECTORY) and len(Path(path).parts) > 2
    }
    if len(directories) > 1:
        problems.append(
            "this pull request edits more than one contributor directory "
            f"({', '.join(sorted(directories))}); submit one report per pull request"
        )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", default="origin/main", help="merge base ref")
    parser.add_argument("--head", default="HEAD", help="ref holding the proposed changes")
    args = parser.parse_args()

    paths = changed_files(args.base, args.head)
    problems: list[str] = []
    for path in paths:
        check_file_shape(path, problems)
        check_credentials(args.base, args.head, path, problems)
    check_single_contributor(paths, problems)
    check_generated_files(paths, problems)

    print(f"Checked {len(paths)} changed file(s) between {args.base} and {args.head}.")
    for problem in problems:
        print(f"error: {problem}", file=sys.stderr)
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
