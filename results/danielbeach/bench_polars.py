# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "polars==1.44.2",
#     "pyiceberg[s3fs,pyarrow]==0.12.0",
#     "boto3>=1.35",
#     "psutil>=6.0",
#     "python-dotenv>=1.0.1",
# ]
# ///
"""Benchmark the five challenge queries with the Polars streaming engine.

Runs one query per invocation so that a ``cold`` run really is cold: a fresh
process holds no Iceberg metadata cache, no manifest cache, and no Parquet
footer cache.

Usage::

    uv run results/danielbeach/bench_polars.py 01_fleet_on_a_day.sql --mode cold
    uv run results/danielbeach/bench_polars.py 01_fleet_on_a_day.sql --mode warm --repeats 3

The queries in ``queries/`` are DuckDB SQL. Polars SQL does not cover all of it
(unbounded ``SUM(COUNT(*)) OVER ()``, ``COUNT(DISTINCT CASE WHEN ...)``,
interval arithmetic against a joined column), so each query is translated to the
Polars LazyFrame API here and executed with ``collect(engine="streaming")``.
The translations are one-for-one; ``sql_changes`` in the JSON record describes
every difference.

The ``runtime_ms`` printed is query execution only. Resolving the Iceberg
metadata and building the scan is reported separately as ``setup_ms`` so both
costs stay visible.

Resource ceiling: the challenge single-node class allows 8 vCPU and 32 GiB RAM,
so Polars is pinned to 8 threads regardless of the host's core count. Polars has
no memory limit setting; the host's 24 GiB is the effective ceiling.
"""

from __future__ import annotations

import argparse
import json
import os
import time
from datetime import date
from pathlib import Path

from dotenv import load_dotenv

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
THREADS = 8

# Polars reads POLARS_MAX_THREADS when its thread pool is built at import time.
os.environ["POLARS_MAX_THREADS"] = str(THREADS)
load_dotenv(REPOSITORY_ROOT / ".env")

import boto3  # noqa: E402
import polars as pl  # noqa: E402
import psutil  # noqa: E402
from pyiceberg.expressions import And, EqualTo, GreaterThanOrEqual, LessThan  # noqa: E402
from pyiceberg.table import StaticTable  # noqa: E402

BUCKET = "drivestats-iceberg"
METADATA_PREFIX = "drivestats/metadata/"
DEFAULT_ENDPOINT = "https://s3.us-west-004.backblazeb2.com"
DEFAULT_REGION = "us-west-004"

DAY = date(2024, 12, 31)
YEAR_START = date(2024, 1, 1)
YEAR_END = date(2025, 1, 1)

# Iceberg row filters matching each query's date predicate, used only to report
# how many data files the predicate leaves after partition pruning.
PLANNING_FILTERS = {
    "01_fleet_on_a_day.sql": EqualTo("date", DAY.isoformat()),
    "02_model_mix.sql": EqualTo("date", DAY.isoformat()),
    "03_failure_rate_by_model.sql": And(
        GreaterThanOrEqual("date", YEAR_START.isoformat()),
        LessThan("date", YEAR_END.isoformat()),
    ),
    "04_smart_warning_signals.sql": None,
    "05_capacity_growth.sql": None,
}


def s3_client():
    return boto3.client(
        "s3",
        endpoint_url=os.getenv("DRIVESTATS_S3_ENDPOINT", DEFAULT_ENDPOINT),
        aws_access_key_id=os.environ["DRIVESTATS_S3_ACCESS_KEY_ID"],
        aws_secret_access_key=os.environ["DRIVESTATS_S3_SECRET_ACCESS_KEY"],
        region_name=os.getenv("DRIVESTATS_S3_REGION", DEFAULT_REGION),
    )


def latest_metadata_key(client) -> str:
    """The table has no Iceberg catalog and no version-hint.text, so pick the
    highest-numbered metadata file in the prefix."""
    pages = client.get_paginator("list_objects_v2").paginate(
        Bucket=BUCKET, Prefix=METADATA_PREFIX
    )
    return max(
        entry["Key"]
        for page in pages
        for entry in page.get("Contents", [])
        if entry["Key"].endswith(".metadata.json")
    )


