# DuckDB 1.5.5 on macOS 26.6.2 — cold runs

**Contributor:** Daniel Beach (@danielbeach)  
**Code repository:** https://github.com/danielbeach/dataIcebergChallenge  
**Run date (UTC):** 2026-09-14  
**Language and version:** Python 3.12.12  
**Tool and version:** DuckDB 1.5.5 (`httpfs` + `iceberg` extensions)  
**Leaderboard class:** single_node  
**Cluster shape:** 1 node; DuckDB pinned to 8 threads and a 24 GiB memory limit  
**Compute and network:** Apple M4 Pro (14 cores present; `SET threads = 8` and `SET memory_limit = '24GB'` hold the run inside the single-node ceiling), macOS 26.6.2, US Central (America/Chicago), public internet to Backblaze B2 `us-west-004`  
**Table state:** snapshot `8298869781046488555`, sequence number 231, committed 2026-09-02T16:26:43Z — 627 data files across 159 monthly partitions, 744,525,690 records  
**Cache state:** cold

## Connection and implementation

- **Iceberg access approach:** DuckDB `iceberg_scan()` directly against `s3://drivestats-iceberg/drivestats` with `unsafe_enable_version_guessing` for metadata discovery. No catalog, no local copy of the table.
- **Exact command:** `uv run python results/danielbeach/bench_duckdb.py <query>.sql --mode cold`
- **SQL changes:** none. The five files in `queries/` were executed verbatim.
- **Date range read:** `01`/`02` read 2024-12-31; `03` reads 2024-01-01 through 2024-12-31; `04` and `05` read the full history, 2013-04 through 2026-06.

### What "cold" means here

Each cold measurement is a **separate OS process**, so DuckDB holds no HTTP
metadata cache, no Iceberg manifest cache, no Parquet footer cache, and an empty
external file cache. Backblaze-side caching is outside my control and unknown.

The reported runtime is **query execution only**. Resolving the Iceberg metadata
and creating the view is a one-time cost paid once per process; it ranged from
4,424 ms to 6,297 ms across these runs and is listed per query in the JSON
`notes`. It is called out separately rather than folded in so that the five
query numbers stay comparable to each other.

## Results

| Query | Status | Runtime | Bytes/files scanned | Result evidence | Notes |
|---|---|---:|---|---|---|
| `01_fleet_on_a_day.sql` | pass | 3.40 s | 5,506,164 B / 1 data file (+26 metadata objects) | 1 row: 2024-12-31, 305,180 drives, 4.42 EB | Single partition |
| `02_model_mix.sql` | pass | 3.05 s | 5,634,845 B / 1 data file | 15 rows; top TOSHIBA MG08ACA16TA, 40,185 drives (13.17%) | Single partition |
| `03_failure_rate_by_model.sql` | pass | 20.49 s | 384,310,099 B / 12 data files | 20 rows; ST12000NM0007 highest at 11.387% AFR | 12 monthly partitions of 2024 |
| `04_smart_warning_signals.sql` | pass | 325.01 s | 3,511,999,629 B / 627 data files | 20 rows; WDC WD1600BPVT highest avg pending sectors at 16,484.5 | Whole history, table scanned twice |
| `05_capacity_growth.sql` | pass | 155.36 s | 173,041,487 B / 627 data files | 159 rows, 2013-04-30 → 2026-06-30; last row 355,238 drives / 5.71 EB / 60.18% ≥ 16 TB | Whole history, two projected columns |

Byte figures are the sum of Parquet bytes and Iceberg metadata bytes; the split
is in each JSON `notes` field. Iceberg metadata is a constant 5,131,094 bytes
across 26 objects (table metadata JSON plus Avro manifest list and manifests)
for every query.

### How the byte and file counts were measured

DuckDB 1.5 registers every remote byte range it fetches in its external file
cache, and ranges evicted under memory pressure remain listed with
`loaded = false`. Summing all rows therefore gives bytes actually read, not just
bytes still resident:

```sql
SELECT SUM(nr_bytes), COUNT(DISTINCT path)
FROM duckdb_external_file_cache()
WHERE path LIKE '%.parquet';
```

`evicted_bytes` was 0 on all five cold runs, so no range was fetched twice and
the totals are exact for this engine's accounting. They exclude TLS and HTTP
header overhead.

## Iceberg observations

**Partition pruning is the whole story for queries 1–3.** The table is
partitioned by a month transform of `date`, materialized as
`data/date_month=YYYY-MM/`. `WHERE date = DATE '2024-12-31'` resolves to the
single `date_month=2024-12` file — 1 of 627 files, 9,373,296 of 744,525,690
records. Query 3's one-year predicate selects exactly 12 files. Query 1 then
reads 375 KB and query 2 reads 504 KB of Parquet from that one file, because
column projection narrows the read further: of the 197 columns in the schema,
query 1 touches `date` and `capacity_bytes`, query 2 touches `date` and `model`.
Predicate plus projection turn a 744-million-row table into a sub-megabyte read.

**Queries 4 and 5 defeat pruning by design, and the cost shape differs.** Both
touch all 627 files, but query 5 reads only 168 MB while query 4 reads 3.5 GB —
query 4 projects `serial_number` plus three SMART columns and scans the table
twice (once for the `failed_drives` CTE, once for the main aggregate), whereas
query 5 projects just `date` and `capacity_bytes`. Query 5's 155 s against
168 MB works out to roughly 9 Mbit/s of effective throughput, so it is bound by
per-file round-trip latency to `us-west-004`, not by bandwidth. Query 4 moves
3.5 GB in 325 s, about 86 Mbit/s, and is genuinely bandwidth-bound.

**Column selection matters more than row selection at this scale.** With 197
columns, a `SELECT *` view over the table is safe only because DuckDB pushes
projection through `iceberg_scan`. The same query written to materialize the CTE
with `d.*` (query 5 does exactly this) still reads only the two columns the
outer `SELECT` needs.

**Practical notes for other contributors:**

- `SET unsafe_enable_version_guessing = true` is required: the table has no
  `version-hint.text`, and hard-coding the metadata filename from the Backblaze
  article breaks as soon as a new snapshot lands. Snapshot 231 was committed
  2026-09-02, so the article's filename is long stale.
- The schema is 197 columns and does evolve. `smart_187_raw` is NULL for whole
  model families, which is why query 4's `avg_reported_uncorrectable_errors`
  column is empty for several rows — that is real missing instrumentation, not a
  query bug.
- `iceberg_metadata()` reports `record_count` per data file but no file size, so
  it cannot be used for a bytes-read metric on its own. The external file cache
  view is the usable source.

Data source: [Backblaze Drive Stats](https://www.backblaze.com/cloud-storage/resources/hard-drive-test-data),
used under Backblaze's published terms.
