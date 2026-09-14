## What is in this pull request

- [ ] A results submission (a new or updated report under `results/<my-github-handle>/`)
- [ ] A change to the challenge itself (queries, scripts, docs)

## Results submission checklist

Delete this section if the pull request is not a submission.

- [ ] Both files exist and share a basename: `results/<my-handle>/<tool>-<version>.json` and `.md`
- [ ] The directory name matches `github_handle` in the JSON
- [ ] Every `<placeholder>` from `TEMPLATE.json` and `TEMPLATE.md` is replaced with a real value
- [ ] `code_repository_url` points at a public GitHub repository holding the runnable code
- [ ] `execution_class`, `node_count`, `vcpu_per_node`, and `ram_gib_per_node` describe the machine I actually used, within the track ceiling
- [ ] All five queries appear in `results`, with unrun ones marked `not_run`
- [ ] `table_state`, `cache_state`, `date_range`, `command`, and `sql_changes` are filled in
- [ ] No credentials, `.env` file, downloaded data, or result extracts are committed
- [ ] This pull request touches only my own `results/` directory — not `LEADERBOARD.md`
      or `README.md`, which are generated and rewritten after merge
- [ ] Validation passes from the repository root:

      uv run python scripts/validate_results.py

## Notes for reviewers

Anything about the run that the report does not already cover — unusual hardware,
network position, engine tuning, or a caveat on a number.
