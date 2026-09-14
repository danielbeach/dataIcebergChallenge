# <tool> <version> on <operating system>

**Contributor:** <display name> (@<github-handle>)  
**Code repository:** https://github.com/<owner>/<repository>  
**Run date (UTC):** YYYY-MM-DD  
**Language and version:** <for example, Rust 1.XX>  
**Tool and version:** <for example, Apache DataFusion X.Y>  
**Leaderboard class:** <single_node or distributed>  
**Cluster shape:** <node count; vCPU and RAM per node>  
**Compute and network:** <CPU model, cloud region or general location>  
**Table state:** <Iceberg snapshot ID, metadata file, or "latest as of run date">  
**Cache state:** <cold, warm, disabled, or unknown>

## Connection and implementation

- **Iceberg access approach:** <native catalog/provider, DuckDB scan, Trino, etc.>
- **Exact command:** <command, with no credentials>
- **SQL changes:** <none, or explain dialect-specific changes while preserving the query>
- **Date range read:** <per query or overall range>

## Results

Use `not run` when a query was not executed. `Bytes/files scanned` and
`Result evidence` may be `not available` only when the tool cannot report
them.

| Query | Status | Runtime | Bytes/files scanned | Result evidence | Notes |
|---|---|---:|---|---|---|
| `01_fleet_on_a_day.sql` | pass | <duration> | <metric> | <row count or values> | |
| `02_model_mix.sql` | pass | <duration> | <metric> | <row count or values> | |
| `03_failure_rate_by_model.sql` | pass | <duration> | <metric> | <row count or values> | |
| `04_smart_warning_signals.sql` | pass | <duration> | <metric> | <row count or values> | |
| `05_capacity_growth.sql` | pass | <duration> | <metric> | <row count or values> | |

## Iceberg observations

Describe the files or partitions selected, metadata operations observed, and
how the query predicate affected reads. Note errors or unexpected behavior
that another contributor should know about.
