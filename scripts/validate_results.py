"""Validate every submitted community leaderboard record."""

from __future__ import annotations

import argparse
from pathlib import Path

from result_records import load_and_validate, submitted_records


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results-dir", type=Path, default=Path("results"))
    args = parser.parse_args()
    records = submitted_records(args.results_dir)
    for path in records:
        load_and_validate(path)
        print(f"valid: {path}")
    print(f"Validated {len(records)} submitted result record(s).")


if __name__ == "__main__":
    main()
