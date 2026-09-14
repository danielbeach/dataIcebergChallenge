# Polars 1.44.2 streaming engine on macOS 26.6.2

**Contributor:** Daniel Beach (@danielbeach)  
**Code repository:** https://github.com/danielbeach/dataIcebergChallenge  
**Run date (UTC):** 2026-09-14  
**Language and version:** Python 3.12.12  
**Tool and version:** Polars 1.44.2, streaming engine (`collect(engine="streaming")`)  
**Leaderboard class:** single_node  
**Cluster shape:** 1 node; 8 vCPU (`POLARS_MAX_THREADS=8` on a 14-core M4 Pro); 24 GiB RAM  
**Compute and network:** Apple M4 Pro, macOS 26.6.2, US Central (America/Chicago) over the public internet to Backblaze B2 `us-west-004`  
**Table state:** `00258-83455019-db09-4def-8eb2-640f5b222dd8.metadata.json`, snapshot `8298869781046488555`, sequence number 231, committed 2026-09-02T16:26:43Z; 627 data files across 159 monthly partitions  
**Cache state:** cold — one fresh process per query, so no Iceberg metadata, manifest, or Parquet footer cache carries over

## Connection and implementation

- **Iceberg access approach:** `pl.scan_iceberg(..., reader_override="native")`. The table
  has no Iceberg catalog and no `version-hint.text`, so the runner lists
  `drivestats/metadata/` and takes the highest-numbered `*.metadata.json`; PyIceberg
  0.12.0 is used only to report how many data files each predicate leaves after
  pruning. The scan itself goes through Polars' native Rust Iceberg reader, not
  PyIceberg, and the table is never copied locally.
- **Exact command:** `uv run results/danielbeach/bench_polars.py <query>.sql --mode cold`
  (the script carries PEP 723 inline dependencies, so no project dependency changes
  are needed; credentials come from a gitignored `.env`)