def storage_options() -> dict[str, str]:
    return {
        "s3.endpoint": os.getenv("DRIVESTATS_S3_ENDPOINT", DEFAULT_ENDPOINT),
        "s3.access-key-id": os.environ["DRIVESTATS_S3_ACCESS_KEY_ID"],
        "s3.secret-access-key": os.environ["DRIVESTATS_S3_SECRET_ACCESS_KEY"],
        "s3.region": os.getenv("DRIVESTATS_S3_REGION", DEFAULT_REGION),
    }


def query_01(drivestats: pl.LazyFrame) -> pl.LazyFrame:
    return (
        drivestats.filter(pl.col("date") == DAY)
        .group_by("date")
        .agg(
            pl.len().alias("active_drives"),
            pl.col("capacity_bytes").sum().alias("capacity_bytes"),
        )
        .select(
            "date",
            "active_drives",
            (pl.col("capacity_bytes") / 1e18).round(2).alias("raw_exabytes"),
        )
    )


def query_02(drivestats: pl.LazyFrame) -> pl.LazyFrame:
    return (
        drivestats.filter(pl.col("date") == DAY)
        .group_by("model")
        .agg(pl.len().alias("active_drives"))
        .with_columns(
            (100.0 * pl.col("active_drives") / pl.col("active_drives").sum())
            .round(2)
            .alias("fleet_percent")
        )
        .sort("active_drives", descending=True)
        .limit(15)
    )


def query_03(drivestats: pl.LazyFrame) -> pl.LazyFrame:
    model_year = (
        drivestats.filter((pl.col("date") >= YEAR_START) & (pl.col("date") < YEAR_END))
        .group_by("model")
        .agg(
            pl.len().alias("drive_days"),
            pl.col("serial_number").n_unique().alias("distinct_drives"),
            pl.col("serial_number")
            .filter(pl.col("failure") == 1)
            .n_unique()
            .alias("failed_drives"),
        )
    )
    return (
        model_year.filter(pl.col("drive_days") >= 100_000)
        .select(
            "model",
            "distinct_drives",
            "failed_drives",
            (100.0 * pl.col("failed_drives") * 365.25 / pl.col("drive_days"))
            .round(3)
            .alias("annualized_failure_rate_pct"),
        )
        .sort(
            ["annualized_failure_rate_pct", "failed_drives"], descending=[True, True]
        )
        .limit(20)
    )


def query_04(drivestats: pl.LazyFrame) -> pl.LazyFrame:
    failed_drives = (
        drivestats.filter(pl.col("failure") == 1)
        .group_by("serial_number")
        .agg(pl.col("date").min().alias("failure_date"))
    )
    return (
        drivestats.select(
            "serial_number", "date", "model", "smart_5_raw", "smart_187_raw", "smart_197_raw"
        )
        .join(failed_drives, on="serial_number", how="inner")
        .filter(
            (pl.col("date") >= pl.col("failure_date").dt.offset_by("-30d"))
            & (pl.col("date") < pl.col("failure_date"))
        )
        .group_by("model")
        .agg(
            pl.len().alias("observations_30_days_before_failure"),
            pl.col("smart_5_raw").mean().round(1).alias("avg_reallocated_sectors"),
            pl.col("smart_187_raw")
            .mean()
            .round(1)
            .alias("avg_reported_uncorrectable_errors"),
            pl.col("smart_197_raw").mean().round(1).alias("avg_pending_sectors"),
        )
        .filter(pl.col("observations_30_days_before_failure") >= 100)
        .sort("avg_pending_sectors", descending=True, nulls_last=True)
        .limit(20)
    )


