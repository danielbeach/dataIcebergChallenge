# Community Runtime Leaderboard

> Results are contributor-reported, not controlled benchmarks. Each query lists its top 5 submissions, at most one row per contributor. Each row names the contributor, the hardware they reported, and the public repository holding their code; the linked report adds network, cache state, table state, and query translation details.

## Single-node engines (max: 8 vCPU / 32 GiB RAM)

### Fastest cold runs

| Query | Rank | Runtime | Contributor | Specs | Tool / report | Code |
|---|---:|---:|---|---|---|---|
| `01_fleet_on_a_day.sql` | 1 | 3.4047 s | Daniel Beach (@danielbeach) | 1 x 8 vCPU / 24 GiB, Apple M4 Pro (14 cores; DuckDB pinned to threads=8, memory_limit=24GB), macOS 26.6.2, US Central (America/Chicago) over the public internet to Backblaze B2 us-west-004 | [DuckDB 1.5.5](results/danielbeach/duckdb-1.5.5-cold.md) | [repository](https://github.com/danielbeach/dataIcebergChallenge) |
| `02_model_mix.sql` | 1 | 2.9198 s | Daniel Beach (@danielbeach) | 1 x 8 vCPU / 24 GiB, Apple M4 Pro (14 cores; Polars pinned to POLARS_MAX_THREADS=8), macOS 26.6.2, US Central (America/Chicago) over the public internet to Backblaze B2 us-west-004 | [Polars (streaming engine) 1.44.2](results/danielbeach/polars-1.44.2-cold.md) | [repository](https://github.com/danielbeach/dataIcebergChallenge) |
| `03_failure_rate_by_model.sql` | 1 | 20.493 s | Daniel Beach (@danielbeach) | 1 x 8 vCPU / 24 GiB, Apple M4 Pro (14 cores; DuckDB pinned to threads=8, memory_limit=24GB), macOS 26.6.2, US Central (America/Chicago) over the public internet to Backblaze B2 us-west-004 | [DuckDB 1.5.5](results/danielbeach/duckdb-1.5.5-cold.md) | [repository](https://github.com/danielbeach/dataIcebergChallenge) |
| `04_smart_warning_signals.sql` | 1 | 253.654 s | Daniel Beach (@danielbeach) | 1 x 8 vCPU / 24 GiB, Apple M4 Pro (14 cores; Polars pinned to POLARS_MAX_THREADS=8), macOS 26.6.2, US Central (America/Chicago) over the public internet to Backblaze B2 us-west-004 | [Polars (streaming engine) 1.44.2](results/danielbeach/polars-1.44.2-cold.md) | [repository](https://github.com/danielbeach/dataIcebergChallenge) |
| `05_capacity_growth.sql` | 1 | 54.0632 s | Daniel Beach (@danielbeach) | 1 x 8 vCPU / 24 GiB, Apple M4 Pro (14 cores; Polars pinned to POLARS_MAX_THREADS=8), macOS 26.6.2, US Central (America/Chicago) over the public internet to Backblaze B2 us-west-004 | [Polars (streaming engine) 1.44.2](results/danielbeach/polars-1.44.2-cold.md) | [repository](https://github.com/danielbeach/dataIcebergChallenge) |

### Fastest warm runs

| Query | Rank | Runtime | Contributor | Specs | Tool / report | Code |
|---|---:|---:|---|---|---|---|
| `01_fleet_on_a_day.sql` | 1 | 251.3 ms | Daniel Beach (@danielbeach) | 1 x 8 vCPU / 24 GiB, Apple M4 Pro (14 cores; Polars pinned to POLARS_MAX_THREADS=8), macOS 26.6.2, US Central (America/Chicago) over the public internet to Backblaze B2 us-west-004 | [Polars (streaming engine) 1.44.2](results/danielbeach/polars-1.44.2-warm.md) | [repository](https://github.com/danielbeach/dataIcebergChallenge) |
| `02_model_mix.sql` | 1 | 290.8 ms | Daniel Beach (@danielbeach) | 1 x 8 vCPU / 24 GiB, Apple M4 Pro (14 cores; Polars pinned to POLARS_MAX_THREADS=8), macOS 26.6.2, US Central (America/Chicago) over the public internet to Backblaze B2 us-west-004 | [Polars (streaming engine) 1.44.2](results/danielbeach/polars-1.44.2-warm.md) | [repository](https://github.com/danielbeach/dataIcebergChallenge) |
| `03_failure_rate_by_model.sql` | 1 | 2.6401 s | Daniel Beach (@danielbeach) | 1 x 8 vCPU / 24 GiB, Apple M4 Pro (14 cores; DuckDB pinned to threads=8, memory_limit=24GB), macOS 26.6.2, US Central (America/Chicago) over the public internet to Backblaze B2 us-west-004 | [DuckDB 1.5.5](results/danielbeach/duckdb-1.5.5-warm.md) | [repository](https://github.com/danielbeach/dataIcebergChallenge) |
| `04_smart_warning_signals.sql` | 1 | 8.0856 s | Daniel Beach (@danielbeach) | 1 x 8 vCPU / 24 GiB, Apple M4 Pro (14 cores; DuckDB pinned to threads=8, memory_limit=24GB), macOS 26.6.2, US Central (America/Chicago) over the public internet to Backblaze B2 us-west-004 | [DuckDB 1.5.5](results/danielbeach/duckdb-1.5.5-warm.md) | [repository](https://github.com/danielbeach/dataIcebergChallenge) |
| `05_capacity_growth.sql` | 1 | 4.969 s | Daniel Beach (@danielbeach) | 1 x 8 vCPU / 24 GiB, Apple M4 Pro (14 cores; DuckDB pinned to threads=8, memory_limit=24GB), macOS 26.6.2, US Central (America/Chicago) over the public internet to Backblaze B2 us-west-004 | [DuckDB 1.5.5](results/danielbeach/duckdb-1.5.5-warm.md) | [repository](https://github.com/danielbeach/dataIcebergChallenge) |

### Lowest reported bytes read

| Query | Rank | Bytes read | Contributor | Specs | Tool / report | Code |
|---|---:|---:|---|---|---|---|
| `01_fleet_on_a_day.sql` | 1 | 5,506,164 | Daniel Beach (@danielbeach) | 1 x 8 vCPU / 24 GiB, Apple M4 Pro (14 cores; DuckDB pinned to threads=8, memory_limit=24GB), macOS 26.6.2, US Central (America/Chicago) over the public internet to Backblaze B2 us-west-004 | [DuckDB 1.5.5](results/danielbeach/duckdb-1.5.5-cold.md) | [repository](https://github.com/danielbeach/dataIcebergChallenge) |
| `02_model_mix.sql` | 1 | 5,634,845 | Daniel Beach (@danielbeach) | 1 x 8 vCPU / 24 GiB, Apple M4 Pro (14 cores; DuckDB pinned to threads=8, memory_limit=24GB), macOS 26.6.2, US Central (America/Chicago) over the public internet to Backblaze B2 us-west-004 | [DuckDB 1.5.5](results/danielbeach/duckdb-1.5.5-cold.md) | [repository](https://github.com/danielbeach/dataIcebergChallenge) |
| `03_failure_rate_by_model.sql` | 1 | 384,310,099 | Daniel Beach (@danielbeach) | 1 x 8 vCPU / 24 GiB, Apple M4 Pro (14 cores; DuckDB pinned to threads=8, memory_limit=24GB), macOS 26.6.2, US Central (America/Chicago) over the public internet to Backblaze B2 us-west-004 | [DuckDB 1.5.5](results/danielbeach/duckdb-1.5.5-cold.md) | [repository](https://github.com/danielbeach/dataIcebergChallenge) |
| `04_smart_warning_signals.sql` | 1 | 1,083,113,472 | Daniel Beach (@danielbeach) | 1 x 8 vCPU / 24 GiB, Apple M4 Pro (14 cores; Polars pinned to POLARS_MAX_THREADS=8), macOS 26.6.2, US Central (America/Chicago) over the public internet to Backblaze B2 us-west-004 | [Polars (streaming engine) 1.44.2](results/danielbeach/polars-1.44.2-cold.md) | [repository](https://github.com/danielbeach/dataIcebergChallenge) |
| `05_capacity_growth.sql` | 1 | 173,041,487 | Daniel Beach (@danielbeach) | 1 x 8 vCPU / 24 GiB, Apple M4 Pro (14 cores; DuckDB pinned to threads=8, memory_limit=24GB), macOS 26.6.2, US Central (America/Chicago) over the public internet to Backblaze B2 us-west-004 | [DuckDB 1.5.5](results/danielbeach/duckdb-1.5.5-cold.md) | [repository](https://github.com/danielbeach/dataIcebergChallenge) |

### Completed all five queries

- Daniel Beach (@danielbeach) — 1 x 8 vCPU / 24 GiB, Apple M4 Pro (14 cores; DuckDB pinned to threads=8, memory_limit=24GB), macOS 26.6.2, US Central (America/Chicago) over the public internet to Backblaze B2 us-west-004 — [DuckDB 1.5.5](results/danielbeach/duckdb-1.5.5-cold.md) — [repository](https://github.com/danielbeach/dataIcebergChallenge), cold cache, community-reported
- Daniel Beach (@danielbeach) — 1 x 8 vCPU / 24 GiB, Apple M4 Pro (14 cores; DuckDB pinned to threads=8, memory_limit=24GB), macOS 26.6.2, US Central (America/Chicago) over the public internet to Backblaze B2 us-west-004 — [DuckDB 1.5.5](results/danielbeach/duckdb-1.5.5-warm.md) — [repository](https://github.com/danielbeach/dataIcebergChallenge), warm cache, community-reported
- Daniel Beach (@danielbeach) — 1 x 8 vCPU / 24 GiB, Apple M4 Pro (14 cores; Polars pinned to POLARS_MAX_THREADS=8), macOS 26.6.2, US Central (America/Chicago) over the public internet to Backblaze B2 us-west-004 — [Polars (streaming engine) 1.44.2](results/danielbeach/polars-1.44.2-cold.md) — [repository](https://github.com/danielbeach/dataIcebergChallenge), cold cache, community-reported
- Daniel Beach (@danielbeach) — 1 x 8 vCPU / 24 GiB, Apple M4 Pro (14 cores; Polars pinned to POLARS_MAX_THREADS=8), macOS 26.6.2, US Central (America/Chicago) over the public internet to Backblaze B2 us-west-004 — [Polars (streaming engine) 1.44.2](results/danielbeach/polars-1.44.2-warm.md) — [repository](https://github.com/danielbeach/dataIcebergChallenge), warm cache, community-reported

## Distributed engines (max: 4 nodes; 8 vCPU / 32 GiB RAM each)

### Fastest cold runs

| Query | Rank | Runtime | Contributor | Specs | Tool / report | Code |
|---|---:|---:|---|---|---|---|
| `01_fleet_on_a_day.sql` | — | — | — | — | No submitted cold run | — |
| `02_model_mix.sql` | — | — | — | — | No submitted cold run | — |
| `03_failure_rate_by_model.sql` | — | — | — | — | No submitted cold run | — |
| `04_smart_warning_signals.sql` | — | — | — | — | No submitted cold run | — |
| `05_capacity_growth.sql` | — | — | — | — | No submitted cold run | — |

### Fastest warm runs

| Query | Rank | Runtime | Contributor | Specs | Tool / report | Code |
|---|---:|---:|---|---|---|---|
| `01_fleet_on_a_day.sql` | — | — | — | — | No submitted warm run | — |
| `02_model_mix.sql` | — | — | — | — | No submitted warm run | — |
| `03_failure_rate_by_model.sql` | — | — | — | — | No submitted warm run | — |
| `04_smart_warning_signals.sql` | — | — | — | — | No submitted warm run | — |
| `05_capacity_growth.sql` | — | — | — | — | No submitted warm run | — |

### Lowest reported bytes read

| Query | Rank | Bytes read | Contributor | Specs | Tool / report | Code |
|---|---:|---:|---|---|---|---|
| `01_fleet_on_a_day.sql` | — | — | — | — | No submitted scan metric | — |
| `02_model_mix.sql` | — | — | — | — | No submitted scan metric | — |
| `03_failure_rate_by_model.sql` | — | — | — | — | No submitted scan metric | — |
| `04_smart_warning_signals.sql` | — | — | — | — | No submitted scan metric | — |
| `05_capacity_growth.sql` | — | — | — | — | No submitted scan metric | — |

### Completed all five queries

No submission has completed all five queries yet.
