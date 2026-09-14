"""Benchmark the five challenge queries with DuckDB against the Drive Stats Iceberg table.

Runs one query per invocation so that a ``cold`` run really is cold: a fresh
process holds no DuckDB HTTP metadata cache, no Iceberg manifest cache, and no
Parquet footer cache.

Usage::

    uv run python scripts/bench_duckdb.py 01_fleet_on_a_day.sql --mode cold
    uv run python scripts/bench_duckdb.py 01_fleet_on_a_day.sql --mode warm --repeats 3

The ``runtime_ms`` printed is query execution only. The one-time Iceberg
metadata resolution (creating the view) is reported separately as
``setup_ms`` so both costs stay visible.

Resource ceiling: the challenge single-node class allows 8 vCPU and 32 GiB RAM,
so DuckDB is pinned to 8 threads and a 24 GiB memory limit regardless of the
host's core count.
"""

from __future__ import annotations

import argparse
import json
import os
import time
from pathlib import Path

import duckdb
from dotenv import load_dotenv

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
QUERY_DIRECTORY = REPOSITORY_ROOT / "queries"
TABLE_LOCATION = "s3://drivestats-iceberg/drivestats"
DEFAULT_ENDPOINT = "https://s3.us-west-004.backblazeb2.com"
DEFAULT_REGION = "us-west-004"
THREADS = 8
MEMORY_LIMIT = "24GB"


def connect() -> duckdb.DuckDBPyConnection:
    load_dotenv(REPOSITORY_ROOT / ".env")
    connection = duckdb.connect()
    connection.execute("INSTALL httpfs; LOAD httpfs; INSTALL iceberg; LOAD iceberg;")
    connection.execute(
        "CREATE SECRET drivestats_b2 (TYPE s3, KEY_ID ?, SECRET ?, REGION ?, ENDPOINT ?)",
        [
            os.environ["DRIVESTATS_S3_ACCESS_KEY_ID"],
            os.environ["DRIVESTATS_S3_SECRET_ACCESS_KEY"],
            os.getenv("DRIVESTATS_S3_REGION", DEFAULT_REGION),
            os.getenv("DRIVESTATS_S3_ENDPOINT", DEFAULT_ENDPOINT).removeprefix("https://"),
        ],
    )
    connection.execute("SET unsafe_enable_version_guessing = true")
    connection.execute(f"SET threads = {THREADS}")
    connection.execute(f"SET memory_limit = '{MEMORY_LIMIT}'")
    return connection


def create_view(connection: duckdb.DuckDBPyConnection) -> float:
    started = time.perf_counter()
    connection.execute(
        f"CREATE OR REPLACE VIEW drivestats AS SELECT * FROM iceberg_scan("
        f"'{TABLE_LOCATION}', version = '?', allow_moved_paths = true)"
    )
    return (time.perf_counter() - started) * 1000


def snapshot_id(connection: duckdb.DuckDBPyConnection) -> int:
    row = connection.execute(
        f"SELECT snapshot_id FROM iceberg_snapshots('{TABLE_LOCATION}', version = '?') "
        "ORDER BY sequence_number DESC LIMIT 1"
    ).fetchone()
    return row[0]


def scan_metrics(connection: duckdb.DuckDBPyConnection) -> dict[str, int]:
    """Bytes and files DuckDB fetched from object storage, from its external file cache.

    Every remote byte range DuckDB reads is registered here; ranges evicted under
    memory pressure stay listed with ``loaded = false``, so summing all rows gives
    the bytes read rather than only the bytes still resident.
    """
    parquet, files = connection.execute(
        "SELECT COALESCE(SUM(nr_bytes), 0), COUNT(DISTINCT path) "
        "FROM duckdb_external_file_cache() WHERE path LIKE '%.parquet'"
    ).fetchone()
    metadata_bytes, metadata_files = connection.execute(
        "SELECT COALESCE(SUM(nr_bytes), 0), COUNT(DISTINCT path) "
        "FROM duckdb_external_file_cache() WHERE path NOT LIKE '%.parquet'"
    ).fetchone()
    evicted = connection.execute(
        "SELECT COALESCE(SUM(nr_bytes), 0) FROM duckdb_external_file_cache() WHERE NOT loaded"
    ).fetchone()[0]
    return {
        "parquet_bytes_read": int(parquet),
        "parquet_files_read": int(files),
        "metadata_bytes_read": int(metadata_bytes),
        "metadata_files_read": int(metadata_files),
        "evicted_bytes": int(evicted),
    }


def run_once(connection: duckdb.DuckDBPyConnection, sql: str) -> tuple[float, list, list[str]]:
    started = time.perf_counter()
    relation = connection.execute(sql)
    rows = relation.fetchall()
    elapsed_ms = (time.perf_counter() - started) * 1000
    columns = [description[0] for description in relation.description]
    return elapsed_ms, rows, columns


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("query", help="Challenge query filename, e.g. 01_fleet_on_a_day.sql")
    parser.add_argument("--mode", choices=("cold", "warm"), default="cold")
    parser.add_argument(
        "--repeats",
        type=int,
        default=3,
        help="Warm mode only: executions after the priming run; the fastest is reported.",
    )
    parser.add_argument("--json-out", type=Path, default=None)
    arguments = parser.parse_args()

    sql = (QUERY_DIRECTORY / arguments.query).read_text()
    connection = connect()
    setup_ms = create_view(connection)

    if arguments.mode == "cold":
        runtime_ms, rows, columns = run_once(connection, sql)
        samples = [runtime_ms]
    else:
        run_once(connection, sql)  # prime the caches, discard
        samples = []
        for _ in range(arguments.repeats):
            elapsed_ms, rows, columns = run_once(connection, sql)
            samples.append(elapsed_ms)
        runtime_ms = min(samples)

    metrics = scan_metrics(connection)
    record = {
        "query": arguments.query,
        "mode": arguments.mode,
        "threads": THREADS,
        "memory_limit": MEMORY_LIMIT,
        "duckdb_version": duckdb.__version__,
        "snapshot_id": snapshot_id(connection),
        "setup_ms": round(setup_ms, 1),
        "runtime_ms": round(runtime_ms, 1),
        "samples_ms": [round(sample, 1) for sample in samples],
        **metrics,
        "row_count": len(rows),
        "columns": columns,
        "rows": [[str(value) for value in row] for row in rows],
    }
    connection.close()

    if arguments.json_out:
        arguments.json_out.write_text(json.dumps(record, indent=2))
    print(json.dumps({key: value for key, value in record.items() if key != "rows"}, indent=2))
    print("--- result ---")
    print(" | ".join(columns))
    for row in rows:
        print(" | ".join(str(value) for value in row))


if __name__ == "__main__":
    main()
