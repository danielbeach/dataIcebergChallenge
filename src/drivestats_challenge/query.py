"""Run challenge SQL against the Backblaze Drive Stats Iceberg table."""

from __future__ import annotations

import argparse
import importlib.resources
import os
from pathlib import Path

import duckdb
from dotenv import load_dotenv

TABLE_LOCATION = "s3://drivestats-iceberg/drivestats"
DEFAULT_ENDPOINT = "https://s3.us-west-004.backblazeb2.com"
DEFAULT_REGION = "us-west-004"
QUERY_DIRECTORY = Path(__file__).resolve().parents[2] / "queries"


def required_environment(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(
            f"{name} is not set. Copy .env.example to .env and add the published "
            "read-only Drive Stats credentials."
        )
    return value


def connect() -> duckdb.DuckDBPyConnection:
    """Create a DuckDB connection with the B2 secret and Iceberg view configured."""
    load_dotenv()
    key_id = required_environment("DRIVESTATS_S3_ACCESS_KEY_ID")
    secret = required_environment("DRIVESTATS_S3_SECRET_ACCESS_KEY")
    endpoint = os.getenv("DRIVESTATS_S3_ENDPOINT", DEFAULT_ENDPOINT)
    region = os.getenv("DRIVESTATS_S3_REGION", DEFAULT_REGION)

    connection = duckdb.connect()
    connection.execute("INSTALL httpfs; LOAD httpfs; INSTALL iceberg; LOAD iceberg;")
    connection.execute(
        """
        CREATE SECRET drivestats_b2 (
            TYPE s3,
            KEY_ID ?,
            SECRET ?,
            REGION ?,
            ENDPOINT ?
        )
        """,
        [key_id, secret, region, endpoint.removeprefix("https://")],
    )
    connection.execute("SET unsafe_enable_version_guessing = true")
    connection.execute(
        f"""
        CREATE OR REPLACE VIEW drivestats AS
        SELECT * FROM iceberg_scan(
            '{TABLE_LOCATION}', version = '?', allow_moved_paths = true
        )
        """
    )
    return connection


def query_path(name: str) -> Path | importlib.resources.abc.Traversable:
    """Resolve project queries locally and wheel-bundled queries after installation."""
    path = Path(name)
    if path.is_file():
        return path
    project_query = QUERY_DIRECTORY / name
    if project_query.is_file():
        return project_query
    packaged_query = importlib.resources.files("drivestats_challenge").joinpath(
        "queries", name
    )
    if packaged_query.is_file():
        return packaged_query
    raise FileNotFoundError(name)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "query",
        help="Challenge query filename (for example, 01_fleet_on_a_day.sql) or path",
    )
    args = parser.parse_args()
    try:
        path = query_path(args.query)
    except FileNotFoundError:
        parser.error(f"query file not found: {args.query}")

    with connect() as connection:
        result = connection.execute(path.read_text()).fetchdf()
    print(result.to_string(index=False))


if __name__ == "__main__":
    main()
