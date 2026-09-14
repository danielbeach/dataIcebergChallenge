# Submitted runtime results

Each directory holds one contributor's reproducible runtime report. Reports stay
as small Markdown files rather than one collected benchmark table: a result is
only meaningful alongside its engine, hardware, network, cache state, table
version, and query translation.

To submit, copy both `TEMPLATE.md` and `TEMPLATE.json` into a directory named
for your GitHub handle, using the same basename:

```text
results/<your-github-handle>/<tool>-<version>.md
results/<your-github-handle>/<tool>-<version>.json
```

For example, `results/octocat/datafusion-45.0.md` and
`results/octocat/datafusion-45.0.json`.

The JSON is machine-validated and generates the leaderboard; the Markdown
explains the result to readers. Validation rejects a record whose directory name
does not match its `github_handle`, whose fields still hold `TEMPLATE.json`
placeholders such as `<display name>`, or whose report is an unedited copy of
`TEMPLATE.md`. Every record must identify the contributor by
display name and GitHub handle, state its hardware specs, and link a public
GitHub repository containing the runnable code — all three appear as leaderboard
columns. Add one row and one JSON result object for each challenge query. Partial
reports are fine, but mark unrun queries `not_run` rather than omitting them.

Before opening the PR, from the repository root:

```bash
uv run python scripts/validate_results.py
```

Commit only the two files in your own directory. `LEADERBOARD.md` and the
leaderboard block in the top-level `README.md` are generated and rewritten
automatically after your PR merges; a PR that edits them is rejected. The PR
summary previews the leaderboard your record produces.

Each query on the leaderboard ranks its top five submissions, separately for
cold runs, warm runs, and lowest reported bytes read.

## Resource classes

Choose exactly one class and record the actual `node_count`, `vcpu_per_node`,
and `ram_gib_per_node` in the JSON record. `compute_and_network` carries the CPU
model and general location; it is shown next to the node shape on the
leaderboard.

| Class | Eligibility |
|---|---|
| `single_node` | Exactly one node, at most 8 vCPU and 32 GiB RAM |
| `distributed` | 2–4 nodes, each at most 8 vCPU and 32 GiB RAM |

Validation rejects records above these limits. A local multi-process engine still
belongs in `single_node` when it uses one machine.

Do not commit downloaded data, query profiles containing credentials, access
keys, or tokens.