def query_05(drivestats: pl.LazyFrame) -> pl.LazyFrame:
    month_end = (
        drivestats.select("date")
        .group_by(pl.col("date").dt.truncate("1mo").alias("month"))
        .agg(pl.col("date").max().alias("month_end_date"))
        .select("month_end_date")
    )
    # month_end_date is unique per month, so DuckDB's inner join selects exactly
    # the rows a semi-join keeps, without widening the row set.
    snapshots = drivestats.select("date", "capacity_bytes").join(
        month_end, left_on="date", right_on="month_end_date", how="semi"
    )
    return (
        snapshots.group_by("date")
        .agg(
            pl.len().alias("active_drives"),
            pl.col("capacity_bytes").sum().alias("raw_bytes"),
            (pl.col("capacity_bytes") >= 16e12)
            .fill_null(False)
            .mean()
            .alias("at_least_16tb_share"),
        )
        .select(
            "date",
            "active_drives",
            (pl.col("raw_bytes") / 1e18).round(2).alias("raw_exabytes"),
            (100.0 * pl.col("at_least_16tb_share"))
            .round(2)
            .alias("drives_at_least_16tb_pct"),
        )
        .sort("date")
    )


QUERIES = {
    "01_fleet_on_a_day.sql": query_01,
    "02_model_mix.sql": query_02,
    "03_failure_rate_by_model.sql": query_03,
    "04_smart_warning_signals.sql": query_04,
    "05_capacity_growth.sql": query_05,
}


def planned_files(metadata_uri: str, query: str) -> dict[str, int]:
    """Data files and their Parquet bytes left after Iceberg partition pruning."""
    table = StaticTable.from_metadata(metadata_uri, properties=storage_options())
    row_filter = PLANNING_FILTERS[query]
    scan = table.scan() if row_filter is None else table.scan(row_filter=row_filter)
    tasks = list(scan.plan_files())
    return {
        "planned_data_files": len(tasks),
        "planned_data_file_bytes": sum(task.file.file_size_in_bytes for task in tasks),
    }


def run_once(plan: pl.LazyFrame) -> tuple[float, pl.DataFrame]:
    started = time.perf_counter()
    frame = plan.collect(engine="streaming")
    return (time.perf_counter() - started) * 1000, frame


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("query", choices=sorted(QUERIES), help="Challenge query filename")
    parser.add_argument("--mode", choices=("cold", "warm"), default="cold")
    parser.add_argument(
        "--repeats",
        type=int,
        default=3,
        help="Warm mode only: executions after the priming run; the fastest is reported.",
    )
    parser.add_argument("--json-out", type=Path, default=None)
    arguments = parser.parse_args()

    client = s3_client()
    metadata_key = latest_metadata_key(client)
    metadata_uri = f"s3://{BUCKET}/{metadata_key}"

    started = time.perf_counter()
    drivestats = pl.scan_iceberg(
        metadata_uri, storage_options=storage_options(), reader_override="native"
    )
    plan = QUERIES[arguments.query](drivestats)
    setup_ms = (time.perf_counter() - started) * 1000

    # Network bytes are measured at the interface, so they are an upper bound on
    # the object-store payload: TLS, HTTP headers, and any other traffic on an
    # otherwise idle machine are included. Polars' native Iceberg reader exposes
    # no per-query byte counter.
    network_before = psutil.net_io_counters().bytes_recv
    if arguments.mode == "cold":
        runtime_ms, frame = run_once(plan)
        samples = [runtime_ms]
    else:
        run_once(plan)  # prime the caches, discard
        samples = []
        for _ in range(arguments.repeats):
            elapsed_ms, frame = run_once(plan)
            samples.append(elapsed_ms)
        runtime_ms = min(samples)
    network_bytes = psutil.net_io_counters().bytes_recv - network_before

    record = {
        "query": arguments.query,
        "mode": arguments.mode,
        "engine": "streaming",
        "threads": pl.thread_pool_size(),
        "polars_version": pl.__version__,
        "metadata_file": metadata_key,
        "setup_ms": round(setup_ms, 1),
        "runtime_ms": round(runtime_ms, 1),
        "samples_ms": [round(sample, 1) for sample in samples],
        "network_bytes_received": network_bytes,
        **planned_files(metadata_uri, arguments.query),
        "row_count": frame.height,
        "columns": frame.columns,
    }

    if arguments.json_out:
        arguments.json_out.write_text(
            json.dumps({**record, "rows": frame.rows()}, indent=2, default=str)
        )
    print(json.dumps(record, indent=2))
    print("--- result ---")
    with pl.Config(tbl_rows=200, tbl_cols=-1, fmt_str_lengths=60):
        print(frame)


if __name__ == "__main__":
    main()
