# Backblaze Drive Stats Iceberg Challenge

**Can your data engine query a half-billion-row Iceberg table efficiently?**
Pick your language and engine, solve five Drive Stats analytics challenges, and
submit reproducible results to the community leaderboard.

![Backblaze Drive Stats Iceberg Challenge](dec.jpg)

**Sponsored by [Data Engineering Central](https://dataengineeringcentral.substack.com/).**

Build a data-engineering portfolio project on Backblaze's public, read-only
[Drive Stats](https://www.backblaze.com/cloud-storage/resources/hard-drive-test-data)
Iceberg table. Each row is one operational-drive snapshot for one day, including
drive identity, capacity, failure status, and S.M.A.R.T. attributes.

This is deliberately a **bring-your-own-language, bring-your-own-engine**
challenge. The five SQL files in [`queries/`](queries) define the questions, not
the implementation. Use Rust, Python, Java, Scala, Go, JavaScript, SQL, or
anything else; use DuckDB, Polars, DataFusion, PyIceberg, Trino, Spark,
Snowflake, or any compatible engine. Reproduce the queries, then improve them
for cost, partition pruning, schema evolution, and reproducibility.

## Contents

- [Choose your track](#choose-your-track)
- [Current leaderboard](#current-leaderboard)
- [Dataset facts](#dataset-facts)
- [Quick start: Python + DuckDB](#quick-start-python--duckdb)
- [The five challenges](#the-five-challenges)
- [Use your preferred stack](#use-your-preferred-stack)
- [Submit your results](#submit-your-results)
- [Submission rules](#submission-rules)
- [Suggested extensions](#suggested-extensions)

## Choose your track

Submit to one track only. The leaderboard does not compare tracks against each
other, because they have fundamentally different execution resources.

| Track | Use this track when | Maximum resources |
|---|---|---|
| **Single-node** | Your engine runs on one machine, including local multi-process execution. | 1 node; 8 vCPU; 32 GiB RAM |
| **Distributed** | Your engine distributes the query across a cluster. | 2–4 nodes; each node at most 8 vCPU and 32 GiB RAM |

Your submitted record must state the actual node count, vCPU per node, and GiB
RAM per node; those specs appear on every leaderboard row. A multi-process
engine on one machine is single-node.

## Current leaderboard

Also published standalone as [`LEADERBOARD.md`](LEADERBOARD.md). Both are
generated from the submitted JSON records — see
[Submit your results](#submit-your-results).

<!-- leaderboard:start -->
> Results are contributor-reported, not controlled benchmarks. Each query lists its top 5 submissions. Each row names the contributor, the hardware they reported, and the public repository holding their code; the linked report adds network, cache state, table state, and query translation details.

### Single-node engines (max: 8 vCPU / 32 GiB RAM)

#### Fastest cold runs

| Query | Rank | Runtime | Contributor | Specs | Tool / report | Code |
|---|---:|---:|---|---|---|---|
| `01_fleet_on_a_day.sql` | 1 | 3.4047 s | Daniel Beach (@danielbeach) | 1 x 8 vCPU / 24 GiB, Apple M4 Pro (14 cores; DuckDB pinned to threads=8, memory_limit=24GB), macOS 26.6.2, US Central (America/Chicago) over the public internet to Backblaze B2 us-west-004 | [DuckDB 1.5.5](results/danielbeach/duckdb-1.5.5-cold.md) | [repository](https://github.com/danielbeach/dataIcebergChallenge) |
| `02_model_mix.sql` | 1 | 3.0511 s | Daniel Beach (@danielbeach) | 1 x 8 vCPU / 24 GiB, Apple M4 Pro (14 cores; DuckDB pinned to threads=8, memory_limit=24GB), macOS 26.6.2, US Central (America/Chicago) over the public internet to Backblaze B2 us-west-004 | [DuckDB 1.5.5](results/danielbeach/duckdb-1.5.5-cold.md) | [repository](https://github.com/danielbeach/dataIcebergChallenge) |
| `03_failure_rate_by_model.sql` | 1 | 20.493 s | Daniel Beach (@danielbeach) | 1 x 8 vCPU / 24 GiB, Apple M4 Pro (14 cores; DuckDB pinned to threads=8, memory_limit=24GB), macOS 26.6.2, US Central (America/Chicago) over the public internet to Backblaze B2 us-west-004 | [DuckDB 1.5.5](results/danielbeach/duckdb-1.5.5-cold.md) | [repository](https://github.com/danielbeach/dataIcebergChallenge) |
| `04_smart_warning_signals.sql` | 1 | 325.012 s | Daniel Beach (@danielbeach) | 1 x 8 vCPU / 24 GiB, Apple M4 Pro (14 cores; DuckDB pinned to threads=8, memory_limit=24GB), macOS 26.6.2, US Central (America/Chicago) over the public internet to Backblaze B2 us-west-004 | [DuckDB 1.5.5](results/danielbeach/duckdb-1.5.5-cold.md) | [repository](https://github.com/danielbeach/dataIcebergChallenge) |
| `05_capacity_growth.sql` | 1 | 155.359 s | Daniel Beach (@danielbeach) | 1 x 8 vCPU / 24 GiB, Apple M4 Pro (14 cores; DuckDB pinned to threads=8, memory_limit=24GB), macOS 26.6.2, US Central (America/Chicago) over the public internet to Backblaze B2 us-west-004 | [DuckDB 1.5.5](results/danielbeach/duckdb-1.5.5-cold.md) | [repository](https://github.com/danielbeach/dataIcebergChallenge) |

#### Fastest warm runs

| Query | Rank | Runtime | Contributor | Specs | Tool / report | Code |
|---|---:|---:|---|---|---|---|
| `01_fleet_on_a_day.sql` | 1 | 1.8272 s | Daniel Beach (@danielbeach) | 1 x 8 vCPU / 24 GiB, Apple M4 Pro (14 cores; DuckDB pinned to threads=8, memory_limit=24GB), macOS 26.6.2, US Central (America/Chicago) over the public internet to Backblaze B2 us-west-004 | [DuckDB 1.5.5](results/danielbeach/duckdb-1.5.5-warm.md) | [repository](https://github.com/danielbeach/dataIcebergChallenge) |
| `02_model_mix.sql` | 1 | 1.9386 s | Daniel Beach (@danielbeach) | 1 x 8 vCPU / 24 GiB, Apple M4 Pro (14 cores; DuckDB pinned to threads=8, memory_limit=24GB), macOS 26.6.2, US Central (America/Chicago) over the public internet to Backblaze B2 us-west-004 | [DuckDB 1.5.5](results/danielbeach/duckdb-1.5.5-warm.md) | [repository](https://github.com/danielbeach/dataIcebergChallenge) |
| `03_failure_rate_by_model.sql` | 1 | 2.6401 s | Daniel Beach (@danielbeach) | 1 x 8 vCPU / 24 GiB, Apple M4 Pro (14 cores; DuckDB pinned to threads=8, memory_limit=24GB), macOS 26.6.2, US Central (America/Chicago) over the public internet to Backblaze B2 us-west-004 | [DuckDB 1.5.5](results/danielbeach/duckdb-1.5.5-warm.md) | [repository](https://github.com/danielbeach/dataIcebergChallenge) |
| `04_smart_warning_signals.sql` | 1 | 8.0856 s | Daniel Beach (@danielbeach) | 1 x 8 vCPU / 24 GiB, Apple M4 Pro (14 cores; DuckDB pinned to threads=8, memory_limit=24GB), macOS 26.6.2, US Central (America/Chicago) over the public internet to Backblaze B2 us-west-004 | [DuckDB 1.5.5](results/danielbeach/duckdb-1.5.5-warm.md) | [repository](https://github.com/danielbeach/dataIcebergChallenge) |
| `05_capacity_growth.sql` | 1 | 4.969 s | Daniel Beach (@danielbeach) | 1 x 8 vCPU / 24 GiB, Apple M4 Pro (14 cores; DuckDB pinned to threads=8, memory_limit=24GB), macOS 26.6.2, US Central (America/Chicago) over the public internet to Backblaze B2 us-west-004 | [DuckDB 1.5.5](results/danielbeach/duckdb-1.5.5-warm.md) | [repository](https://github.com/danielbeach/dataIcebergChallenge) |

#### Lowest reported bytes read

| Query | Rank | Bytes read | Contributor | Specs | Tool / report | Code |
|---|---:|---:|---|---|---|---|
| `01_fleet_on_a_day.sql` | 1 | 5,506,164 | Daniel Beach (@danielbeach) | 1 x 8 vCPU / 24 GiB, Apple M4 Pro (14 cores; DuckDB pinned to threads=8, memory_limit=24GB), macOS 26.6.2, US Central (America/Chicago) over the public internet to Backblaze B2 us-west-004 | [DuckDB 1.5.5](results/danielbeach/duckdb-1.5.5-cold.md) | [repository](https://github.com/danielbeach/dataIcebergChallenge) |
| `02_model_mix.sql` | 1 | 5,634,845 | Daniel Beach (@danielbeach) | 1 x 8 vCPU / 24 GiB, Apple M4 Pro (14 cores; DuckDB pinned to threads=8, memory_limit=24GB), macOS 26.6.2, US Central (America/Chicago) over the public internet to Backblaze B2 us-west-004 | [DuckDB 1.5.5](results/danielbeach/duckdb-1.5.5-cold.md) | [repository](https://github.com/danielbeach/dataIcebergChallenge) |
| `03_failure_rate_by_model.sql` | 1 | 384,310,099 | Daniel Beach (@danielbeach) | 1 x 8 vCPU / 24 GiB, Apple M4 Pro (14 cores; DuckDB pinned to threads=8, memory_limit=24GB), macOS 26.6.2, US Central (America/Chicago) over the public internet to Backblaze B2 us-west-004 | [DuckDB 1.5.5](results/danielbeach/duckdb-1.5.5-cold.md) | [repository](https://github.com/danielbeach/dataIcebergChallenge) |
| `04_smart_warning_signals.sql` | 1 | 3,511,999,629 | Daniel Beach (@danielbeach) | 1 x 8 vCPU / 24 GiB, Apple M4 Pro (14 cores; DuckDB pinned to threads=8, memory_limit=24GB), macOS 26.6.2, US Central (America/Chicago) over the public internet to Backblaze B2 us-west-004 | [DuckDB 1.5.5](results/danielbeach/duckdb-1.5.5-cold.md) | [repository](https://github.com/danielbeach/dataIcebergChallenge) |
| `05_capacity_growth.sql` | 1 | 173,041,487 | Daniel Beach (@danielbeach) | 1 x 8 vCPU / 24 GiB, Apple M4 Pro (14 cores; DuckDB pinned to threads=8, memory_limit=24GB), macOS 26.6.2, US Central (America/Chicago) over the public internet to Backblaze B2 us-west-004 | [DuckDB 1.5.5](results/danielbeach/duckdb-1.5.5-cold.md) | [repository](https://github.com/danielbeach/dataIcebergChallenge) |

#### Completed all five queries

- Daniel Beach (@danielbeach) — 1 x 8 vCPU / 24 GiB, Apple M4 Pro (14 cores; DuckDB pinned to threads=8, memory_limit=24GB), macOS 26.6.2, US Central (America/Chicago) over the public internet to Backblaze B2 us-west-004 — [DuckDB 1.5.5](results/danielbeach/duckdb-1.5.5-cold.md) — [repository](https://github.com/danielbeach/dataIcebergChallenge), cold cache, community-reported
- Daniel Beach (@danielbeach) — 1 x 8 vCPU / 24 GiB, Apple M4 Pro (14 cores; DuckDB pinned to threads=8, memory_limit=24GB), macOS 26.6.2, US Central (America/Chicago) over the public internet to Backblaze B2 us-west-004 — [DuckDB 1.5.5](results/danielbeach/duckdb-1.5.5-warm.md) — [repository](https://github.com/danielbeach/dataIcebergChallenge), warm cache, community-reported

### Distributed engines (max: 4 nodes; 8 vCPU / 32 GiB RAM each)

#### Fastest cold runs

| Query | Rank | Runtime | Contributor | Specs | Tool / report | Code |
|---|---:|---:|---|---|---|---|
| `01_fleet_on_a_day.sql` | — | — | — | — | No submitted cold run | — |
| `02_model_mix.sql` | — | — | — | — | No submitted cold run | — |
| `03_failure_rate_by_model.sql` | — | — | — | — | No submitted cold run | — |
| `04_smart_warning_signals.sql` | — | — | — | — | No submitted cold run | — |
| `05_capacity_growth.sql` | — | — | — | — | No submitted cold run | — |

#### Fastest warm runs

| Query | Rank | Runtime | Contributor | Specs | Tool / report | Code |
|---|---:|---:|---|---|---|---|
| `01_fleet_on_a_day.sql` | — | — | — | — | No submitted warm run | — |
| `02_model_mix.sql` | — | — | — | — | No submitted warm run | — |
| `03_failure_rate_by_model.sql` | — | — | — | — | No submitted warm run | — |
| `04_smart_warning_signals.sql` | — | — | — | — | No submitted warm run | — |
| `05_capacity_growth.sql` | — | — | — | — | No submitted warm run | — |

#### Lowest reported bytes read

| Query | Rank | Bytes read | Contributor | Specs | Tool / report | Code |
|---|---:|---:|---|---|---|---|
| `01_fleet_on_a_day.sql` | — | — | — | — | No submitted scan metric | — |
| `02_model_mix.sql` | — | — | — | — | No submitted scan metric | — |
| `03_failure_rate_by_model.sql` | — | — | — | — | No submitted scan metric | — |
| `04_smart_warning_signals.sql` | — | — | — | — | No submitted scan metric | — |
| `05_capacity_growth.sql` | — | — | — | — | No submitted scan metric | — |

#### Completed all five queries

No submission has completed all five queries yet.
<!-- leaderboard:end -->

## Dataset facts

| Property | Value |
|---|---|
| Table location | `s3://drivestats-iceberg/drivestats` |
| Object store | Backblaze B2 S3-compatible API (`us-west-004`) |
| Layout | Apache Iceberg metadata plus Parquet data files |
| Partitioning | Hidden year/month transforms of `date` |
| Published scale | 564,566,016 drive-day records (May 2025 article) |
| Compression example | December 2024: 3.7 GB CSV → 242 MB Parquet (over 15:1) |

Schema changes can occur quarterly. Do not hard-code a CSV-era schema: inspect
the Iceberg schema before building a production-quality solution.

## Quick start: Python + DuckDB

This runnable path is a convenience, not a requirement. It gives newcomers a
small, reproducible starting point; submissions may use any stack.

1. Install [uv](https://docs.astral.sh/uv/), then run `uv sync`.
2. Copy [`.env.example`](.env.example) to `.env`.
3. Fill in the two credential variables using the **published read-only
   credentials** on Backblaze's Drive Stats page. `.env` is gitignored and must
   not be committed.
4. Run a query:

   ```bash
   uv run drivestats-query 01_fleet_on_a_day.sql
   ```

The command installs DuckDB's `httpfs` and `iceberg` extensions, configures an
S3 secret only in the local process, enables DuckDB's metadata version
discovery, and creates a `drivestats` view. It does not copy the table locally.

## The five challenges

| Query | Theme | Skills exercised |
|---|---|---|
| [`01_fleet_on_a_day.sql`](queries/01_fleet_on_a_day.sql) | Daily fleet baseline | Date predicates, capacity aggregation |
| [`02_model_mix.sql`](queries/02_model_mix.sql) | Fleet composition | Windows and percentage calculations |
| [`03_failure_rate_by_model.sql`](queries/03_failure_rate_by_model.sql) | Reliability comparison | Drive-days, distinct failures, annualization |
| [`04_smart_warning_signals.sql`](queries/04_smart_warning_signals.sql) | Pre-failure SMART behavior | Self-join, time windows, null handling |
| [`05_capacity_growth.sql`](queries/05_capacity_growth.sql) | Fleet evolution | Monthly snapshots, scale, capacity mix |

Queries intentionally use a recent historical date where appropriate, rather
than assuming today's partitions are available. Begin with one-month or
one-year predicates before attempting table-wide exploration.

## Use your preferred stack

The table URI, B2 endpoint, region, and published read-only credentials are the
only common connection inputs. The challenge queries are written in portable
analytical SQL, but small dialect adjustments are expected and must be recorded
in your submission.

| Tool | Recommended approach |
|---|---|
| DuckDB | `httpfs` + `iceberg`; see the included Python runner. |
| PyIceberg | Use `pyiceberg` with an S3-compatible `FileIO` to inspect metadata, snapshots, schemas, and manifests. |
| Polars | Use PyIceberg or DuckDB to resolve Iceberg metadata, then scan the selected Parquet files with Polars. |
| Apache DataFusion / Rust | Configure an S3 object store and its Iceberg catalog/table provider; query through DataFusion SQL or the Rust API. |
| Trino | Configure the Iceberg connector and native S3 filesystem, then register the object-store table in a metastore. |
| Spark | Configure `SparkCatalog`/Hadoop S3A for B2 and register the existing table metadata. |
| Java, Scala, Go, JavaScript, other runtimes | Use an Iceberg-compatible client, or connect to a query engine that supports the S3-compatible B2 endpoint. |

The source article includes complete DuckDB, Trino, and Snowflake examples:
[Iceberg on Backblaze B2](https://www.backblaze.com/blog/iceberg-on-backblaze-b2/).
Use the current metadata rather than pinning the article's historical metadata
filename.

## Submit your results

Benchmarking across runtimes is part of the challenge. Fork this repository, run
one or more queries, and open a PR adding one report under
[`results/`](results). Copy both [`results/TEMPLATE.md`](results/TEMPLATE.md)
and [`results/TEMPLATE.json`](results/TEMPLATE.json) to
`results/<your-github-handle>/<tool>-<version>.<md|json>`.

The JSON is the machine-readable source for the leaderboard; the Markdown
explains the result to readers. Every record must carry:

- **Contributor identity** — display name and GitHub handle.
- **Specs** — `execution_class`, node count, vCPU and RAM per node, plus CPU
  model and general location. These are shown directly on the leaderboard.
- **Code** — a public GitHub repository URL containing the runnable code.
- **Run context** — language, tool and version, table snapshot or run
  timestamp, cache state, date range, exact command, and any SQL dialect
  changes.
- **One result object per query** — filename, `pass`/`fail`/`not_run`, runtime,
  result row count or values, and scanned bytes/files when the tool reports
  them. Partial reports are welcome, but mark unrun queries `not_run` rather
  than omitting them.

**Commit only your two files.** `LEADERBOARD.md` and the leaderboard block in
this README are generated, and
[a workflow](.github/workflows/update-leaderboard.yml) rewrites them after your
PR merges. A PR that also edits them is rejected, because every submission
rewrites the same rows and hand-carried copies collide.

Check your record before opening the PR:

```bash
uv run python scripts/validate_results.py
```

Opening the PR runs that same validation in GitHub Actions
([`.github/workflows/pr-checks.yml`](.github/workflows/pr-checks.yml)),
plus a hygiene scan for committed credentials, data extracts, oversized files,
and edits to another contributor's directory. Validation rejects records that
still hold `TEMPLATE.json` placeholders, a report that is an unedited copy of
`TEMPLATE.md`, a directory name that does not match `github_handle`, and specs
above the resource ceiling for their class. The PR summary shows a preview of
the leaderboard your record produces.

The generator separates single-node from distributed engines, then ranks the top
five submissions per query for fastest cold run, fastest warm run, and lowest
bytes read, followed by everyone who completed all five queries.

Validation checks the structured JSON and requires a matching Markdown report.
It does not run submitted code, access the Drive Stats dataset, or handle
credentials — reviewers assess the contextual claims in the report. Results are
not a controlled cross-engine benchmark: network location, object-store
caching, hardware, concurrency, and metadata version all affect runtime.
Publish enough context for readers to reproduce and interpret the number.

## Submission rules

1. Cite Backblaze as the data source and follow its
   [usage terms](https://www.backblaze.com/cloud-storage/resources/hard-drive-test-data).
2. Never commit credentials, downloaded raw data, or generated access tokens.
3. Document engine version, execution time, scanned bytes/files if available,
   and date range for every result.
4. Include only source code, configuration with secrets removed, and concise
   textual or tabular result evidence; do not commit result data extracts.
5. Stay within the resource ceiling for your chosen track.
6. Explain how Iceberg metadata and date predicates reduce object-store reads.

## Suggested extensions

- Inspect snapshots and compare a query at two historical table states.
- Validate a schema change across quarterly boundaries.
- Produce a model-level reliability dashboard with confidence thresholds.
- Benchmark equivalent queries in DuckDB, DataFusion, Polars, and Trino.
