# Backblaze Drive Stats Iceberg Challenge

**Can your data engine query a half-billion-row Iceberg table efficiently?**
Choose your language and tool, solve five Drive Stats analytics challenges, and
submit reproducible results to the community leaderboard.

![Backblaze Drive Stats Iceberg Challenge](dec.jpg)

**Sponsored by [Data Engineering Central](https://dataengineeringcentral.substack.com/).**

Build a data-engineering portfolio project from Backblaze's public, read-only
[Drive Stats](https://www.backblaze.com/cloud-storage/resources/hard-drive-test-data)
Iceberg table. Each row is one operational-drive snapshot for one day, including
drive identity, capacity, failure status, and S.M.A.R.T. attributes.

This is deliberately a **bring-your-own-language and bring-your-own-engine**
challenge. The five SQL files in [`queries/`](queries) define the questions,
not the implementation. Use Rust, Python, Java, Scala, Go, JavaScript,
SQL, or another language; use DuckDB, Polars, DataFusion, PyIceberg, Trino,
Spark, Snowflake, or any compatible tool. Reproduce the queries, then improve
them for cost, partition pruning, schema evolution, and reproducibility.

## Choose your challenge track

Submit to one track only. The leaderboard does not compare these tracks because
they have fundamentally different execution resources.

| Track | Use this track when | Maximum resources |
|---|---|---|
| **Single-Node** | Your engine runs on one machine, including local multi-process execution. | 1 node; 8 vCPU; 32 GiB RAM |
| **Distributed** | Your engine distributes the query across a cluster. | 2–4 nodes; each node at most 8 vCPU and 32 GiB RAM |

## Current leaderboard

<!-- leaderboard:start -->
> Results are contributor-reported, not controlled benchmarks. Report links identify the contributor and link their public GitHub code repository, with hardware, network, cache state, table state, and query translation details.


### Single-node engines (max: 8 vCPU / 32 GiB RAM)

#### Fastest cold runs

| Query | Runtime | Contributor | Tool / report | Code |
|---|---:|---|---|---|
| `01_fleet_on_a_day.sql` | — | — | No submitted cold run | — |
| `02_model_mix.sql` | — | — | No submitted cold run | — |
| `03_failure_rate_by_model.sql` | — | — | No submitted cold run | — |
| `04_smart_warning_signals.sql` | — | — | No submitted cold run | — |
| `05_capacity_growth.sql` | — | — | No submitted cold run | — |

#### Fastest warm runs

| Query | Runtime | Contributor | Tool / report | Code |
|---|---:|---|---|---|
| `01_fleet_on_a_day.sql` | — | — | No submitted warm run | — |
| `02_model_mix.sql` | — | — | No submitted warm run | — |
| `03_failure_rate_by_model.sql` | — | — | No submitted warm run | — |
| `04_smart_warning_signals.sql` | — | — | No submitted warm run | — |
| `05_capacity_growth.sql` | — | — | No submitted warm run | — |

#### Lowest reported bytes read

| Query | Bytes read | Contributor | Tool / report | Code |
|---|---:|---|---|---|
| `01_fleet_on_a_day.sql` | — | — | No submitted scan metric | — |
| `02_model_mix.sql` | — | — | No submitted scan metric | — |
| `03_failure_rate_by_model.sql` | — | — | No submitted scan metric | — |
| `04_smart_warning_signals.sql` | — | — | No submitted scan metric | — |
| `05_capacity_growth.sql` | — | — | No submitted scan metric | — |

#### Completed all five queries

No submission has completed all five queries yet.

### Distributed engines (max: 4 nodes; 8 vCPU / 32 GiB RAM each)

#### Fastest cold runs

| Query | Runtime | Contributor | Tool / report | Code |
|---|---:|---|---|---|
| `01_fleet_on_a_day.sql` | — | — | No submitted cold run | — |
| `02_model_mix.sql` | — | — | No submitted cold run | — |
| `03_failure_rate_by_model.sql` | — | — | No submitted cold run | — |
| `04_smart_warning_signals.sql` | — | — | No submitted cold run | — |
| `05_capacity_growth.sql` | — | — | No submitted cold run | — |

#### Fastest warm runs

| Query | Runtime | Contributor | Tool / report | Code |
|---|---:|---|---|---|
| `01_fleet_on_a_day.sql` | — | — | No submitted warm run | — |
| `02_model_mix.sql` | — | — | No submitted warm run | — |
| `03_failure_rate_by_model.sql` | — | — | No submitted warm run | — |
| `04_smart_warning_signals.sql` | — | — | No submitted warm run | — |
| `05_capacity_growth.sql` | — | — | No submitted warm run | — |

#### Lowest reported bytes read

| Query | Bytes read | Contributor | Tool / report | Code |
|---|---:|---|---|---|
| `01_fleet_on_a_day.sql` | — | — | No submitted scan metric | — |
| `02_model_mix.sql` | — | — | No submitted scan metric | — |
| `03_failure_rate_by_model.sql` | — | — | No submitted scan metric | — |
| `04_smart_warning_signals.sql` | — | — | No submitted scan metric | — |
| `05_capacity_growth.sql` | — | — | No submitted scan metric | — |

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

## Included quick start: Python + DuckDB

This runnable path is a convenience, not a requirement. It gives newcomers a
small, reproducible starting point; submissions may use any stack.

1. Install [uv](https://docs.astral.sh/uv/), then run `uv sync`.
2. Copy `.env.example` to `.env`.
3. Populate the first two variables using the **published read-only credentials**
   on Backblaze's Drive Stats page. `.env` is ignored and must not be committed.
4. Run a query:

   ```bash
   uv run drivestats-query 01_fleet_on_a_day.sql
   ```

The command installs DuckDB's `httpfs` and `iceberg` extensions, configures an
S3 secret only in the local process, enables DuckDB's metadata version discovery,
and creates a `drivestats` view. It does not copy the table locally.

## Five challenges

| Query | Theme | Skills exercised |
|---|---|---|
| `01_fleet_on_a_day.sql` | Daily fleet baseline | Date predicates, capacity aggregation |
| `02_model_mix.sql` | Fleet composition | Windows and percentage calculations |
| `03_failure_rate_by_model.sql` | Reliability comparison | Drive-days, distinct failures, annualization |
| `04_smart_warning_signals.sql` | Pre-failure SMART behavior | Self-join, time windows, null handling |
| `05_capacity_growth.sql` | Fleet evolution | Monthly snapshots, scale, capacity mix |

Queries intentionally use a recent historical date where appropriate, rather
than assuming today's partitions are available. Begin with one-month or
one-year predicates before attempting table-wide exploration.

## Use your preferred stack

The table URI, B2 endpoint, region, and published read-only credentials are
the only common connection inputs. The challenge queries are written in
portable analytical SQL, but small dialect adjustments are expected and should
be recorded in your submission.

| Tool | Recommended approach |
|---|---|
| DuckDB | `httpfs` + `iceberg`; see the included Python runner. |
| PyIceberg | Use `pyiceberg` with an S3-compatible `FileIO` to inspect metadata, snapshots, schemas, and manifests. |
| Polars | Use PyIceberg or DuckDB to resolve Iceberg metadata, then scan the selected Parquet files with Polars. |
| Apache DataFusion / Rust | Configure an S3 object store and its Iceberg catalog/table provider; query through DataFusion SQL or the Rust API. |
| Trino | Configure the Iceberg connector and native S3 filesystem, then register the object-store table in a metastore. |
| Spark | Configure `SparkCatalog`/Hadoop S3A for B2 and register the existing table metadata. |
| Java, Scala, Go, JavaScript, or other runtimes | Use an Iceberg-compatible client or connect to a query engine that supports the S3-compatible B2 endpoint. |

The source article includes complete DuckDB, Trino, and Snowflake examples:
[Iceberg on Backblaze B2](https://www.backblaze.com/blog/iceberg-on-backblaze-b2/).
Use the current metadata rather than pinning the article's historical metadata
filename.

## Share your results by pull request

Benchmarking across runtimes is part of the challenge. Fork this repository,
run one or more queries, and open a PR adding one report under
[`results/`](results). Start by copying both
[`results/TEMPLATE.md`](results/TEMPLATE.md) and
[`results/TEMPLATE.json`](results/TEMPLATE.json) to
`results/<your-github-handle>/<tool>-<version>.<md|json>`.

Each report must record one result row for every query it ran: query filename,
success/failure, runtime, result row count or result values, and scan
bytes/files when the tool exposes them. Also include the contributor's display
name and GitHub handle, a public GitHub repository URL containing the runnable
code, language, tool and version, OS/compute details, table snapshot or run
timestamp, date range, command, and any SQL dialect changes. Markdown is for
people; the paired JSON record is the source for the generated leaderboard. The
[pull request template](.github/pull_request_template.md) turns these into a
review checklist.

Results are not a cross-engine performance leaderboard: network location,
object-store caching, hardware, concurrency, and metadata version affect
runtime. Publish enough context for readers to reproduce and interpret the
number rather than comparing a single runtime in isolation.

## Leaderboard

The leaderboard near the top of this README is rebuilt automatically when a
results PR is merged. It separates engines running on one machine from
distributed engines, then lists community-reported leaders for fastest cold
run, fastest warm run, lowest bytes read, and completing all five queries.
Every entry names its contributor and links to the submitted report, so runtime
claims retain their context.

| Class | Maximum resources |
|---|---|
| Single node | 1 node; 8 vCPU; 32 GiB RAM |
| Distributed | 2–4 nodes; each node at most 8 vCPU and 32 GiB RAM |

The submitted record must state actual node count, vCPU per node, and GiB RAM
per node. A multi-process engine operating on one machine is single-node.

Pull-request automation only validates submitted JSON and Markdown; it does not
run submitted code, access the Drive Stats dataset, or expose credentials.
Entries are community-reported. The automation validates the structured JSON
and requires its matching Markdown report; reviewers assess the contextual
claims in the report.

## Submission rules

1. Cite Backblaze as the data source and follow its
   [usage terms](https://www.backblaze.com/cloud-storage/resources/hard-drive-test-data).
2. Never commit credentials, downloaded raw data, or generated access tokens.
3. Document engine version, execution time, scanned bytes/files if available,
   and date range for every result.
4. Include only source code, configuration with secrets removed, and concise
   textual or tabular result evidence; do not commit result data extracts.
5. Stay within the resource ceiling for the selected leaderboard class.
6. Explain how Iceberg metadata and date predicates reduce object-store reads.

## Suggested extensions

- Inspect snapshots and compare a query at two historical table states.
- Validate a schema change across quarterly boundaries.
- Produce a model-level reliability dashboard with confidence thresholds.
- Benchmark equivalent queries in DuckDB, DataFusion, Polars, and Trino.
