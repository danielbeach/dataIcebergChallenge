# Submitted runtime results

Each directory contains a contributor's reproducible runtime report. Reports
are intentionally kept as small Markdown files rather than collected into a
single benchmark table: a result is only meaningful alongside its engine,
hardware, network, cache state, table version, and query translation.

To submit, copy both `TEMPLATE.md` and `TEMPLATE.json` into a directory named
for your GitHub handle, using the same basename:

```text
results/<your-github-handle>/<tool>-<version>.md
results/<your-github-handle>/<tool>-<version>.json
```

For example, `results/octocat/datafusion-45.0.md` and
`results/octocat/datafusion-45.0.json`. The JSON is machine-validated and
generates `LEADERBOARD.md`; the Markdown explains the result to readers. Every
record must identify the contributor by display name and GitHub handle and link
to a public GitHub repository containing the runnable code. Add one row and one
JSON result object for each challenge query. You may submit a partial report,
but mark unrun queries as `not run`; do not omit them.

## Resource classes

Choose exactly one class and record the actual `node_count`, `vcpu_per_node`,
and `ram_gib_per_node` in the JSON record.

| Class | Eligibility |
|---|---|
| `single_node` | Exactly one node, at most 8 vCPU and 32 GiB RAM |
| `distributed` | 2–4 nodes, each at most 8 vCPU and 32 GiB RAM |

The leaderboard rejects records above these limits. A local multi-process
engine still belongs in `single_node` when it uses one machine.

Do not commit downloaded data, query profiles containing credentials, access
keys, or tokens.
