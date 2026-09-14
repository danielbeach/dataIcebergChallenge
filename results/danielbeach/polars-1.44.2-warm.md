# Polars 1.44.2 streaming engine on macOS 26.6.2 (warm cache)

**Contributor:** Daniel Beach (@danielbeach)  
**Code repository:** https://github.com/danielbeach/dataIcebergChallenge  
**Run date (UTC):** 2026-09-14  
**Language and version:** Python 3.12.12  
**Tool and version:** Polars 1.44.2, streaming engine (`collect(engine="streaming")`)  
**Leaderboard class:** single_node  
**Cluster shape:** 1 node; 8 vCPU (`POLARS_MAX_THREADS=8` on a 14-core M4 Pro); 24 GiB RAM  
**Compute and network:** Apple M4 Pro, macOS 26.6.2, US Central (America/Chicago) over the public internet to Backblaze B2 `us-west-004`  
**Table state:** `00258-83455019-db09-4def-8eb2-640f5b222dd8.metadata.json`, snapshot `8298869781046488555`, sequence number 231, committed 2026-09-02T16:26:43Z; 627 data files across 159 monthly partitions  
**Cache state:** warm — one discarded priming execution, then the fastest of the repeats, all inside one process

This is the warm companion to my
[cold Polars run](polars-1.44.2-cold.md) on the same snapshot and machine. The
connection approach, runner, and query translations are identical; only the
cache state differs. See the cold report for the
[query translation table](polars-1.44.2-cold.md#query-translation).

## Connection and implementation

- **Iceberg access approach:** `pl.scan_iceberg(..., reader_override="native")`,
  resolving the highest-numbered `*.metadata.json` under `drivestats/metadata/`
  because the table has no catalog and no `version-hint.text`.
- **Exact command:** `uv run results/danielbeach/bench_polars.py <query>.sql --mode warm --repeats 3`,
  with `--repeats 2` for query 04 because each execution takes over four minutes.
- **SQL changes:** translated from DuckDB SQL to the Polars LazyFrame API; see the cold report.
- **Date range read:** 01 and 02: 2024-12-31. 03: 2024-01-01 through 2024-12-31.
  04 and 05: full table history, 2013-04 through 2026-06.

## Results

| Query | Status | Runtime | Bytes/files scanned | Result evidence | Notes |
|---|---|---|---:|---|---|
| `01_fleet_on_a_day.sql` | pass | 0.2513 s | not available / 1 file | 1 row: 2024-12-31, 305,180 active drives, 4.42 raw EB | Samples 324.5 / 357.2 / 251.3 ms |
| `02_model_mix.sql` | pass | 0.2908 s | not available / 1 file | 15 rows; TOSHIBA MG08ACA16TA 40,185 (13.17%) down to TOSHIBA MG08ACA16TE 5,912 (1.94%) | Samples 361.0 / 436.4 / 290.8 ms |
| `03_failure_rate_by_model.sql` | pass | 18.856 s | not available / 12 files | 20 rows; ST12000NM0007 at 11.387% (1,169 drives, 125 failures) down to TOSHIBA MG08ACA16TE at 1.143% | Samples 20388.7 / 18856.2 / 20353.8 ms |
| `04_smart_warning_signals.sql` | pass | 259.52 s | not available / 627 files | 20 rows; WDC WD1600BPVT 16,484.5 avg pending sectors over 119 observations, ST14000NM0138 4,963.5 over 13,765 | Samples 259523.9 / 272388.4 ms |
| `05_capacity_growth.sql` | pass | 40.442 s | not available / 627 files | 159 rows, 2013-04-30 to 2026-06-30; first 21,734 drives / 0.06 EB / 0.0% ≥16 TB, last 355,238 drives / 5.71 EB / 60.18% ≥16 TB | Samples 44304.0 / 40442.1 / 55145.0 ms |

All values are identical to the cold run and to my DuckDB 1.5.5 runs against the
same snapshot.

`bytes_scanned` is reported as null rather than a number. The interface counter
this runner uses spans the whole warm session — priming execution plus repeats —
so it cannot be attributed to the one reported execution. The per-execution
averages it implies are quoted below, because they are the interesting part of
this record.

## What "warm" actually buys Polars

| Query | Cold | Warm | Speedup | Cold bytes | Warm bytes per execution |
|---|---:|---:|---:|---:|---:|
| 01 | 7.3692 s | 0.2513 s | 29x | 7.9 MB | 2.5 MB |
| 02 | 2.9198 s | 0.2908 s | 10x | 8.2 MB | 2.9 MB |
| 03 | 26.245 s | 18.856 s | 1.4x | 1.23 GB | 0.88 GB |
| 04 | 253.65 s | 259.52 s | none | 1.08 GB | 1.10 GB |
| 05 | 54.063 s | 40.442 s | 1.3x | 414 MB | 309 MB |

**The cache boundary sits between queries 02 and 03.** Queries 01 and 02 touch
one small pruned data file, and re-executing them is nearly free: four executions
of query 01 moved 10.1 MB in total against 7.9 MB for a single cold execution.
Everything above that size is re-fetched from B2 on every execution. Query 04 is
the clearest case — 3.30 GB across three executions is 1.10 GB each, matching its
cold 1.08 GB, and its warm runtime of 259.52 s is *slower* than the 253.65 s cold
run, inside run-to-run variance.

**This is the headline difference from DuckDB on the same machine.** DuckDB's
external file cache held all 3.5 GB of query 04's projected column chunks in the
24 GiB limit, so its warm run was 8.09 s — 40x its own cold run. Polars 1.44.2's
native Iceberg reader has no equivalent persistent cache, so warm and cold are
the same query. Polars wins query 04 cold by a wide margin (253.65 s against
325.01 s, on a third of the bytes) and loses it warm by a factor of 32. Which
engine is faster here is entirely a question of whether the workload re-reads the
same bytes.

**The residual 1.3–1.4x gains on queries 03 and 05 are not data caching.** They
come from Iceberg metadata, manifests, and Parquet footers already being resolved
in the process, which removes a round trip per file but not the column chunks
themselves. Query 05's samples span 40.4 s to 55.1 s — a wider spread than the
gain over its cold run — which says the same thing the cold report did: these
whole-history queries are governed by per-file request latency across 627 remote
objects, and that latency is not something a second execution improves.
