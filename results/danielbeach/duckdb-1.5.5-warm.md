# DuckDB 1.5.5 on macOS 26.6.2 — warm runs

**Contributor:** Daniel Beach (@danielbeach)  
**Code repository:** https://github.com/danielbeach/dataIcebergChallenge  
**Run date (UTC):** 2026-09-14  
**Language and version:** Python 3.12.12  
**Tool and version:** DuckDB 1.5.5 (`httpfs` + `iceberg` extensions)  
**Leaderboard class:** single_node  
**Cluster shape:** 1 node; DuckDB pinned to 8 threads and a 24 GiB memory limit  
**Compute and network:** Apple M4 Pro (14 cores present; `SET threads = 8` and `SET memory_limit = '24GB'` hold the run inside the single-node ceiling), macOS 26.6.2, US Central (America/Chicago), public internet to Backblaze B2 `us-west-004`  
**Table state:** snapshot `8298869781046488555`, sequence number 231, committed 2026-09-02T16:26:43Z — 627 data files across 159 monthly partitions, 744,525,690 records  
**Cache state:** warm

Companion to [`duckdb-1.5.5-cold.md`](duckdb-1.5.5-cold.md), same machine, same
table state, same day. Read that report for the Iceberg pruning analysis; this
one covers what caching changes.

## Connection and implementation

- **Iceberg access approach:** DuckDB `iceberg_scan()` directly against `s3://drivestats-iceberg/drivestats` with `unsafe_enable_version_guessing` for metadata discovery.
- **Exact command:** `uv run python scripts/bench_duckdb.py <query>.sql --mode warm --repeats 3` (`--repeats 2` for queries 4 and 5)
- **SQL changes:** none. The five files in `queries/` were executed verbatim.
- **Date range read:** `01`/`02` read 2024-12-31; `03` reads 2024-01-01 through 2024-12-31; `04` and `05` read the full history, 2013-04 through 2026-06.

### What "warm" means here

One process per query: the Iceberg view is created, the query runs once to prime
caches and that run is **discarded**, then the query runs 2–3 more times and the
fastest of those is reported. The caches that matter are DuckDB's in-process
Parquet footer cache and its external file cache, which is enabled by default
(`enable_external_file_cache = true`) and holds fetched column chunks in the
24 GiB buffer pool. Nothing is written to local disk and the table is never
copied.

## Results

| Query | Status | Runtime | Bytes/files scanned | Result evidence | Notes |
|---|---|---:|---|---|---|
| `01_fleet_on_a_day.sql` | pass | 1.83 s | not applicable | 1 row: 2024-12-31, 305,180 drives, 4.42 EB | Samples 1917.9 / 2027.4 / 1827.2 ms |
| `02_model_mix.sql` | pass | 1.94 s | not applicable | 15 rows; top TOSHIBA MG08ACA16TA, 40,185 drives (13.17%) | Samples 1951.2 / 1938.6 / 2172.8 ms |
| `03_failure_rate_by_model.sql` | pass | 2.64 s | not applicable | 20 rows; ST12000NM0007 highest at 11.387% AFR | Samples 2711.0 / 2640.1 / 2796.6 ms |
| `04_smart_warning_signals.sql` | pass | 8.09 s | not applicable | 20 rows; WDC WD1600BPVT highest avg pending sectors at 16,484.5 | Samples 8089.9 / 8085.6 ms |
| `05_capacity_growth.sql` | pass | 4.97 s | not applicable | 159 rows, 2013-04-30 → 2026-06-30; last row 355,238 drives / 5.71 EB / 60.18% ≥ 16 TB | Samples 4969.0 / 5191.1 ms |

Bytes and files are reported as not applicable rather than zero. The column
chunks are served from the in-process external file cache, so the counter would
measure cache hits, not object-store reads. The cold report carries the real
scan metrics.

## Cold versus warm

| Query | Cold | Warm | Speedup | Cold bytes read |
|---|---:|---:|---:|---:|
| `01_fleet_on_a_day.sql` | 3.40 s | 1.83 s | 1.9x | 5.5 MB |
| `02_model_mix.sql` | 3.05 s | 1.94 s | 1.6x | 5.6 MB |
| `03_failure_rate_by_model.sql` | 20.49 s | 2.64 s | 7.8x | 384 MB |
| `04_smart_warning_signals.sql` | 325.01 s | 8.09 s | 40x | 3.51 GB |
| `05_capacity_growth.sql` | 155.36 s | 4.97 s | 31x | 173 MB |

The speedup tracks how much of the runtime was object-store I/O rather than
compute. Queries 1 and 2 already read under a megabyte thanks to partition
pruning, so caching buys little; their floor of roughly 1.8–1.9 s is DuckDB
re-planning the Iceberg scan and re-checking metadata, not data transfer.

Queries 4 and 5 collapse by 40x and 31x, which is the clearest evidence that
their cold cost was network-bound. All 3.5 GB of query 4's projected column
chunks stayed resident in the 24 GiB cache with zero evictions, so the warm run
is a pure local scan of 744 million rows across seven columns in 8.09 s — about
92 million rows per second on 8 threads. That is the engine's real compute
ceiling for this workload; everything above it in the cold numbers is the wire.

Query 5 is the interesting case: it reads only 173 MB cold, yet takes 155 s,
and drops to 4.97 s warm. Bandwidth was never the limit there — 627 sequential
file opens against `us-west-004` were. An engine that issues those requests with
more concurrency, or that runs closer to the bucket, should beat this cold
number by a wide margin without reading a byte less.

## Iceberg observations

See [`duckdb-1.5.5-cold.md`](duckdb-1.5.5-cold.md) for the partition-pruning and
projection analysis. One warm-specific note: the one-time Iceberg metadata
resolution (4.4–6.4 s) is paid per process and is **not** eliminated by warm
caches, because `unsafe_enable_version_guessing` re-probes for the current
metadata file on every fresh connection. A long-lived process that creates the
view once amortizes it; a per-query CLI invocation does not.

Data source: [Backblaze Drive Stats](https://www.backblaze.com/cloud-storage/resources/hard-drive-test-data),
used under Backblaze's published terms.