- **SQL changes:** each query is translated from DuckDB SQL to the Polars LazyFrame
  API — see [Query translation](#query-translation).
- **Date range read:** 01 and 02: 2024-12-31. 03: 2024-01-01 through 2024-12-31.
  04 and 05: full table history, 2013-04 through 2026-06.

## Results

| Query | Status | Runtime | Bytes/files scanned | Result evidence | Notes |
|---|---|---:|---|---|---|
| `01_fleet_on_a_day.sql` | pass | 7.3692 s | 7,930,880 B / 1 file | 1 row: 2024-12-31, 305,180 active drives, 4.42 raw EB | First request of the session; carries DNS and TLS setup |
| `02_model_mix.sql` | pass | 2.9198 s | 8,205,312 B / 1 file | 15 rows; TOSHIBA MG08ACA16TA 40,185 (13.17%) down to TOSHIBA MG08ACA16TE 5,912 (1.94%) | Same pruned file, reading `date` and `model` |
| `03_failure_rate_by_model.sql` | pass | 26.245 s | 1,229,798,400 B / 12 files | 20 rows; ST12000NM0007 at 11.387% (1,169 drives, 125 failures) down to TOSHIBA MG08ACA16TE at 1.143% | `serial_number` dominates the read |
| `04_smart_warning_signals.sql` | pass | 253.65 s | 1,083,113,472 B / 627 files | 20 rows; WDC WD1600BPVT 16,484.5 avg pending sectors over 119 observations, ST14000NM0138 4,963.5 over 13,765 | Whole history, read twice (join build and probe) |
| `05_capacity_growth.sql` | pass | 54.063 s | 414,135,296 B / 627 files | 159 rows, 2013-04-30 to 2026-06-30; first 21,734 drives / 0.06 EB / 0.0% ≥16 TB, last 355,238 drives / 5.71 EB / 60.18% ≥16 TB | Whole history, only `date` and `capacity_bytes` projected |

All five results are value-for-value identical to my
[DuckDB 1.5.5 cold run](duckdb-1.5.5-cold.md) against the same snapshot, which is
the cross-check that the translations below are faithful. The
[warm companion run](polars-1.44.2-warm.md) uses the same runner and snapshot.

### How these numbers were measured

Two measurement differences make this record stricter than my DuckDB one, so
compare with them in mind:

- **Runtime includes Iceberg metadata resolution.** Polars resolves the table
  inside `collect()`, so there is no separable setup phase to report apart from
  execution. My DuckDB record excluded a 4–6 s view-creation cost from every
  runtime; nothing comparable is excluded here.
- **Bytes are measured at the network interface,** as `psutil` `bytes_recv`
  across the query on an otherwise idle machine. Polars' native Iceberg reader
  exposes no per-query byte counter the way `duckdb_external_file_cache()` does.
  Interface bytes include TLS and HTTP framing, so every figure here is an upper
  bound on the object-store payload, not an exact count. The file counts are
  exact — they come from Iceberg scan planning.

## Query translation

Polars SQL does not cover the whole DuckDB dialect used in `queries/`, so every
query runs through the LazyFrame API instead. The translations are one-for-one:

| Query | DuckDB construct | Polars equivalent |
|---|---|---|
| 02 | `SUM(COUNT(*)) OVER ()` | `pl.col("active_drives") / pl.col("active_drives").sum()` after the group-by |
| 03 | `COUNT(DISTINCT CASE WHEN failure = 1 THEN serial_number END)` | `pl.col("serial_number").filter(pl.col("failure") == 1).n_unique()` |
| 04 | `d.date >= f.failure_date - INTERVAL 30 DAY` | `pl.col("failure_date").dt.offset_by("-30d")`, which keeps the `Date` type |
| 04 | `ORDER BY ... DESC NULLS LAST` | `sort(..., descending=True, nulls_last=True)` |
| 05 | `JOIN month_end ON d.date = m.month_end_date` | `join(..., how="semi")` — `month_end_date` is unique per month, so the inner join selects exactly the rows a semi-join keeps |
| 05 | `AVG(CASE WHEN capacity_bytes >= 16e12 THEN 1 ELSE 0 END)` | `(pl.col("capacity_bytes") >= 16e12).fill_null(False).mean()` — the `fill_null` reproduces SQL's `ELSE 0` for a null capacity |
| 01, 05 | `SUM(capacity_bytes::HUGEINT)` | plain `Int64` sum; the largest monthly total is 5.7e18, inside `Int64` range |

## Iceberg observations

**Pruning is what makes queries 01–03 cheap.** The hidden month transform on
`date` means the `2024-12-31` predicate resolves to one data file out of 627, and
the 2024 range resolves to 12. Iceberg planning reports 241,657,332 bytes in that
December file, but the wire cost of query 01 was 7.9 MB: partition pruning picks
the file, and Parquet column-chunk projection picks the few percent of it that
`date` and `capacity_bytes` occupy. Query 03 is the reverse lesson — it prunes to
12 files, yet still pulls 1.23 GB, because `COUNT(DISTINCT serial_number)` needs
every value of a high-cardinality string column.

**Queries 04 and 05 have no date predicate, so pruning cannot help; projection
does.** Both plan all 627 files, 26,196,746,019 bytes of Parquet. Query 05 reads
414 MB of that — two narrow columns — and query 04 reads 1.08 GB across *two*
passes over the whole table, because the `failed_drives` side and the probe side
are separate scans. Query 04's build side is narrower than its probe side
(`serial_number`, `date`, `failure` against six columns), which is why two full
scans still cost less than three times query 05's single one.

**Where the streaming engine pays off.** Query 04 is the interesting case: it
joins the full history against every failed drive's first failure date. The
streaming engine ran it in 253.65 s against 325.01 s for DuckDB on the same
snapshot and machine, and moved 1.08 GB against DuckDB's 3.51 GB, while holding
about 2.2 GB RSS — well inside the 24 GiB ceiling, so nothing spilled. Query 05
shows the same shape more sharply: 54.06 s against 155.36 s. Both are dominated
by per-file request latency across 627 remote objects rather than by bandwidth or
CPU; the machine sat at roughly 25% CPU throughout query 04. An engine that
issues more concurrent range requests, or a client closer to `us-west-004`, would
move these numbers more than any query rewrite.

**Practical note for other Polars contributors.** `POLARS_MAX_THREADS` is read
when the thread pool is built at import time, so it has to be set before
`import polars`, not after. The runner does this so the 8 vCPU ceiling is real
rather than nominal on a 14-core host.
